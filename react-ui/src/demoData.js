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

    // for (const msg in demo_messages) {
    //     dispatch(addChatEntry({ msg: demo_messages[msg][0], isStrong: demo_messages[msg][1] }));
    // }

    dispatch(setStage("day"))

    return
}

export default addDemoData;