import React from 'react';
import Container from 'react-bootstrap/Container';

import Controls from './features/Controls'
import GridAndChat from './features/GridAndChat'

function Game() {
    return (
        <Container id="content-box" className="container pt-5 bg-light bg-night-dark">
            <GridAndChat />
            <h1 className="row col d-md-block d-none">Your role</h1>
            <Controls />
        </Container>
    );
}

export default Game;
