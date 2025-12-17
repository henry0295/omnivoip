import { io } from 'socket.io-client'
import { store } from '@store'
import { updateAgentList, setAgentStatus } from '@store/slices/agentsSlice'
import { updateQueueStats } from '@store/slices/queuesSlice'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

class WebSocketService {
  constructor() {
    this.socket = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
  }

  connect() {
    const token = localStorage.getItem('access_token')

    if (!token) {
      console.warn('No auth token found, skipping WebSocket connection')
      return
    }

    this.socket = io(WS_URL, {
      auth: {
        token,
      },
      transports: ['websocket'],
    })

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
    })

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected')
      this.handleReconnect()
    })

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error)
    })

    // Listen to events
    this.socket.on('agent_status_update', (data) => {
      store.dispatch(updateAgentList(data.agents))
    })

    this.socket.on('queue_stats_update', (data) => {
      store.dispatch(updateQueueStats(data.stats))
    })

    this.socket.on('campaign_update', (data) => {
      console.log('Campaign updated:', data)
    })

    this.socket.on('call_event', (data) => {
      console.log('Call event:', data)
    })
  }

  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      setTimeout(() => {
        console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`)
        this.connect()
      }, 1000 * this.reconnectAttempts)
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  emit(event, data) {
    if (this.socket && this.socket.connected) {
      this.socket.emit(event, data)
    } else {
      console.warn('WebSocket not connected')
    }
  }

  on(event, callback) {
    if (this.socket) {
      this.socket.on(event, callback)
    }
  }

  off(event, callback) {
    if (this.socket) {
      this.socket.off(event, callback)
    }
  }
}

export default new WebSocketService()
