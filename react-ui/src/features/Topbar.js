import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import Navbar from 'react-bootstrap/Navbar';
import Form from 'react-bootstrap/Form';
import HelpButton from './HelpButton'
import {
  Link
} from 'react-router-dom'

import {
  selectMyName,
  selectMyNameIsGenerated
} from './selectors'


function Topbar(props) {
  const name = useSelector(selectMyName);
  const name_is_generated = useSelector(selectMyNameIsGenerated);

  const [chosenName, setChosenName] = useState(null);

  if (!chosenName && name && !name_is_generated) {
    setChosenName(name)
  }

  return (
    <Navbar expand="lg" bg="light" className="bg-secondary bg-night-black">
      <Link to="/" className="px-2"><img src="/images/logo.svg" alt="Wurwolves logo" id="logo" /></Link>
      <Link className="navbar-brand px-2" to="/">Wurwolves</Link>
      <div className="d-flex ml-auto">
        <Form className="px-2" onSubmit={e => {
          e.preventDefault()
          document.activeElement.blur()
        }}>
          <Form.Control
            placeholder={name}
            onChange={e => setChosenName(e.target.value)}
            onBlur={() => requestNewName(chosenName)}
            value={chosenName ? chosenName : ""}
          />
        </Form>
        <HelpButton className="px-2"/>
      </div>
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
