import React from 'react';
import { useSelector, useStore } from 'react-redux';

import {
    selectMessages
} from '../features/stateSlices/chatEntries'

function ChatEntry(props) {
    return (<p>{props.msg}</p>)
}

export function Chatbox() {
    const chat_messages = useSelector(selectMessages)

    return (
        <div class="col-md-5">
            <div class="card card-body d-flex flex-column chat-holder bg-night-black">
                <h5 class="card-title">Events / secret chat</h5>
                <div id="chat-box" class="flex-grow-1">
                    {chat_messages.map((m, ind) => m.isStrong 
                        ? <strong key={ind}><ChatEntry msg={m.msg} /></strong>
                        : <ChatEntry key={ind} msg={m.msg} />
                        )}
                </div>
                <div class="mt-3">
                    <input type="text" class="form-control" id="chatInput"
                        placeholder="Secret message to the wolves" />
                </div>
            </div>
        </div>
    )
}

export default Chatbox;