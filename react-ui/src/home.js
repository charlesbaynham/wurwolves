import React, { Component } from 'react';
import Button from 'react-bootstrap/Button';


class Home extends Component {
    state = {
        url: ""
    }

    render() {
        return (
            <div className="container limited-width pt-5 bg-light bg-night-dark">
                Welcome to Wurwolves...

                <Button href={this.state.url}>
                    Start a new game
                </Button>
            </div>
        );
    }

    componentDidMount() {
        fetch('/api/get_game')
            .then(res => res.json())
            .then((data) => {
                var newUrl = '/' + data;
                this.setState({ url: newUrl })
            })
            .catch(console.log)
    }
}

export default Home;
