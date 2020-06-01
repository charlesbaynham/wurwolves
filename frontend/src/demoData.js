import React from 'react';

import {
    addPlayer
} from './features/stateSlices/players'
import {
    addChatEntry
} from './features/stateSlices/chatEntries'


const demo_messages = [
    ["3 votes for Euan (Rosie, Rachel, Gaby)", false],
    ["Gaby was voted off", true],
    ["Sophie was killed in the night", true],
    ["Rob was nominated by Charles", false],
    ["James was nominated by Charles", false],
    ["James was seconded by Parav", false],
    ["4 votes for Gaby (Charles, James, Parav, Harry)", false],
    ["3 votes for Euan (Rosie, Rachel, Gaby)", false],
    ["Gaby was voted off", true],
    ["Sophie was killed in the night", true],
    ["Rob was nominated by Charles", false],
    ["James was nominated by Charles", false],
    ["James was seconded by Parav", false],
    ["4 votes for Gaby (Charles, James, Parav, Harry)", false],
    ["3 votes for Euan (Rosie, Rachel, Gaby)", false],
    ["Gaby was voted off", true],
    ["Sophie was killed in the night", true],
    ["Rob was nominated by Charles", false],
    ["James was nominated by Charles", false]
]

export function addDemoData(dispatch) {

    var id = 0;

    for (const msg in demo_messages) {
        dispatch(addChatEntry({ msg: demo_messages[msg][0], isStrong: demo_messages[msg][1] }));
    }

    dispatch(addPlayer({
        id: "0",
        name: "Hello world",
        status: "normal"
    }))
    dispatch(addPlayer({
        id: "1",
        name: "Dead one",
        status: "wolfed"
    }))
    dispatch(addPlayer({
        id: "2",
        name: "Lynched one",
        status: "lynched"
    }))
    dispatch(addPlayer({
        id: "3",
        name: "Nommed one",
        status: "nominated"
    }))
    dispatch(addPlayer({
        id: "4",
        name: "Seconded one",
        status: "seconded"
    }))
    dispatch(addPlayer({
        id: "5",
        name: "Spectator",
        status: "spectating"
    }))

    return (
        <p>Nothing</p>
    )
}

export default addDemoData;