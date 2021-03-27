import React, { useState } from 'react';
import { useSelector } from 'react-redux';

import ReactMarkdown from 'react-markdown';

import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Alert from 'react-bootstrap/Alert';

import { selectIsCustomized } from '../selectors'

import DistributionSetup from '../DistributionSetup'

import { make_api_url } from '../../utils'
import { settings_text } from '../../prose'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCircle } from '@fortawesome/free-solid-svg-icons'

import styles from './SettingsButton.module.css'
import icon from './icon.svg'

function SettingsButton({ className, gameTag }) {

    const [show, setShow] = useState(false);

    const [endClicked, setEndClicked] = useState(false);
    const [endTimeoutComplete, setEndTimeoutComplete] = useState(false);
    const [timeoutID, setTimeoutID] = useState(null);

    const isCustomized = useSelector(selectIsCustomized);

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
            <a className={`${styles.link} ${className}`}
                href="/" onClick={(event) => {
                    event.preventDefault()
                    handleShow()
                }}>
                <img src={icon} alt="Utilities icon" className={styles.icon} />
                {
                    isCustomized ?
                        <FontAwesomeIcon className={styles.notification} icon={faCircle} />
                        : null
                }

            </a>

            <Modal show={show} onHide={handleClose}>
                <Modal.Header closeButton>
                    <Modal.Title>Utilities</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <ReactMarkdown source={settings_text} />

                    <h5 className='mt-3'>Customise roles</h5>

                    Change the settings for the next time this game is restarted:

                    <DistributionSetup game_tag={gameTag} auto_update={true} no_padding={true} />

                    <h5 className='mt-3'>End game</h5>
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
