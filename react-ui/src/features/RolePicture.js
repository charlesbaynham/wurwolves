import React from 'react';

import styles from './RolePicture.module.css'

const num_pics = {
    Villager: 11,
    Wolf: 7,
    Seer: 1,
    Medic: 1,
    Jester: 1,
    Spectator: 0,
    Narrator: 0,
    Vigilante: 1,
    Mayor: 1,
    Miller: 1,
    Acolyte: 1,
    Priest: 1,
    Prostitute: 1,
    Mason: 1,
    Exorcist: 1,
    Fool: 1,
}

export function getRoleURL(role, state, seed) {
    const pic_num = Math.floor(seed * num_pics[role])

    if (role.toLowerCase() === "spectator") {
        return `/images/spectator.svg`
    }

    const state_strs = {
        "alive": "",
        "lynched": "knot",
        "shot": "shot",
        "wolfed": "claw"
    }
    const state_str = state_strs[state.toLowerCase()]

    return `/images/characters/${role.toLowerCase()}${pic_num}${state_str}.svg`
}

export function RolePicture(props) {

    if (num_pics[props.role] > 0) {

        const pic_url = getRoleURL(props.role, props.status, props.seed)

        return (
            <img className={styles.role_picture} src={pic_url} alt={`Role ${props.role}`} />
        )
    } else {
        return null
    }
}


export default RolePicture;
