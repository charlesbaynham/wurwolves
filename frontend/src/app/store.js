import { configureStore } from '@reduxjs/toolkit';
import playersReducer from '../features/stateSlices/players'

export default configureStore({
  reducer: {
    players: playersReducer,
  },
});
