import React from 'react';
import Navbar from 'react-bootstrap/Navbar';
import Form from 'react-bootstrap/Form';


function Topbar() {
    return (
      <Navbar expand="lg" bg="light" className="bg-secondary bg-night-black">
        <a className="navbar-brand" href="/">Wurwolves</a>
        <Form className="ml-auto">
          <Form.Control placeholder="Your name..." />
        </Form>
      </Navbar>
    )
  }

export default Topbar;
