import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '@services/api'

export const fetchCampaigns = createAsyncThunk(
  'campaigns/fetchAll',
  async () => {
    const response = await api.get('/campaigns/')
    return response.data
  }
)

const campaignsSlice = createSlice({
  name: 'campaigns',
  initialState: {
    items: [],
    loading: false,
    error: null,
    currentCampaign: null,
  },
  reducers: {
    setCurrentCampaign: (state, action) => {
      state.currentCampaign = action.payload
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCampaigns.pending, (state) => {
        state.loading = true
      })
      .addCase(fetchCampaigns.fulfilled, (state, action) => {
        state.loading = false
        state.items = action.payload.results || action.payload
      })
      .addCase(fetchCampaigns.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message
      })
  },
})

export const { setCurrentCampaign } = campaignsSlice.actions
export default campaignsSlice.reducer
