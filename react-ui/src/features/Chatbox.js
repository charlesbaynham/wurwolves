import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import Form from 'react-bootstrap/Form';
import ScrollableFeed from 'react-scrollable-feed'
import { make_api_url } from '../utils'

import {
    selectMessages, selectShowSecretChat
} from './selectors'


function ChatEntry(props) {
    return (<p>{props.msg}</p>)
}


export function Chatbox(props) {

    const chat_messages = useSelector(selectMessages)
    const showSecretChat = useSelector(selectShowSecretChat)

    const [chatMessage, setChatMessage] = useState("");

    const sendChatMessage = (msg) => {
        fetch(
            make_api_url(props.game_tag, "chat", { message: msg }),
            { method: 'post' }
        )
    }

    const secretChat = (
        showSecretChat ?
            <Form className="mt-3" onSubmit={e => {
                e.preventDefault()
                sendChatMessage(chatMessage);
                setChatMessage("");
            }}>
                <Form.Control
                    placeholder="Secret message to team..."
                    onChange={e => setChatMessage(e.target.value)}
                    value={chatMessage}
                />
            </Form>
            :
            null
    )

    return (
        <div className="col-md-5">
            <div className="card card-body d-flex flex-column chat-holder bg-night-black">
                <h5 className="card-title">Events</h5>
                <ScrollableFeed className="chat-box flex-grow-1">
                    {chat_messages.map((m, ind) => m.isStrong
                        ? <strong key={ind}><ChatEntry msg={m.msg} /></strong>
                        : <ChatEntry key={ind} msg={m.msg} />
                    )}
                </ScrollableFeed>
                {secretChat}
            </div>
        </div>
    )
}

export default Chatbox;
