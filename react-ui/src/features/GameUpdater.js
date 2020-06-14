/**
 * Game state updater
 * 
 * This is a renderless react component which polls the game state for updates
 * at a regular interval. If it gets any updates from the server, it parses them
 * and updates the local state accordingly. 
 */

import { Component } from 'react'
import { connect, useDispatch } from 'react-redux'
import { replaceState } from '../app/store'

import {
    selectAllPlayers,
    selectMyID
} from './selectors'


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
        this.joinGame()
        this.checkNewData()
        this.intervalId = setInterval(this.checkNewData, 500)
    }

    stopPolling() {
        clearInterval(this.intervalId)
    }

    checkNewData() {
        // fetch(`/api/${this.props.game_tag}/newest_id`)
        //     .then(r => r.json())
        //     .then(mostRecentID => {
        //         if (mostRecentID > this.mostRecentID) {
        //             this.updateState()
        //         }
        //     })
        this.updateState()
    }

    updateState() {
        var url = new URL(`/api/${this.props.game_tag}/state`, document.baseURI)

        fetch(url)
            .then(r => r.json())
            .then(data => {
                // for (const event of data) {
                //     console.log(`Event: new id = ${event.id}, current most recent = ${this.mostRecentID}`)
                //     this.mostRecentID = event.id
                //     this.handleEvent(event.details)
                // }
                const { dispatch } = this.props;
                dispatch(replaceState(data));
            })
    }

    joinGame() {
        fetch(`/api/${this.props.game_tag}/join`, { method: 'post' })
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

