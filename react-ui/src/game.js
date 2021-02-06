import React from 'react';
import Container from 'react-bootstrap/Container';

import Controls from './features/Controls'
import GameUpdater from './features/GameUpdater'
import GridAndChat from './features/GridAndChat'
import Topbar from './features/Topbar'
import AllOverlays from './features/overlays/AllOverlays'

function Game(props) {
    const game_tag = props.match.params.game_tag
    return (
        <div>
            <Topbar game_tag={game_tag} />
            <Container id="content-box" className="container pt-5 bg-night-dark">
                <GameUpdater game_tag={game_tag} />
                <GridAndChat game_tag={game_tag} />
                <h1 className="row col d-md-block d-none">Your role</h1>
                <Controls game_tag={game_tag} />
                <AllOverlays/>
            </Container>
        </div>
    );
}

export default Game;
