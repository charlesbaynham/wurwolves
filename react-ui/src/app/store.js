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
    controls: {},
    myID: "",
    myName: "",
    myNameIsGenerated: true,
  },
  reducers: {
    replace: (state, action) => action.payload
  }
})

export const replaceState = backend.actions.replace

const selectedPlayer = createSlice({
  name: 'selectedPlayer',
  initialState: null,
  reducers: {
    selectPlayer: (state, action) => action.payload,
    unselectAll: state => null, 
  }
})

export const selectPlayer = selectedPlayer.actions.selectPlayer
export const unselectAll = selectedPlayer.actions.unselectAll

const reducer = combineReducers({
  backend: backend.reducer,
  selectedPlayer: selectedPlayer.reducer,
})



export default createStore(
  reducer,
  composeWithDevTools()
);
