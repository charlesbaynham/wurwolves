import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ReactMarkdown from 'react-markdown';

import Button from 'react-bootstrap/Button';

import {
    selectControls, selectSelectedPlayer
} from './selectors'
import { make_api_url } from '../utils'

import { unselectAll } from '../app/store'
import { RolePicture } from './RolePicture'


const DEFAULT_STATE = {
    title: "",
    text: "",
    button_visible: false,
    button_enabled: false,
}

function Controls(props) {
    var controlsState = useSelector(selectControls);
    const selected_player = useSelector(selectSelectedPlayer);
    const dispatch = useDispatch();

    const [isSending, setIsSending] = useState(false)
    const [isError, setIsError] = useState(false);

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

            // Log the error to the console
            r.json().then(r => console.log(r))

            // Add then remove the "error" class from the button
            setIsError(true);
            await wait(1000);
            setIsError(false);
        }
    }

    return (
        <div className="row pt-4 pt-md-0 d-flex  flex-row-reverse align-items-center">
            <div className="col-md">
                {controlsState.button_visible ?
                    <div>
                        <Button onClick={doButtonAction} variant={controlsState.button_enabled ? "primary" : "success"}
                            size="lg" block disabled={!controlsState.button_enabled || isSending}
                            className={isError ? "error" : ""}>
                            <em>{controlsState.button_text}</em>
                        </Button>
                    </div>
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
