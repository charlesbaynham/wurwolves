import { createSlice } from '@reduxjs/toolkit';


export const roleSlice = createSlice({
  name: 'role',
  initialState: {
    title: "",
    day_text: "",
    night_text: "",
    button_visible: false,
    button_enabled: false,
    button_text: "",
    button_confirm_text: "",
  },
  reducers: {
    setRole: (state, action) => {
      for (const property in action.payload) {
        state[property] = action.payload[property]
      }
      
      return state;
    },
  },
});

export const { setRole } = roleSlice.actions;

// The function below is called a selector and allows us to select a value from
// the state. Selectors can also be defined inline where they're used instead of
// in the slice file. For example: `useSelector((state) => state.counter.value)`
export const selectRole = (state => state.role);

export default roleSlice.reducer;
