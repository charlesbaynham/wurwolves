import React from 'react';

import Controls from './features/Controls'
import GridAndChat from './features/GridAndChat'

function Game() {
    return (
        <div className="container limited-width pt-5 bg-light bg-night-dark">
            <GridAndChat />
            <h1 className="row col d-md-block d-none">Your role</h1>
            <Controls />
        </div>
    );
}

export default Game;
