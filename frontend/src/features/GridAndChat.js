import React from 'react';
import { PlayerGrid } from './Playergrid'
import { Chatbox } from './Chatbox'


function GridAndChat() {
    return (
        <div id="grid-and-chat" class="row">
            <PlayerGrid />
            <Chatbox />
        </div>
    )
}

export default GridAndChat;