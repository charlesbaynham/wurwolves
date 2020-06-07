import { createSlice } from '@reduxjs/toolkit';


export const myIDSlice = createSlice({
  name: 'myID',
  initialState: "",
  reducers: {
    setID: (state, action) => {
      return action.payload;
    },
  },
});

export const { setID } = myIDSlice.actions;

export const selectMyID = (state => state);

export default myIDSlice.reducer;
