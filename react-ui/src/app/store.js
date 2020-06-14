import { createStore } from 'redux'
import { composeWithDevTools } from 'redux-devtools-extension'

const initialState = {
  players: [],
  chat: [],
  stage: "LOBBY",
  role: {
    title: "",
    day_text: "",
    night_text: "",
    lobby_text: "",
    button_visible: false,
    button_enabled: false,
    button_text: "",
    button_confirm_text: "",
    button_submit_url: null,
    button_submit_person: null,
  },
  myID: "",
}

export function replaceState(state) {
  return {
    type: "REPLACE",
    state: state
  }
} 

function reducer(state, action) {
  if (typeof state === 'undefined') {
    return initialState
  } else {
    return action.state
  }
}

export default createStore(
  reducer,
  composeWithDevTools()
);
