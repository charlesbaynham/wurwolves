import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';

import {
  Link
} from 'react-router-dom'


function HelpButton() {

    const [show, setShow] = useState(false);

    const handleClose = () => setShow(false);
    const handleShow = () => setShow(true);

    return (
        <>
        <a className="navbar-help"
            href="/" onClick={ (event) => {
                event.preventDefault()
                handleShow()
            } }>
            <img src="/images/help.svg" alt="Help icon" id="help"/>
        </a>

        <Modal show={show} onHide={handleClose}>
            <Modal.Header closeButton>
            <Modal.Title>Modal heading</Modal.Title>
            </Modal.Header>
            <Modal.Body>Woohoo, you're reading this text in a modal!</Modal.Body>
            <Modal.Footer>
            <Button variant="secondary" onClick={handleClose}>
                Close
            </Button>
            <Button variant="primary" onClick={handleClose}>
                Save Changes
            </Button>
            </Modal.Footer>
        </Modal>
        </>
    )
}

function requestNewName(name) {
  var url = new URL(`/api/set_name`, document.baseURI)
  const params = { name: name }
  Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))

  fetch(url, { method: 'post', params: params })
}

export default HelpButton;
