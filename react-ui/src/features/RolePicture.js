import React from 'react';


export function RolePicture(props) {
    const image_details = {
        'img': '/images/characters/acolyte.svg',
        'alt': 'Picture of an acolyte'
    }

    return (
        <img className="role_picture" src={image_details.img} alt={image_details.alt} />
    )
}


export default RolePicture;
