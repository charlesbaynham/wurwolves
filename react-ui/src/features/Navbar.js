import React from 'react';

function Navbar() {
    return (
      <nav className="navbar navbar-expand-lg navbar-light bg-secondary bg-night-black">
        <a className="navbar-brand" href="/">Wurwolves</a>
        <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent"
          aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
          <span className="navbar-toggler-icon"></span>
        </button>
      </nav>
    )
  }

export default Navbar;
