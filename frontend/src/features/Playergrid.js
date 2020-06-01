import React from 'react';
import { useSelector, useDispatch } from 'react-redux';

import Player from './player/Player'
import {
    selectAllPlayers
} from './stateSlices/players'


export function PlayerGrid() {
    const players = useSelector(selectAllPlayers);

    var player_ids = Object.keys(players)

    return (
        <div className="col-md container">
            <div className="row flex-wrap">
                {player_ids.map(id => <Player key={id} player_id={id} />)}
            </div>
        </div>
    )
}

export default PlayerGrid;
