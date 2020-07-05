import React, { useEffect, useRef, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';

import {
    selectPlayerName,
    selectPlayerStatus,
    selectSelectedPlayer,
    selectPlayerSelectable,
    selectPlayerReady
} from './selectors'

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


function makePlayerImage(ref, status, selected) {
    return (
        <img ref={ref}
            src={IMAGE_LOOKUP[status].img}
            className={`figure-img img-fluid w-100 ${selected ? "selected" : ""}`}
            alt={IMAGE_LOOKUP[status].alt}
        />
    )
}

function Player(props) {
    const player_id = props.player_id
    const name = useSelector(selectPlayerName(player_id));
    const status = useSelector(selectPlayerStatus(player_id));
    const playerReady = useSelector(selectPlayerReady(player_id));

    const selectedPlayer = useSelector(selectSelectedPlayer);
    const playerSelectable = useSelector(selectPlayerSelectable);

    const selected = selectedPlayer === player_id && playerSelectable;

    const dispatch = useDispatch()

    const playerImageDOM = useRef(null);

    const [playerImage, setPlayerImage] = useState(
        makePlayerImage(playerImageDOM, status, selected)
    )

    // Plan:
    // Render image via state
    // On change, trigger useEffect:
    // * create new image
    // * Set old image spinning
    // * Half way through animation, substitute it for newImage. Ensure that same animation starts half-way through on newImage
    // * At end of animation nothing to do: old image is gone and newImage is there

    const oldStatusRef = useRef(status)
    const oldSelectedRef = useRef(selected)

    useEffect(() => {
        // Immediately update selected if it has changed
        if (selected !== oldSelectedRef.current) {
            oldSelectedRef.current = selected
            setPlayerImage(
                makePlayerImage(playerImageDOM, oldStatusRef.current, selected)
            )
        }

        // If status has changed, animate the change
        if (status !== oldStatusRef.current) {
            oldStatusRef.current = selected
            console.log(`Player ${name} rendered with new status ${status} (used to be ${oldStatusRef.current})`)
            console.log("Need to change the status next")
        }
    }, [status, selected])

    return (
        <figure className="col-4 col-sm-3 figure player" onClick={
            selected
                ? () => dispatch(unselectAll(player_id))
                : () => dispatch(selectPlayer(player_id))
        }>
            <div>
                {playerImage}
            </div>
            {playerReady ? <img src='/images/tick.svg' alt="Ready tick-mark" className='tick' /> : null}
            <figcaption className="figure-caption text-center">{name} {(status === "spectating") ? "(spectating)" : ""}</figcaption>
        </figure>
    )
}


export default Player;
