import {
    addPlayer
} from './features/stateSlices/players'
import {
    addChatEntry
} from './features/stateSlices/chatEntries'
import { setStage } from './features/stateSlices/gameStage'
import { setRole } from './features/stateSlices/role'


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

    dispatch(setStage("day"))

    dispatch(setRole({
        name: "Seer",
        day_text: `
You win the game if the villagers lynch all the wolves.

During the night, you may check the identity of one person and discover if they are a wolf.
        `,
        night_text: "You get to check someone's identity!",
        button_visible: true,
        button_enabled: true,
        button_text: "Select someone to lynch...",
        button_confirm_text: "Lynch {}?",
    }))
    
    return
}

export default addDemoData;