import React from 'react';
import { PlayerGrid } from './Playergrid'
import { Chatbox } from './Chatbox'


function GridAndChat(props) {

    return (
        <div id="grid-and-chat" className="row">
            <PlayerGrid />
            <Chatbox game_tag={props.game_tag} />
        </div>
    )
}

export default GridAndChat;
