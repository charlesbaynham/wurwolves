import React, { useState, useEffect } from 'react';
import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import ReactMarkdown from 'react-markdown';
import Topbar from './features/Topbar'
import {
    Link
} from 'react-router-dom'


function Home(props) {

    const [newGameURL, setNewGameURL] = useState('')

    useEffect(() => {
        if (newGameURL === "") {
            fetch('/api/get_game')
                .then(res => res.json())
                .then((data) => {
                    var newUrl = '/' + data;
                    console.log("Setting new location to " + newUrl)
                    setNewGameURL(newUrl)
                })
                .catch(console.log)
        }
    })

    return (
        <div>
            <Topbar />
            <Container id="home-content-box" className="container-sm pt-5 qbg-night-dark">
                <Row><Col><h1 id="home-title">Wurwolves</h1></Col></Row>
                <Row><Col>
                    <ReactMarkdown source={`
Play werewolves online with an automated narrator. If you're not in the same room,
you should probably start a video call.

The game hasn't started yet: you'll need at least 5 players for the game to be playable,
but it's more fun with 7 or more. Press the "Start a new game" button
and then share the link with your friends.
                `} />
                </Col></Row>
                <Row><Col>
                    <Link to={newGameURL}>
                        <Button block size="lg">
                            Start a new game
                        </Button>
                    </Link>
                </Col></Row>
            </Container>
        </div>
    );

}

export default Home;
