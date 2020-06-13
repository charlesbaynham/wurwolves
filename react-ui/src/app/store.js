import { configureStore } from '@reduxjs/toolkit';


export default configureStore({
  reducer: {
    players: playersReducer,
    state: (oldState, newState) => newState,
  },
});
