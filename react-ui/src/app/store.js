import { createStore, combineReducers } from 'redux'
import { createSlice } from '@reduxjs/toolkit'
import { composeWithDevTools } from 'redux-devtools-extension'


const backend = createSlice({
  name: 'backend',
  initialState: {
    state_hash: 0,
    players: [],
    chat: [],
    stage: "LOBBY",
    roles: {},
    myID: "",
    myName: "",
    myNameIsGenerated: true,
  },
  reducers: {
    replace: (state, action) => action.payload
  }
})

export const replaceState = backend.actions.replace

const reducer = combineReducers({
  backend: backend.reducer,
})

export default createStore(
  reducer,
  composeWithDevTools()
);
