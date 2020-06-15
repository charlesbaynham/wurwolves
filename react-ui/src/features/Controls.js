import React from 'react';
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

    var role = roles[game_stage]

    if (typeof (role) == "undefined") {
        role = DEFAULT_ROLE
    }

    function doButtonAction(props) {
        return () => {
            dispatch(unselectAll());
            var url = new URL(`/api/${props.game_tag}/${role.button_submit_func}`, document.baseURI),
                params = { selected_id: selected_player }
            Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))

            fetch(url, { method: 'post' })
                .then(r => r.json())
                .then(r => console.log(r))
        }
    }

    return (
        <div className="row pt-4 pt-md-0 d-flex  flex-row-reverse align-items-center">
            <div className="col-md">
                {role.button_visible ?
                    <Button onClick={doButtonAction(props)} variant="primary" size="lg" block disabled={!role.button_enabled}>
                        <em>{role.button_text}</em>
                    </Button>
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
