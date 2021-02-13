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

const config = createSlice({
  name: 'config',
  initialState: {
    gameConfig: {
      number_of_wolves: null,
      probability_of_villager: null,
      role_weights: {}
    },
    defaultConfig: {
      number_of_wolves: null,
      probability_of_villager: null,
      role_weights: {}
    }
  },
  reducers: {
    replaceGameConfig: (state, action) => Object.assign({}, state, { gameConfig: action.payload }),
    replaceDefaultConfig: (state, action) => Object.assign({}, state, { defaultConfig: action.payload }),
  }
})

export const setGameConfig = config.actions.replaceGameConfig
export const setDefaultConfig = config.actions.replaceDefaultConfig
export const clearGameConfig = config.actions.clear

const reducer = combineReducers({
  backend: backend.reducer,
  selectedPlayer: selectedPlayer.reducer,
  config: config.reducer,
})


// Expose the store on window.store for debugging
let store = createStore(
  reducer,
  composeWithDevTools()
);
window.store = store;

export default store;
