import { configureStore } from '@reduxjs/toolkit';
import playersReducer from '../features/stateSlices/players'
import chatReducer from '../features/stateSlices/chatEntries'
import roleReducer from '../features/stateSlices/role'
import stageReducer from '../features/stateSlices/gameStage'

export default configureStore({
  reducer: {
    players: playersReducer,
    chat: chatReducer,
    stage: stageReducer,
    role: roleReducer,
  },
});
