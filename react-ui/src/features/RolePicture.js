import React from 'react';

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
    Prostitute: 0,
    Mason: 1,
}

export function RolePicture(props) {

    if (num_pics[props.role] > 0) {
        const image_details = {
            'img': `/images/characters/${props.role.toLowerCase()}0.svg`,
            'alt': 'Picture of your role'
        }

        return (
            <img className="role_picture" src={image_details.img} alt={image_details.alt} />
        )
    } else {
        return null
    }
}


export default RolePicture;
