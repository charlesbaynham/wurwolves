import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import ReactMarkdown from 'react-markdown';

import Button from 'react-bootstrap/Button';

import {
    selectStage, selectRoles, selectSelectedPlayer
} from './selectors'

import { unselectAll } from '../app/store'


const DEFAULT_ROLE = {
    title: "",
    text: "",
    button_visible: false,
    button_enabled: false,
}

function Controls(props) {
    const roles = useSelector(selectRoles);
    const game_stage = useSelector(selectStage);
    const selected_player = useSelector(selectSelectedPlayer);
    const dispatch = useDispatch();

    const [isSending, setIsSending] = useState(false)
    const [isError, setIsError] = useState(false);

    var role = roles[game_stage]

    if (typeof (role) == "undefined") {
        role = DEFAULT_ROLE
    }

    const doButtonAction = async () => {

        console.log(role)

        // don't send again while we are sending
        if (isSending) return
        // update state
        setIsSending(true)

        var url = new URL(`/api/${props.game_tag}/${role.button_submit_func}`, document.baseURI),
            params = { selected_id: selected_player }
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))

        const r = await fetch(url, { method: 'post' })

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
                {role.button_visible ?
                    <div>
                        <Button onClick={doButtonAction} variant="primary"
                            size="lg" block disabled={!role.button_enabled || isSending}
                            className={isError ? "error" : ""}>
                            <em>{role.button_text}</em>
                        </Button>
                    </div>
                    : null}
            </div>
            <div className="col-md pt-4 pt-md-0">
                <h5>{role.title}</h5>
                <ReactMarkdown source={role.text} />
            </div>
        </div>
    )
}

export default Controls;
