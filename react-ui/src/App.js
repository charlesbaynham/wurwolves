import React from 'react';
import {
  BrowserRouter as Router,
  Route,
  Switch
} from 'react-router-dom'

import { useSelector } from 'react-redux';

import 'bootstrap/dist/css/bootstrap.css';
import './App.css';

import Game from './game'
import Home from './home'

import Footer from './features/Footer'

import {
  selectStage
} from './features/selectors'

import ReactGA from 'react-ga'


ReactGA.initialize('UA-186218553-1');
ReactGA.pageview(window.location.pathname + window.location);


function App() {
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
