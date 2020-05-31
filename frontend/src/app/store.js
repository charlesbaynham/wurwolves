import { configureStore } from '@reduxjs/toolkit';
import playersReducer from '../features/stateSlices/players'
import chatSlice from '../features/stateSlices/chatEntries'

export default configureStore({
  reducer: {
    players: playersReducer,
    chat: chatSlice,
  },
});
