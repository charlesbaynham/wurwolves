import React from 'react';
import {
  BrowserRouter as Router,
  Route,
  Switch
} from 'react-router-dom'

import { useSelector, useDispatch } from 'react-redux';

import 'bootstrap/dist/css/bootstrap.css';
import './App.css';

import Game from './game'
import Home from './home'

import Footer from './features/Footer'

// For demo data:
import {
  selectStage
} from './features/stateSlices/gameStage'
import addDemoData from './demoData'


function App() {
  addDemoData(useDispatch());
  const game_stage = useSelector(selectStage)
  return (
    <div className={game_stage}>
      <div id="main" className="min-vh-100 bg-night-black">
        <Router>
          <Switch>
            <Route path="/:game_tag" component={Game} />
            <Route path="/" component={Home} />
          </Switch>
        </Router>
        <Footer />
      </div>
    </div>
  );
}

export default App;
