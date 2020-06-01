import React from 'react';
import { useSelector, useDispatch } from 'react-redux';

import {
    selectPlayerName,
    selectPlayerStatus,
    selectPlayerSelected
} from '../stateSlices/players'

const IMAGE_LOOKUP = {
    'normal': {
        'img': '/images/person.svg',
        'alt': 'A normal villager?'
    },
    'lynched': {
        'img': '/images/person-lynched.svg',
        'alt': 'A lynched player'
    },
    'nominated': {
        'img': '/images/person-nominated.svg',
        'alt': 'A nominated player'
    },
    'wolfed': {
        'img': '/images/person-wolfed.svg',
        'alt': 'A player killed by a wolf'
    },
    'seconded': {
        'img': '/images/person-seconded.svg',
        'alt': 'A seconded player'
    },
    'spectating': {
        'img': '/images/person-spectating.svg',
        'alt': 'A spectator'
    }
}

function Player(props) {
    const player_id = props.player_id
    const name = useSelector(selectPlayerName(player_id));
    const status = useSelector(selectPlayerStatus(player_id));
    const selected = useSelector(selectPlayerSelected(player_id));

    return (
        <figure className="col-4 col-sm-3 figure player">
            <img src={IMAGE_LOOKUP[status].img}
                className="figure-img img-fluid w-100"
                alt={IMAGE_LOOKUP[status].alt} />
            <figcaption className="figure-caption text-center">{name} {(status == "spectating") ? "(spectating)" : "" }</figcaption>
        </figure>
    )
}



{/* <figure className="col-4 col-sm-3 figure player">
<img src="/images/person-seconded.svg" className="figure-img img-fluid w-100"
    alt="A normal villager" />
<figcaption className="figure-caption text-center">Charles</figcaption>
</figure>
<figure className="col-4 col-sm-3 figure player">
<img src="/images/person-nominated.svg" className="figure-img img-fluid w-100"
    alt="A normal villager" />
<figcaption className="figure-caption text-center">Charles</figcaption>
</figure>
<figure className="col-4 col-sm-3 figure player">
<img src="/images/person-lynched.svg" className="figure-img img-fluid w-100"
    alt="A normal villager" />
<figcaption className="figure-caption text-center">Charles</figcaption>
</figure>
<figure className="col-4 col-sm-3 figure player">
<img src="/images/person.svg" className="figure-img img-fluid w-100" alt="A normal villager" />
<figcaption className="figure-caption text-center">Charles</figcaption>
</figure>
<figure className="col-4 col-sm-3 figure player">
<img src="/images/person-wolfed.svg" className="figure-img img-fluid w-100" alt="A normal villager" />
<figcaption className="figure-caption text-center">Charles</figcaption>
</figure> */}

export default Player;
