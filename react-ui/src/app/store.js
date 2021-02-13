import { createStore, combineReducers } from 'redux'
import { createSlice } from '@reduxjs/toolkit'
import { composeWithDevTools } from 'redux-devtools-extension'


const backend = createSlice({
  name: 'backend',
  initialState: {
    state_hash: 0,
    players: [],
    chat: [],
    showSecretChat: false,
    stage: "LOBBY",
    controls_state: {},
    myID: "",
    myName: "",
    myNameIsGenerated: true,
    myStatus: null,
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

const gameConfig = createSlice({
  name: 'gameConfig',
  initialState: null,
  reducers: {
    replace: (state, action) => action.payload,
    clear: (state) => null,
  }
})

export const setConfig = gameConfig.actions.replace
export const clearConfig = gameConfig.actions.clear

const reducer = combineReducers({
  backend: backend.reducer,
  selectedPlayer: selectedPlayer.reducer,
  gameConfig: gameConfig.reducer,
})


// Expose the store on window.store for debugging
let store = createStore(
  reducer,
  composeWithDevTools()
);
window.store = store;

export default store;
