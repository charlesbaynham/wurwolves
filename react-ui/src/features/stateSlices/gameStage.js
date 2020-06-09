import { createSlice } from '@reduxjs/toolkit';


export const stageSlice = createSlice({
  name: 'stage',
  initialState: "day",
  reducers: {
    setStage: (state, action) => {
      return action.payload.stage.toLowerCase();
    },
  },
});

export const { setStage } = stageSlice.actions;

export const selectStage = (state => state.stage);

export default stageSlice.reducer;
