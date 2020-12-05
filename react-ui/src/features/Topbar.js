import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import Navbar from 'react-bootstrap/Navbar';
import Form from 'react-bootstrap/Form';

import {
  Link
} from 'react-router-dom'

import { make_api_url } from '../utils'

import HelpButton from './HelpButton'
import SettingsButton from './Settings/SettingsButton'

import {
  selectMyName,
  selectMyNameIsGenerated
} from './selectors'


function Topbar(props) {
  const name = useSelector(selectMyName);
  const name_is_generated = useSelector(selectMyNameIsGenerated);

  const [chosenName, setChosenName] = useState(null);

  if (chosenName === null && name && !name_is_generated) {
    setChosenName(name)
  }

  return (
    <Navbar expand="lg" bg="light" className="bg-secondary bg-night-black">
      <Link to="/" className="px-2"><img src="/images/logo.svg" alt="Wurwolves logo" id="logo" /></Link>
      <Link className="navbar-brand px-2 d-none d-sm-block" to="/">Wurwolves</Link>
      <div className="d-flex ml-auto align-items-center">
        <Form className="pl-2" onSubmit={e => {
          e.preventDefault()
          document.activeElement.blur()
        }}>
          <Form.Control
            placeholder={name}
            onChange={e => setChosenName(e.target.value)}
            onBlur={() => {
              if (chosenName) {
                requestNewName(chosenName);
              } else {
                setChosenName(name);
              }
            }}
            value={chosenName ? chosenName : ""}
          />
        </Form>
        <HelpButton className="pl-2" />
        {props.game_tag ?
          <SettingsButton className="pl-2" gameTag={props.game_tag} />
        : null}
      </div>
    </Navbar>
  )
}

function requestNewName(name) {
  fetch(
    make_api_url(
      null,
      "set_name",
      { name: name }
    ),
    { method: 'post' }
  )
}

export default Topbar;
