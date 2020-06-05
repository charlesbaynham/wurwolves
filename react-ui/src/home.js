import React, { Component } from 'react';
import Button from 'react-bootstrap/Button';


class Home extends Component {
    render() {
        return (
            <div className="container limited-width pt-5 bg-light bg-night-dark">
                Welcome to Wurwolves...

                <Button onClick={this.start_game}>
                    Start a new game
                </Button>
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
