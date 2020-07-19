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

const IMAGE_LOOKUP = {
    'ALIVE': {
        'img': '/images/person.svg',
        'alt': 'A normal villager?'
    },
    'LYNCHED': {
        'img': '/images/person-lynched.svg',
        'alt': 'A lynched player'
    },
    'NOMINATED': {
        'img': '/images/person-nominated.svg',
        'alt': 'A nominated player'
    },
    'WOLFED': {
        'img': '/images/person-wolfed.svg',
        'alt': 'A player killed by a wolf'
    },
    'SECONDED': {
        'img': '/images/person-seconded.svg',
        'alt': 'A seconded player'
    },
    'SHOT': {
        'img': '/images/person-shot.svg',
        'alt': 'A player who has been shot'
    },
    'SPECTATING': {
        'img': '/images/person-spectating.svg',
        'alt': 'A spectator'
    },
    'MAYOR': {
        'img': '/images/person-mayor.svg',
        'alt': 'The mayor'
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function makePlayerImage(ref, details) {
    // Until I've got a way of modifying images by status, only show the images if the player is alive
    var image_url;
    if (details.status === 'ALIVE') {
        image_url = getRoleURL(details.role, details.seed)
    } else {
        if (!(details.status in IMAGE_LOOKUP)) {
            console.log("Error: details are")
            console.log(details)
            image_url = IMAGE_LOOKUP['SPECTATING'].img
        } else {
            image_url = IMAGE_LOOKUP[details.status].img
        }
    }
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
        if (selected !== detailsRef.current.selected) {
            detailsRef.current.selected = selected
            setPlayerImage(
                makePlayerImage(playerImageDOM, detailsRef.current)
            )
        }

        // If anything else has changed, animate the change
        if (status !== detailsRef.current.status || role !== detailsRef.current.role) {
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
    }, [status, selected])

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
            <figcaption className="figure-caption text-center">{name} {(status === "spectating") ? "(spectating)" : ""}</figcaption>
        </figure>
    )
}


export default Player;
