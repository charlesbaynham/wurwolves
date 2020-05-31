import React from 'react';


function PlayerGrid() {
    return (
        <div id="player-grid" class="row">
            <div class="col-md container">
                <div class="row flex-wrap">
                    <figure class="col-4 col-sm-3 figure player">
                        <img src="/images/person.svg" class="figure-img img-fluid w-100" alt="A normal villager" />
                        <figcaption class="figure-caption text-center">Charles</figcaption>
                    </figure>
                    <figure class="col-4 col-sm-3 figure player">
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
                    </figure>
                </div>
            </div>
            <div class="col-md-5">
                <div class="card card-body d-flex flex-column chat-holder bg-night-black">
                    <h5 class="card-title">Events / secret chat</h5>
                    <div id="chat-box" class="flex-grow-1">
                        <p>4 votes for Gaby (Charles, James, Parav, Harry)</p>
                        <p>3 votes for Euan (Rosie, Rachel, Gaby)</p>
                        <p><strong>Gaby was voted off</strong></p>
                        <p><strong>Sophie was killed in the night</strong></p>
                        <p>Rob was nominated by Charles</p>
                        <p>James was nominated by Charles</p>
                        <p>James was seconded by Parav</p>
                        <p>4 votes for Gaby (Charles, James, Parav, Harry)</p>
                        <p>3 votes for Euan (Rosie, Rachel, Gaby)</p>
                        <p><strong>Gaby was voted off</strong></p>
                        <p><strong>Sophie was killed in the night</strong></p>
                        <p>Rob was nominated by Charles</p>
                        <p>James was nominated by Charles</p>
                        <p>James was seconded by Parav</p>
                        <p>4 votes for Gaby (Charles, James, Parav, Harry)</p>
                        <p>3 votes for Euan (Rosie, Rachel, Gaby)</p>
                        <p><strong>Gaby was voted off</strong></p>
                        <p><strong>Sophie was killed in the night</strong></p>
                        <p>Rob was nominated by Charles</p>
                        <p>James was nominated by Charles</p>
                        <p>James was seconded by Parav</p>
                    </div>
                    <div class="mt-3">
                        <input type="text" class="form-control" id="chatInput"
                            placeholder="Secret message to the wolves" />
                    </div>
                </div>
            </div>
        </div>
    )
}

export default PlayerGrid;
