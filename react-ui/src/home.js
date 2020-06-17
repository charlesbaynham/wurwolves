import React, { Component } from 'react';
import Button from 'react-bootstrap/Button';
import Container from 'react-bootstrap/Container';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import ReactMarkdown from 'react-markdown';
import Topbar from './features/Topbar'


class Home extends Component {
    render() {
        return (
            <div>
                <Topbar />
                <Container id="home-content-box" className="container-sm pt-5 bg-light bg-night-dark">
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
                        <Button block size="lg" onClick={this.start_game}>
                            Start a new game
                    </Button>
                    </Col></Row>
                </Container>
            </div>
        );
    }

    start_game() {
        fetch('/api/get_game')
            .then(res => res.json())
            .then((data) => {
                var newUrl = '/' + data;
                console.log("Starting new game at " + newUrl)
                window.location = newUrl;
            })
            .catch(console.log)
    }
}

export default Home;
