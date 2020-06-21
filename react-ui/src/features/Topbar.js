import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import Navbar from 'react-bootstrap/Navbar';
import Form from 'react-bootstrap/Form';

import {
  selectMyName,
  selectMyNameIsGenerated
} from './selectors'


function Topbar(props) {
  const name = useSelector(selectMyName);
  const name_is_generated = useSelector(selectMyNameIsGenerated);

  const [chosenName, setChosenName] = useState(null);

  if (!name_is_generated && chosenName === null) {
    setChosenName(name)
  }

  return (
    <Navbar expand="lg" bg="light" className="bg-secondary bg-night-black">
      <a className="navbar-brand" href="/">Wurwolves</a>
      <Form className="ml-auto" onSubmit={e => {
        e.preventDefault()
        document.activeElement.blur()
      }}>
        <Form.Control
          placeholder="Your name..."
          onChange={e => setChosenName(e.target.value)}
          onBlur={() => requestNewName(chosenName)}
          value={chosenName ? chosenName : ""}
        />
      </Form>
    </Navbar>
  )
}

function requestNewName(name) {
  var url = new URL(`/api/set_name`, document.baseURI)
  const params = { name: name }
  Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))

  fetch(url, { method: 'post', params: params })
}

export default Topbar;
