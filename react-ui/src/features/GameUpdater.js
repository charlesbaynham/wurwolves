/**
 * Game state updater
 * 
 * This is a renderless react component which polls the game state for updates
 * at a regular interval. If it gets any updates from the server, it parses them
 * and updates the local state accordingly. 
 */

import { Component } from 'react';
import { selectAllPlayers, addPlayer } from './stateSlices/players'
import { connect, useDispatch } from 'react-redux'


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
                    console.log(`New id = ${event.id}, current most recent = ${this.mostRecentID}`)
                    this.mostRecentID = event.id
                    this.handleEvent(event.details)
                }
            })
    }

    handleEvent(eventDetails) {
        /** Handle a UI event from the server
         *
         * Parse an event from the server and update the local state accordingly
         */

        switch (eventDetails.type) {
            case "UPDATE_PLAYER":
                const id = eventDetails.payload.id
                const name = eventDetails.payload.name
                console.log(`Making new player ${id} = ${name}. Current players:`)
                console.log(this.props.players)
                // if (this.props.players.some(p => p.id)) {
                //     console.log("player already exists")
                // }
                // else {
                //     const { dispatch } = this.props;    
                //     dispatch(addPlayer({ id: id, name: name, status: "spectating" }))
                // }
                const { dispatch } = this.props;
                dispatch(addPlayer({ id: id, name: name, status: "spectating" }))
        }
    }

    render() {
        return null
    }
}

function mapStateToProps(state) {
    const players = selectAllPlayers(state);
    return { players };
}

export default connect(mapStateToProps)(GameUpdater);

