import { createSlice } from '@reduxjs/toolkit';

class PlayerData {
  constructor(id, name, status, selected) {
    this.id = id;
    this.name = name;
    this.status = status;
    this.selected = selected;
  }
}

export const playersSlice = createSlice({
  name: 'players',
  initialState: {},
  reducers: {
    addPlayer: (state, action) => {
      // Redux Toolkit allows us to write "mutating" logic in reducers. It
      // doesn't actually mutate the state because it uses the Immer library,
      // which detects changes to a "draft state" and produces a brand new
      // immutable state based off those changes
      var new_player = new PlayerData(action.payload.id, action.payload.name, action.payload.status, false);
      state[action.payload.id] = new_player;
      return state;
    },
    removePlayer: (state, action) => {
      var idToRemove = action.payload;
      delete state[idToRemove];
      return state;
    },
    setPlayerName: (state, action) => {
      state[action.payload.id].name = action.payload.name
      return state;
    },
    setPlayerStatus: (state, action) => {
      state[action.payload.id].status = action.payload.status
      return state;
    },
    setPlayerSelected: (state, action) => {
      state[action.payload.id].selected = action.payload.selected
      return state;
    },
  },
});

export const { addPlayer, removePlayer, setPlayerName, setPlayerStatus, setPlayerSelected } = playersSlice.actions;

// The function below is called a selector and allows us to select a value from
// the state. Selectors can also be defined inline where they're used instead of
// in the slice file. For example: `useSelector((state) => state.counter.value)`
export const selectPlayerName = id => (state => state.players[id].name);
export const selectPlayerStatus = id => (state => state.players[id].status);
export const selectPlayerSelected = id => (state => state.players[id].selected);

export const selectAllPlayers = state => state.players;

export default playersSlice.reducer;
