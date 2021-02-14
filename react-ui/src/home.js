import React, { useState } from 'react';
import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import ReactMarkdown from 'react-markdown';
import Topbar from './features/Topbar'
import NewGameButton from './features/NewGameButton'
import DistributionSetup from './features/DistributionSetup'


function Home(props) {

    const [newGameID, setNewGameID] = useState(null);

    return (
        <div>
            <Topbar />
            <Container id="home-content-box" className="container-sm pt-5 qbg-night-dark">
                <Row><Col><h1 id="home-title">Wurwolves</h1></Col></Row>
                <Row><Col>
                    <ReactMarkdown source={`
Play werewolves online with an automated narrator. If you're not in the same room,
you should probably start a video call.

The game hasn't started yet: you'll need at least 3 players for the game to be playable,
but it's more fun with 6 or more. Press Start to make a new game, or enter
a game id from someone else and click Join.

To learn how to play, select the question mark at the top right of the screen.
                `} />
                </Col></Row>
                <Row><Col>
                    <NewGameButton callback={setNewGameID} />
                </Col></Row>
                <Row className='pt-3'><Col>
                    <DistributionSetup game_tag={newGameID} />
                </Col></Row>
            </Container>
        </div>
    );
}

export default Home;
