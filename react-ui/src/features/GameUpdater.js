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
        this.mostRecentID = 0
        this.checkNewData = this.checkNewData.bind(this)
    }

    componentDidMount() {
        this.startPolling()
    }

    componentWillUnmount() {
        this.stopPolling()
    }

    startPolling() {
        this.intervalId = setInterval(this.checkNewData, 1000)
    }

    stopPolling() {
        clearInterval(this.intervalId)
    }

    checkNewData() {
        fetch(`/api/${this.props.game_tag}/newest_id`)
            .then(r => r.json())
            .then(mostRecentID => {
                if (mostRecentID > this.mostRecentID) {
                    this.updateState()
                }
            })
    }

    updateState() {
        var url = new URL(`/api/${this.props.game_tag}/ui_events`, document.baseURI),
            params = { since: this.mostRecentID }
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))

        fetch(url)
            .then(r => r.json())
            .then(data => {
                for (const event of data) {
                    this.mostRecentID = event.id
                    console.log(event.details)
                }
            })
    }

    render() {
        return null
    }
}

export default GameUpdater;
