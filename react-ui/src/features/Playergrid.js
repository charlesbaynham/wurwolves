import React from 'react';
import { useSelector, useStore } from 'react-redux';

import Player from './Player'
import {
    selectAllPlayers
} from './selectors'


export function PlayerGrid() {
    const players = useSelector(selectAllPlayers);

    console.log(useStore().getState())

    return (
        <div className="col-md container">
            <div className="row flex-wrap">
                {players.map(p => <Player key={p.id} player_id={p.id} />)}
            </div>
        </div>
    )
}

export default PlayerGrid;
