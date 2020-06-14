import { createStore } from 'redux'
import { composeWithDevTools } from 'redux-devtools-extension'

const initialState = {
  state_hash: 0,
  players: [],
  chat: [],
  stage: "LOBBY",
  roles: {},
  myID: "",
  myName: "",
  myNameIsGenerated: true,
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
