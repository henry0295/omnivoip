import { createSlice } from '@reduxjs/toolkit'

const contactsSlice = createSlice({
  name: 'contacts',
  initialState: {
    items: [],
    loading: false,
    error: null,
  },
  reducers: {},
})

export default contactsSlice.reducer
