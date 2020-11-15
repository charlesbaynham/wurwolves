import React, { useEffect, useRef, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';

import {
    selectPlayerName,
    selectPlayerRole,
    selectPlayerSeed,
    selectPlayerStatus,
    selectSelectedPlayer,
    selectPlayerSelectable,
    selectPlayerReady
} from './selectors'

import { getRoleURL } from './RolePicture'

import { selectPlayer, unselectAll } from '../app/store'

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function makePlayerImage(ref, details) {
    var image_url = getRoleURL(details.role, details.status, details.seed)

    return (
        <img ref={ref}
            src={image_url}
            className={`figure-img img-fluid w-100 ${details.selected ? "selected" : ""}`}
            alt={`A ${details.role}`}
        />
    )
}

function Player(props) {
    const player_id = props.player_id
    const name = useSelector(selectPlayerName(player_id));
    const role = useSelector(selectPlayerRole(player_id));
    const seed = useSelector(selectPlayerSeed(player_id));
    const status = useSelector(selectPlayerStatus(player_id));
    const playerReady = useSelector(selectPlayerReady(player_id));

    const selectedPlayer = useSelector(selectSelectedPlayer);
    const playerSelectable = useSelector(selectPlayerSelectable);

    const selected = selectedPlayer === player_id && playerSelectable;

    const dispatch = useDispatch()

    const playerImageDOM = useRef(null);

    const details = {
        role: role,
        seed: seed,
        status: status,
        selected: selected
    }

    const [playerImage, setPlayerImage] = useState(
        makePlayerImage(playerImageDOM, details)
    )

    // Plan:
    // Render image via state
    // On change, trigger useEffect:
    // * create new image
    // * Set old image spinning
    // * Half way through animation, substitute it for newImage. Ensure that same animation starts half-way through on newImage
    // * At end of animation nothing to do: old image is gone and newImage is there

    const detailsRef = useRef(details)

    useEffect(() => {
        // Immediately update selected if it has changed
        if (details.selected !== detailsRef.current.selected) {
            detailsRef.current.selected = details.selected
            setPlayerImage(
                makePlayerImage(playerImageDOM, detailsRef.current)
            )
        }

        // If anything else has changed, animate the change
        if (details.status !== detailsRef.current.status || details.role !== detailsRef.current.role) {
            detailsRef.current = details

            async function animate() {
                playerImageDOM.current.classList.add("spinToFlat")

                await sleep(500)

                setPlayerImage(
                    makePlayerImage(playerImageDOM, detailsRef.current)
                )
                playerImageDOM.current.classList.remove("spinToFlat")
                playerImageDOM.current.classList.add("spinFromFlat")
                await sleep(500)
                playerImageDOM.current.classList.remove("spinFromFlat")
            }
            animate()
        }
    }, [details])

    return (
        <figure className="col-4 col-sm-3 figure player" onClick={
            selected
                ? () => dispatch(unselectAll(player_id))
                : () => dispatch(selectPlayer(player_id))
        }>
            <div className="playerWrapperOuter">
                <div className="playerWrapperInner">
                    {playerImage}
                </div>
            </div>
            {playerReady ? <img src='/images/tick.svg' alt="Ready tick-mark" className='tick' /> : null}
            <figcaption className="figure-caption text-center text-break">{name} {(status === "spectating") ? "(spectating)" : ""}</figcaption>
        </figure>
    )
}


export default Player;
