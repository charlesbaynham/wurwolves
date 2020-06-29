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

        this.timeoutID = null
        this.checkAndReschedule = this.checkAndReschedule.bind(this)
    }

    componentDidMount() {
        this.startPolling()
    }

    componentWillUnmount() {
        this.stopPolling()
    }

    startPolling() {
        this.joinGame()
        this.checkAndReschedule()
    }

    checkAndReschedule() {
        const errorCheckRate = 1000
        const successCheckRate = 500

        const successHandler = r => {
            this.timeoutID = setTimeout(this.checkAndReschedule, successCheckRate)

            if (!r.ok) {
                throw Error("Fetch state failed with error " + r.status)
            }

            return r.json().then(new_hash => {
                if (new_hash !== this.props.state_hash) {
                    this.updateState()
                }
            })
        }

        const failureHandler = r => {
            this.timeoutID = setTimeout(this.checkAndReschedule, errorCheckRate)
        }

        var url = new URL(`/api/${this.props.game_tag}/state_hash`, document.baseURI),
            params = { known_hash: this.props.state_hash }
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))

        fetch(url).then(successHandler, failureHandler)
    }

    stopPolling() {
        clearInterval(this.intervalId)
    }


    updateState() {
        const url = new URL(`/api/${this.props.game_tag}/state`, document.baseURI)

        fetch(url)
            .then(r => {
                if (!r.ok) {
                    throw Error("Fetch state failed with error " + r.status)
                }
                return r.json()
            })
            .then(data => {
                if (data) {
                    const { dispatch } = this.props;
                    dispatch(replaceState(data));
                }
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

