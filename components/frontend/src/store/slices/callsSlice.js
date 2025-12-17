import { createSlice } from '@reduxjs/toolkit'

const callsSlice = createSlice({
  name: 'calls',
  initialState: {
    items: [],
    loading: false,
    error: null,
    activeCall: null,
  },
  reducers: {
    setActiveCall: (state, action) => {
      state.activeCall = action.payload
    },
  },
})

export const { setActiveCall } = callsSlice.actions
export default callsSlice.reducer
