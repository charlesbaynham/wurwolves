import React from 'react';
import { useSelector } from 'react-redux';

import {
    selectMessages
} from '../features/stateSlices/chatEntries'

function ChatEntry(props) {
    return (<p>{props.msg}</p>)
}

export function Chatbox() {
    const chat_messages = useSelector(selectMessages)

    return (
        <div className="col-md-5">
            <div className="card card-body d-flex flex-column chat-holder bg-night-black">
                <h5 className="card-title">Events / secret chat</h5>
                <div id="chat-box" className="flex-grow-1">
                    {chat_messages.map((m, ind) => m.isStrong 
                        ? <strong key={ind}><ChatEntry msg={m.msg} /></strong>
                        : <ChatEntry key={ind} msg={m.msg} />
                        )}
                </div>
                <div className="mt-3">
                    <input type="text" className="form-control" id="chatInput"
                        placeholder="Secret message to the wolves" />
                </div>
            </div>
        </div>
    )
}

export default Chatbox;