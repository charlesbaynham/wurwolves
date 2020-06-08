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
                <Container id="content-box" className="pt-5 bg-light bg-night-dark">
                    <Row><Col><h1>Welcome to Wurwolves...</h1></Col></Row>
                    <Row>
                        <Col md>
                            <ReactMarkdown source={`
This is where I should write a bit of a description of this site, maybe some instructions. 

Probably some other stuff too. 
                    `} />
                        </Col>
                        <Col md>
                            <Button block onClick={this.start_game}>
                                Start a new game
                    </Button>
                        </Col>
                    </Row>
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
