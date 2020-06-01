import { createSlice } from '@reduxjs/toolkit';


export const chatSlice = createSlice({
    name: 'chat',
    initialState: [],
    reducers: {
        addChatEntry: (state, action) => {
            const msg = action.payload.msg;
            const strong = action.payload.isStrong;
            state.push({ msg: msg, isStrong: strong })
            return state;
        },
        clearChat: state => {
            return [];
        }
    },
});

export const { addChatEntry, clearChat } = chatSlice.actions;

// The function below is called a selector and allows us to select a value from
// the state. Selectors can also be defined inline where they're used instead of
// in the slice file. For example: `useSelector((state) => state.counter.value)`
export const selectMessages = (state => state.chat);

export default chatSlice.reducer;
