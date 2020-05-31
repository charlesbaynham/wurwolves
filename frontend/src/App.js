import React from 'react';

import Controls from './features/controls/Controls'
import Footer from './features/Footer'
import GridAndChat from './features/GridAndChat'
import Navbar from './features/Navbar'

import 'bootstrap/dist/css/bootstrap.css';
import './App.css';

import addDemoData from './demoData'
import { useDispatch } from 'react-redux';

function App() {
  addDemoData(useDispatch());
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
