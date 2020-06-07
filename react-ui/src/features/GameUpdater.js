/**
 * Game state updater
 * 
 * This is a renderless react component which polls the game state for updates
 * at a regular interval. If it gets any updates from the server, it parses them
 * and updates the local state accordingly. 
 */

import { Component } from 'react';


class GameUpdater extends Component {

    constructor() {
        super()

        this.intervalId = null
        this.updateState = this.updateState.bind(this)
    }

    componentDidMount() {
        this.startPolling()
    }

    componentWillUnmount() {
        this.stopPolling()
    }

    startPolling() {
        this.intervalId = setInterval(this.updateState, 1000)
    }

    stopPolling() {
        clearInterval(this.intervalId)
    }

    updateState() {
        console.log(`Fetching ${this.props.game_tag}...`)
    }

    render() {
        return null
    }
}

export default GameUpdater;
