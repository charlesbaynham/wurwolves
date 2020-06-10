import { createSlice } from '@reduxjs/toolkit';


export const playersSlice = createSlice({
  name: 'players',
  initialState: [],
  reducers: {
    addPlayer: (state, action) => {
      // Redux Toolkit allows us to write "mutating" logic in reducers. It
      // doesn't actually mutate the state because it uses the Immer library,
      // which detects changes to a "draft state" and produces a brand new
      // immutable state based off those changes
      const new_player = {
        id: action.payload.id,
        name: action.payload.name,
        status: action.payload.status,
        selected: false
      };
      state.push(new_player);
      return state;
    },
    removePlayer: (state, action) => {
      const id = action.payload.id;
      const ind_player = state.indexOf(p => p.id === id)
      state.splice(ind_player, 1)
      return state;
    },
    setPlayerName: (state, action) => {
      const id = action.payload.id;
      var player = getPlayerById(state, id)
      if (action.payload.name) {
        player.name = action.payload.name
      }
      return state;
    },
    setPlayerStatus: (state, action) => {
      const id = action.payload.id;
      var player = getPlayerById(state, id)
      if (action.payload.status) {
        player.status = action.payload.status
      }
      return state;
    },
    setPlayerSelected: (state, action) => {
      const id = action.payload.id;
      var player = getPlayerById(state, id)
      player.selected = action.payload.selected
      return state;
    },
  },
});

export const { addPlayer, removePlayer, setPlayerName, setPlayerStatus, setPlayerSelected } = playersSlice.actions;

// The function below is called a selector and allows us to select a value from
// the state. Selectors can also be defined inline where they're used instead of
// in the slice file. For example: `useSelector((state) => state.counter.value)`
// export const selectPlayerName = id => (state => state.players[id].name);
// export const selectPlayerStatus = id => (state => state.players[id].status);
// export const selectPlayerSelected = id => (state => state.players[id].selected);

// export const selectPlayerName = id => (state => "potato");
// export const selectPlayerStatus = id => (state => "wolfed");
// export const selectPlayerSelected = id => (state => false);

export function getPlayerById(players, id) {
  return players.find(p => id === p.id);
}

export const selectPlayer = id => (state => getPlayerById(state.players, id));

export const selectPlayerName = id => (state => getPlayerById(state.players, id).name);
export const selectPlayerStatus = id => (state => getPlayerById(state.players, id).status);
export const selectPlayerSelected = id => (state => getPlayerById(state.players, id).selected);

export const selectAllPlayers = state => state.players;

export default playersSlice.reducer;
