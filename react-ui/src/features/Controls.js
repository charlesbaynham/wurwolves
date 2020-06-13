import React from 'react';
import { useSelector } from 'react-redux';
import ReactMarkdown from 'react-markdown';

import Button from 'react-bootstrap/Button';

import {
    selectStage, selectRole
} from './selectors'


function Controls(props) {
    const role = useSelector(selectRole);
    const game_stage = useSelector(selectStage);

    var left_text;
    if (game_stage === "day") {
        left_text = role.day_text;
    } else {
        left_text = role.night_text;
    }

    function doButtonAction(props) {
        return () => {
            var url = new URL(`/api/${props.game_tag}/${role.button_submit_url}`, document.baseURI),
                params = {}
            Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))

            fetch(url)
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
                <ReactMarkdown source={left_text} />
            </div>
        </div>
    )
}

export default Controls;
