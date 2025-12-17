import { createSlice } from '@reduxjs/toolkit'

const agentsSlice = createSlice({
  name: 'agents',
  initialState: {
    items: [],
    loading: false,
    error: null,
    currentStatus: 'OFFLINE',
  },
  reducers: {
    setAgentStatus: (state, action) => {
      state.currentStatus = action.payload
    },
    updateAgentList: (state, action) => {
      state.items = action.payload
    },
  },
})

export const { setAgentStatus, updateAgentList } = agentsSlice.actions
export default agentsSlice.reducer
