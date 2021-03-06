import React, { useState } from 'react';

import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Alert from 'react-bootstrap/Alert';

import ReactMarkdown from 'react-markdown';

import { make_api_url } from '../../utils'
import { settings_text } from '../../prose'

import styles from './SettingsButton.module.css'
import icon from './icon.svg'

function SettingsButton({className, gameTag}) {

    const [show, setShow] = useState(false);

    const [endClicked, setEndClicked] = useState(false);
    const [endTimeoutComplete, setEndTimeoutComplete] = useState(false);
    const [timeoutID, setTimeoutID] = useState(null);

    const handleClose = () => {
        setShow(false);
        setEndClicked(false);
        setEndTimeoutComplete(false);
        if (timeoutID) {
            clearTimeout(timeoutID);
            setTimeoutID(null);
        }
    };
    const handleShow = () => setShow(true);

    return (
        <>
        <a className={`navbar-settings ${className}`}
            href="/" onClick={ (event) => {
                event.preventDefault()
                handleShow()
            } }>
            <img src={icon} alt="Utilities icon" className={styles.icon}/>
        </a>

        <Modal show={show} onHide={handleClose}>
            <Modal.Header closeButton>
                <Modal.Title>Utilities</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <ReactMarkdown source={settings_text} />

                <h5>End game</h5>
                End the game for everyone. Use with care!

                {!endClicked ?
                    <Button variant="danger" block onClick={() => {
                        setEndClicked(true);
                        setTimeoutID(setTimeout(() => {
                            setEndTimeoutComplete(true);
                            setTimeoutID(null);
                        }, 3000));
                    }}>
                        End game
                    </Button>
                :
                    <Alert variant="danger">
                        {endTimeoutComplete ?
                            <Button variant="danger" block onClick={() => {
                                endGame(gameTag);
                                handleClose();
                            }}>
                                Confirm end game
                            </Button>
                        :
                            <>Wait for it...</>
                        }
                    </Alert>
                }


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

function endGame(game_tag) {
    fetch(make_api_url(game_tag, "end_game"), { method: 'post' })
}

export default SettingsButton;
