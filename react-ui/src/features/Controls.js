import React from 'react';
import { useSelector } from 'react-redux';
import ReactMarkdown from 'react-markdown';

import {
    selectRole
} from './stateSlices/role'
import {
    selectStage
} from './stateSlices/gameStage'


function Controls() {
    const role = useSelector(selectRole);
    const game_stage = useSelector(selectStage);

    console.log(game_stage)

    var left_text;
    if (game_stage === "day") {
        left_text = role.day_text;
    } else {
        left_text = role.night_text;
    }

    return (
        <div className="row pt-4 pt-md-0 d-flex  flex-row-reverse align-items-center">
            <div className="col-md">
                <button type="button" className="btn btn-secondary btn-block btn-lg"><em>Select someone to
                          lynch...</em></button>
            </div>
            <div className="col-md pt-4 pt-md-0">
                <h5>You are a {role.name}</h5>
                <ReactMarkdown source={left_text} />
            </div>
        </div>
    )
}

export default Controls;
