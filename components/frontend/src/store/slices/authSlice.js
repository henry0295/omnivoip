import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '@services/api'

// Async thunks
export const login = createAsyncThunk(
  'auth/login',
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await api.post('/auth/login/', credentials)
      localStorage.setItem('access_token', response.data.tokens.access)
      localStorage.setItem('refresh_token', response.data.tokens.refresh)
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Login failed')
    }
  }
)

export const logout = createAsyncThunk('auth/logout', async () => {
  await api.post('/auth/logout/')
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
})

export const fetchCurrentUser = createAsyncThunk(
  'auth/fetchCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/auth/users/me/')
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data)
    }
  }
)

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    isAuthenticated: !!localStorage.getItem('access_token'),
    loading: false,
    error: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false
        state.isAuthenticated = true
        state.user = action.payload.user
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
      // Logout
      .addCase(logout.fulfilled, (state) => {
        state.user = null
        state.isAuthenticated = false
      })
      // Fetch current user
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.user = action.payload
      })
  },
})

export const { clearError } = authSlice.actions
export default authSlice.reducer
