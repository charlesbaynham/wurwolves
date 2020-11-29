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
import { make_api_url } from '../utils'
import {
    selectAllPlayers,
    selectMyID,
    selectStateHash
} from './selectors'


class GameUpdater extends Component {

    constructor() {
        super()

        this.timeoutID = null
        this.cancelled = false
        this.checkAndReschedule = this.checkAndReschedule.bind(this)
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
        this.checkAndReschedule()
    }

    checkAndReschedule() {
        // console.log(`checkAndReschedule with this.timeoutID = ${this.timeoutID}`)

        const errorCheckRate = 1000
        const successCheckRate = 500

        const successHandler = r => {
            if (!this.cancelled) {
                this.timeoutID = setTimeout(this.checkAndReschedule, (r.ok ? successCheckRate : errorCheckRate))

                if (!r.ok) {
                    console.log("Fetch state failed with error " + r.status);
                    if (r.status === 404) {
                        // 404 means that the game doesn't exist: create it
                        setTimeout(this.joinGame, errorCheckRate);
                    } else {
                        // Unknown error: log it to console
                        console.log(`Unknown error on state fetch:`);
                        console.log(r);
                    }
                    return;
                }

                // Otherwise, process the json and update the state if required
                return r.json().then(new_hash => {
                    if (new_hash !== this.props.state_hash) {
                        this.updateState()
                    }
                })
            }
        }

        const failureHandler = r => {
            if (!this.cancelled) {
                this.timeoutID = setTimeout(this.checkAndReschedule, errorCheckRate)
                console.log(`Remounted updater after error for ${this.props.game_tag} with id ${this.timeoutID} after failure`)
            }
        }

        fetch(
            make_api_url(this.props.game_tag, "state_hash", { known_hash: this.props.state_hash })
        ).then(successHandler, failureHandler)
    }

    stopPolling() {
        console.log(`Unmounting updater for ${this.props.game_tag} with id ${this.timeoutID}`)
        clearTimeout(this.timeoutID)
        this.cancelled = true
    }


    updateState() {
        fetch(make_api_url(this.props.game_tag, "state"))
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
        console.log("Joining game " + this.props.game_tag);
        fetch(make_api_url(this.props.game_tag, "join"), { method: 'post' })
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
