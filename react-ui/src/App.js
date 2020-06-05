import React from 'react';

import Controls from './features/Controls'
import Footer from './features/Footer'
import GridAndChat from './features/GridAndChat'
import Navbar from './features/Navbar'

import 'bootstrap/dist/css/bootstrap.css';
import './App.css';

import addDemoData from './demoData'
import { useDispatch, useSelector } from 'react-redux';

import {
  selectStage
} from './features/stateSlices/gameStage'

function App() {
  addDemoData(useDispatch());

  const game_stage = useSelector(selectStage)

  return (
    <div className={game_stage}>
      <div id="main" className="min-vh-100 bg-night-black">
        <Navbar />
        <div className="container limited-width pt-5 bg-light bg-night-dark">
          <GridAndChat />
          <h1 className="row col d-md-block d-none">Your role</h1>
          <Controls />
        </div>

        <Footer />
      </div>
    </div>
  );
}

export default App;
