import React from "react";
import {
  RouterProvider,
  Route,
  Routes,
  createBrowserRouter,
} from "react-router-dom";

import { useSelector } from "react-redux";

import "bootstrap/dist/css/bootstrap.css";
import "./App.css";

import Game from "./game";
import Home from "./home";

import Footer from "./features/Footer";

import { selectStage } from "./features/selectors";

const router = createBrowserRouter([
  {
    path: "/:game_tag",
    element: <Game />,
  },
  {
    path: "/",
    element: <Home />,
  },
]);

// Disable console.log in production
function noop() {}
if (process.env.NODE_ENV !== "development") {
  console.debug = noop;
  console.log = noop;
  console.warn = noop;
  console.error = noop;
}

function App() {
  const game_stage = useSelector(selectStage);

  return (
    <div className={game_stage}>
      <div id="main" className="min-vh-100 bg-night-black">
        <RouterProvider router={router} />
        <Footer />
      </div>
    </div>
  );
}

export default App;
