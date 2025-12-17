import { createSlice } from '@reduxjs/toolkit'

const queuesSlice = createSlice({
  name: 'queues',
  initialState: {
    items: [],
    loading: false,
    error: null,
    statistics: {},
  },
  reducers: {
    updateQueueStats: (state, action) => {
      state.statistics = action.payload
    },
  },
})

export const { updateQueueStats } = queuesSlice.actions
export default queuesSlice.reducer
