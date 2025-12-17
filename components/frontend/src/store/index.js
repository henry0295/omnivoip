import { configureStore } from '@reduxjs/toolkit'
import authReducer from './slices/authSlice'
import campaignsReducer from './slices/campaignsSlice'
import contactsReducer from './slices/contactsSlice'
import callsReducer from './slices/callsSlice'
import agentsReducer from './slices/agentsSlice'
import queuesReducer from './slices/queuesSlice'
import reportsReducer from './slices/reportsSlice'
import uiReducer from './slices/uiSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    campaigns: campaignsReducer,
    contacts: contactsReducer,
    calls: callsReducer,
    agents: agentsReducer,
    queues: queuesReducer,
    reports: reportsReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
})

export default store
