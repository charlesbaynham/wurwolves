/**
 * Game state updater
 * 
 * This is a renderless react component which polls the game state for updates
 * at a regular interval. If it gets any updates from the server, it parses them
 * and updates the local state accordingly. 
 */

import { Component } from 'react'
import { connect } from 'react-redux'
import { replaceState } from '../app/store'

import {
    selectAllPlayers,
    selectMyID,
    selectStateHash
} from './selectors'


class GameUpdater extends Component {

    constructor() {
        super()

        this.intervalId = null
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
        fetch(`/api/${this.props.game_tag}/state_hash`)
            .then(r => r.json())
            .then(new_hash => {
                if (new_hash !== this.props.state_hash) {
                    this.updateState()
                }
            })
    }

    updateState() {
        const url = new URL(`/api/${this.props.game_tag}/state`, document.baseURI)

        fetch(url)
            .then(r => r.json())
            .then(data => {
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
    const state_hash = selectStateHash(state);
    return { players, myID, state_hash };
}

export default connect(mapStateToProps)(GameUpdater);

