import React, { useState } from 'react';

import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Tabs from 'react-bootstrap/Tabs'
import Tab from 'react-bootstrap/Tab'

import ReactMarkdown from 'react-markdown';
import {help_text} from '../prose'
import RoleDescriptions  from './RoleDescriptions'


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

        <Modal show={show} onHide={handleClose} size="lg">
            <Modal.Header closeButton>
                <Modal.Title>How to play</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Tabs id="help-tabs" defaultActiveKey="intro" className="flex-row">
                    <Tab eventKey="intro" title="Game" className="px-1">
                        <ReactMarkdown className="help_text" source={help_text} />
                    </Tab>
                    <Tab eventKey="roles" title="Roles">
                        <RoleDescriptions/>
                    </Tab>
                </Tabs>
            </Modal.Body>
            <Modal.Footer>
            <Button variant="primary" onClick={handleClose}>
                Close
            </Button>
            </Modal.Footer>
        </Modal>
        </>
    )
}


export default HelpButton;
