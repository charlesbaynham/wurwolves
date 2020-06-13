import React from 'react';
import { useSelector } from 'react-redux';

import Player from './player/Player'
import {
    selectAllPlayers
} from './selectors'


export function PlayerGrid() {
    const players = useSelector(selectAllPlayers);

    return (
        <div className="col-md container">
            <div className="row flex-wrap">
                {players.map(p => <Player key={p.id} player_id={p.id} />)}
            </div>
        </div>
    )
}

export default PlayerGrid;
