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
        'img': '/images/person.svg',
        'alt': 'A spectator'
    }
}

function Player(props) {
    const player_id = props.player_id
    const name = useSelector(selectPlayerName(player_id));
    const status = useSelector(selectPlayerStatus(player_id));
    const selected = useSelector(selectPlayerSelected(player_id));

    return (
        <figure class="col-4 col-sm-3 figure player">
            <img src={IMAGE_LOOKUP[status].img}
                class="figure-img img-fluid w-100"
                alt={IMAGE_LOOKUP[status].alt} />
            <figcaption class="figure-caption text-center">{name}</figcaption>
        </figure>
    )
}



{/* <figure class="col-4 col-sm-3 figure player">
<img src="/images/person-seconded.svg" class="figure-img img-fluid w-100"
    alt="A normal villager" />
<figcaption class="figure-caption text-center">Charles</figcaption>
</figure>
<figure class="col-4 col-sm-3 figure player">
<img src="/images/person-nominated.svg" class="figure-img img-fluid w-100"
    alt="A normal villager" />
<figcaption class="figure-caption text-center">Charles</figcaption>
</figure>
<figure class="col-4 col-sm-3 figure player">
<img src="/images/person-lynched.svg" class="figure-img img-fluid w-100"
    alt="A normal villager" />
<figcaption class="figure-caption text-center">Charles</figcaption>
</figure>
<figure class="col-4 col-sm-3 figure player">
<img src="/images/person.svg" class="figure-img img-fluid w-100" alt="A normal villager" />
<figcaption class="figure-caption text-center">Charles</figcaption>
</figure>
<figure class="col-4 col-sm-3 figure player">
<img src="/images/person-wolfed.svg" class="figure-img img-fluid w-100" alt="A normal villager" />
<figcaption class="figure-caption text-center">Charles</figcaption>
</figure> */}

export default Player;
