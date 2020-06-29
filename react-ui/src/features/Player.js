import React from 'react';
import { useSelector, useDispatch } from 'react-redux';

import {
    selectPlayerName,
    selectPlayerStatus,
    selectSelectedPlayer,
    selectPlayerSelectable
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

function Player(props) {
    const player_id = props.player_id
    const name = useSelector(selectPlayerName(player_id));
    const status = useSelector(selectPlayerStatus(player_id));

    const selectedPlayer = useSelector(selectSelectedPlayer);
    const playerSelectable = useSelector(selectPlayerSelectable);

    const selected = selectedPlayer === player_id && playerSelectable;

    const dispatch = useDispatch()

    return (
        <figure className="col-4 col-sm-3 figure player" onClick={
            selected
                ? () => dispatch(unselectAll(player_id))
                : () => dispatch(selectPlayer(player_id))
        }>
            <img src={IMAGE_LOOKUP[status].img}
                className={`figure-img img-fluid w-100 ${selected ? "selected" : ""}`}
                alt={IMAGE_LOOKUP[status].alt} />
            <figcaption className="figure-caption text-center">{name} {(status === "spectating") ? "(spectating)" : ""}</figcaption>
        </figure>
    )
}


export default Player;
