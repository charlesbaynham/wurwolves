import { createStore } from 'redux'
import { composeWithDevTools } from 'redux-devtools-extension'

const initialState = {
  players: [],
  chat: [],
  stage: "day",
  role: {
    title: "",
    day_text: "",
    night_text: "",
    button_visible: false,
    button_enabled: false,
    button_text: "",
    button_confirm_text: "",
    button_submit_url: null,
    button_submit_person: null,
  },
  myID: "",
}

function reducer(oldState, newState) {
  if (typeof state === 'undefined') {
    return initialState
  } else {
    return newState
  }
}

export default createStore(
  reducer,
  composeWithDevTools()
);
