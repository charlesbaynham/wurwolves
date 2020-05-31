import React from 'react';

import 'bootstrap/dist/css/bootstrap.css';
import './App.css';

function Navbar() {
  return (
    <nav class="navbar navbar-expand-lg navbar-light bg-secondary bg-night-black">
      <a class="navbar-brand" href="#">Wurwolves</a>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent"
        aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
    </nav>
  )
}

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

function Controls() {
  return (
    <div class="row pt-4 pt-md-0 d-flex  flex-row-reverse align-items-center">
      <div class="col-md">
        <button type="button" class="btn btn-secondary btn-block btn-lg"><em>Select someone to
                        lynch...</em></button>
      </div>
      <div class="col-md pt-4 pt-md-0">
        <h5>You are a Seer</h5>
        <p>You win the game if the villagers lynch all the wolves. During the night, you may check the identity
                    of one person and discover if they are a wolf. </p>
      </div>
    </div>
  )
}

function Footer() {
  return (
    <div class="text-muted footer d-flex flex-row-reverse px-5 bg-light bg-night-black">
      <p>Baynham Design</p>
    </div>
  )
}

function App() {
  return (
    <div class="bg-night-black">
      <Navbar />
      <div class="container limited-width pt-5 bg-light bg-night-dark">
        <PlayerGrid />
        <h1 class="row col d-md-block d-none">Your role</h1>
        <Controls />
      </div>

      <Footer />
    </div>
  );
}

export default App;
