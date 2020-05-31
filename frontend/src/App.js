import React from 'react';

import Controls from './features/controls/Controls'
import Footer from './features/Footer'
import GridAndChat from './features/GridAndChat'
import Navbar from './features/Navbar'

import 'bootstrap/dist/css/bootstrap.css';
import './App.css';


import {
   addPlayer
} from './features/stateSlices/players'
import { useDispatch } from 'react-redux';


function App() {
  const dispatch = useDispatch();

  dispatch(addPlayer({
    id: "123",
    name: "Hello world",
    status: "normal"
  }))
  dispatch(addPlayer({
    id: "321",
    name: "Next one",
    status: "wolfed"
  }))

  return (
    <div class="bg-night-black">
      <Navbar />
      <div class="container limited-width pt-5 bg-light bg-night-dark">
        <GridAndChat />
        <h1 class="row col d-md-block d-none">Your role</h1>
        <Controls />
      </div>

      <Footer />
    </div>
  );
}

export default App;
