import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ReactMarkdown from 'react-markdown';

import useClipboard from "react-use-clipboard";

import Button from 'react-bootstrap/Button';

import {
    selectControls, selectSelectedPlayer, selectStage
} from './selectors'
import { make_api_url } from '../utils'

import { unselectAll } from '../app/store'
import { RolePicture } from './RolePicture'

import styles from './Controls.module.css'

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faCopy } from '@fortawesome/free-solid-svg-icons'

const DEFAULT_STATE = {
    title: "",
    text: "",
    button_visible: false,
    button_enabled: false,
}

function Controls(props) {
    var controlsState = useSelector(selectControls);
    const selected_player = useSelector(selectSelectedPlayer);
    const gameStage = useSelector(selectStage);
    const dispatch = useDispatch();

    const [isSending, setIsSending] = useState(false)
    const [isError, setIsError] = useState(false);
    const [errorText, setErrorText] = useState("");
    const [isCopied, setCopied] = useClipboard(window.location.href, {successDuration: 1000});

    if (typeof (controlsState) == "undefined") {
        controlsState = DEFAULT_STATE
    }

    const doButtonAction = async () => {

        // don't send again while we are sending
        if (isSending) return
        // update state
        setIsSending(true)

        const r = await fetch(
            make_api_url(
                props.game_tag,
                controlsState.button_submit_func,
                { selected_id: selected_player }
            ),
            { method: 'post' }
        )

        setIsSending(false)

        if (r.ok) {
            dispatch(unselectAll());
        } else {
            const wait = ms => new Promise(resolve => setTimeout(resolve, ms));

            r.json().then(async r => {
                // Log the error to the console
                console.log(r);

                setErrorText(Array.isArray(r.detail) ? r.detail[0].msg : r.detail);

                // Add then remove the "error" class from the button
                setIsError(true);
                await wait(1000);
                setIsError(false);
            })
        }
    }

    return (
        <div className="row pt-4 pt-md-0 d-flex  flex-row-reverse align-items-center">
            <div className="col-md">
                    {controlsState.button_visible ?
                            <>
                                <Button id="actionButton" onClick={doButtonAction} variant={controlsState.button_enabled ? "primary" : "success"}
                                    size="lg" block disabled={!controlsState.button_enabled || isSending}
                                    className={isError ? "error" : ""}>
                                    <em>{controlsState.button_text}</em>
                                </Button>
                                <div className={styles.errorMessage}>
                                    {isError ? errorText : ""}
                                </div>
                            </>
                            : null}
                    {gameStage === "LOBBY" ?
                        <Button onClick={setCopied} className="mt-2" variant="dark" disabled={isCopied}
                            size="lg" block>
                            <em>Copy link</em>
                            <FontAwesomeIcon className="ml-3" icon={faCopy} />
                        </Button>
                    : null}
            </div>
            <div className="col-md-8 pt-4 pt-md-0">
                <h5>{controlsState.title}</h5>
                <RolePicture role={controlsState.role} status="ALIVE" seed={controlsState.seed} />
                <ReactMarkdown source={controlsState.text} />
            </div>
        </div>
    )
}

export default Controls;
