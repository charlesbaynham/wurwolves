/**
 * Game state updater
 * 
 * This is a renderless react component which polls the game state for updates
 * at a regular interval. If it gets any updates from the server, it parses them
 * and updates the local state accordingly. 
 */

import { Component } from 'react';
import { selectAllPlayers, addPlayer, setPlayerName, setPlayerStatus, getPlayerById } from './stateSlices/players'
import { selectMyID } from './stateSlices/myID'
import { connect, useDispatch } from 'react-redux'


class GameUpdater extends Component {

    constructor() {
        super()

        this.intervalId = null
        this.mostRecentID = 0
        this.checkNewData = this.checkNewData.bind(this)
        this.joinGame = this.joinGame.bind(this)
    }

    componentDidMount() {
        this.startPolling()
    }

    componentWillUnmount() {
        this.stopPolling()
    }

    startPolling() {
        this.joinGame()
        this.checkNewData()
        this.intervalId = setInterval(this.checkNewData, 500)
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
                    console.log(`Event: new id = ${event.id}, current most recent = ${this.mostRecentID}`)
                    this.mostRecentID = event.id
                    this.handleEvent(event.details)
                }
            })
    }

    joinGame() {
        const { dispatch } = this.props;

        fetch(`/api/${this.props.game_tag}/join`, { method: 'post' })
            .then(r => r.json())
            .then(data => console.log(data))
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
                const status = eventDetails.payload.status
                const { dispatch } = this.props;

                if (getPlayerById(this.props.players, id)) {
                    console.log(`player ${id} already exists`)
                    dispatch(setPlayerName({ id: id, name: name }))
                    dispatch(setPlayerStatus({ id: id, status: status }))
                }
                else {
                    dispatch(addPlayer({ id: id, name: name, status: status }))
                }
        }
    }

    render() {
        return null
    }
}

function mapStateToProps(state) {
    const players = selectAllPlayers(state);
    const myID = selectMyID(state);
    return { players, myID };
}

export default connect(mapStateToProps)(GameUpdater);

