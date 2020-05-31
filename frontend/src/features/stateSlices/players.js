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
  initialState: {
    value: [],
  },
  reducers: {
    addPlayer: (state, action) => {
      // Redux Toolkit allows us to write "mutating" logic in reducers. It
      // doesn't actually mutate the state because it uses the Immer library,
      // which detects changes to a "draft state" and produces a brand new
      // immutable state based off those changes
      new_player = PlayerData(action.payload.id, action.payload.name, action.payload.status, false)
      state.push(new_player)
      return state
    },
    decrement: state => {
      state.value -= 1;
    },
    incrementByAmount: (state, action) => {
      state.value += action.payload;
    },
  },
});