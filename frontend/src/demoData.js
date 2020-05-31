import React from 'react';

import {
    addPlayer
} from './features/stateSlices/players'
import {
    addChatEntry
} from './features/stateSlices/chatEntries'


const demo_messages = [
    "3 votes for Euan (Rosie, Rachel, Gaby)",
    "<strong>Gaby was voted off</strong>",
    "<strong>Sophie was killed in the night</strong>",
    "Rob was nominated by Charles",
    "James was nominated by Charles",
    "James was seconded by Parav",
    "4 votes for Gaby (Charles, James, Parav, Harry)",
    "3 votes for Euan (Rosie, Rachel, Gaby)",
    "<strong>Gaby was voted off</strong>",
    "<strong>Sophie was killed in the night</strong>",
    "Rob was nominated by Charles",
    "James was nominated by Charles",
    "James was seconded by Parav",
    "4 votes for Gaby (Charles, James, Parav, Harry)",
    "3 votes for Euan (Rosie, Rachel, Gaby)",
    "<strong>Gaby was voted off</strong>",
    "<strong>Sophie was killed in the night</strong>",
    "Rob was nominated by Charles",
    "James was nominated by Charles",
    "James was seconded by Parav"
]

export function addDemoData(dispatch) {

    var id = 0;

    for (const msg in demo_messages) {
        dispatch(addChatEntry(demo_messages[msg]));
    }

    dispatch(addPlayer({
        id: "123",
        name: "Hello world",
        status: "normal"
    }))
    dispatch(addPlayer({
        id: "321",
        name: "Next one",
        status: "wolfed"
    }))

    return (
        <p>Nothing</p>
    )
}

export default addDemoData;