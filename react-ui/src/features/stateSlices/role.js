import { createSlice } from '@reduxjs/toolkit';


export const roleSlice = createSlice({
  name: 'role',
  initialState: {
    name: "",
    day_text: "",
    night_text: "",
    button_visible: false,
    button_enabled: false,
    button_text: "",
    button_confirm_text: "",
  },
  reducers: {
    setRole: (state, action) => {
      state.name = action.payload.name
      state.day_text = action.payload.day_text
      state.night_text = action.payload.night_text
      state.button_visible = action.payload.button_visible
      state.button_enabled = action.payload.button_enabled
      state.button_text = action.payload.button_text
      state.button_confirm_text = action.payload.button_confirm_text

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
