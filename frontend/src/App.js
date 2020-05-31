import React from 'react';

import Controls from './features/controls/controls'
import Footer from './features/footer'
import PlayerGrid from './features/playergrid/playergrid'
import Navbar from './features/navbar'

import 'bootstrap/dist/css/bootstrap.css';
import './App.css';


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
