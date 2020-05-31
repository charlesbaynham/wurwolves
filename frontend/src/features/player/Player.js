import React, { useState } from 'react';


function Player() {
    const [playerStatus, setPlayerStatus] = useState('spectator');

    return (
        <figure class="col-4 col-sm-3 figure player">
            <img src="/images/person.svg" class="figure-img img-fluid w-100" alt="A normal villager" />
            <figcaption class="figure-caption text-center">Charles</figcaption>
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
