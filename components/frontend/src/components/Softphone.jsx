import { useState, useEffect } from 'react'
import { useDispatch } from 'react-redux'
import {
  Paper,
  Box,
  Typography,
  TextField,
  IconButton,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Divider,
} from '@mui/material'
import {
  Call,
  CallEnd,
  Mic,
  MicOff,
  Pause,
  PlayArrow,
  Dialpad,
} from '@mui/icons-material'
import sipService from '@services/sipService'
import { setActiveCall } from '@store/slices/callsSlice'
import { setAgentStatus } from '@store/slices/agentsSlice'

const Softphone = ({ open, onClose }) => {
  const dispatch = useDispatch()
  const [phoneNumber, setPhoneNumber] = useState('')
  const [isCallActive, setIsCallActive] = useState(false)
  const [isMuted, setIsMuted] = useState(false)
  const [isOnHold, setIsOnHold] = useState(false)
  const [callDuration, setCallDuration] = useState(0)
  const [agentStatus, setStatus] = useState('AVAILABLE')

  useEffect(() => {
    let interval
    if (isCallActive) {
      interval = setInterval(() => {
        setCallDuration((prev) => prev + 1)
      }, 1000)
    } else {
      setCallDuration(0)
    }
    return () => clearInterval(interval)
  }, [isCallActive])

  const handleCall = () => {
    if (!isCallActive && phoneNumber) {
      sipService.makeCall(phoneNumber)
      setIsCallActive(true)
      dispatch(setActiveCall({ number: phoneNumber, status: 'calling' }))
      dispatch(setAgentStatus('BUSY'))
    }
  }

  const handleHangup = () => {
    sipService.hangupCall()
    setIsCallActive(false)
    setCallDuration(0)
    dispatch(setActiveCall(null))
    dispatch(setAgentStatus('AVAILABLE'))
  }

  const handleMute = () => {
    if (isMuted) {
      sipService.unmuteAudio()
    } else {
      sipService.muteAudio()
    }
    setIsMuted(!isMuted)
  }

  const handleHold = () => {
    if (isOnHold) {
      sipService.unholdCall()
    } else {
      sipService.holdCall()
    }
    setIsOnHold(!isOnHold)
  }

  const handleStatusChange = (status) => {
    setStatus(status)
    dispatch(setAgentStatus(status))
  }

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs
      .toString()
      .padStart(2, '0')}`
  }

  if (!open) return null

  return (
    <Paper
      elevation={3}
      sx={{
        position: 'fixed',
        bottom: 20,
        right: 20,
        width: 320,
        p: 2,
        zIndex: 1300,
      }}
    >
      <Typography variant="h6" gutterBottom>
        Softphone
      </Typography>

      <Divider sx={{ mb: 2 }} />

      {/* Agent Status */}
      <FormControl fullWidth size="small" sx={{ mb: 2 }}>
        <InputLabel>Status</InputLabel>
        <Select
          value={agentStatus}
          label="Status"
          onChange={(e) => handleStatusChange(e.target.value)}
        >
          <MenuItem value="AVAILABLE">Available</MenuItem>
          <MenuItem value="BUSY">Busy</MenuItem>
          <MenuItem value="ON_BREAK">On Break</MenuItem>
          <MenuItem value="OFFLINE">Offline</MenuItem>
        </Select>
      </FormControl>

      {/* Phone Number Input */}
      <TextField
        fullWidth
        size="small"
        label="Phone Number"
        value={phoneNumber}
        onChange={(e) => setPhoneNumber(e.target.value)}
        disabled={isCallActive}
        sx={{ mb: 2 }}
      />

      {/* Call Duration */}
      {isCallActive && (
        <Box sx={{ textAlign: 'center', mb: 2 }}>
          <Typography variant="h4" color="primary">
            {formatDuration(callDuration)}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {isOnHold ? 'On Hold' : 'In Call'}
          </Typography>
        </Box>
      )}

      {/* Call Controls */}
      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mb: 2 }}>
        {!isCallActive ? (
          <IconButton
            color="primary"
            size="large"
            onClick={handleCall}
            disabled={!phoneNumber}
            sx={{
              bgcolor: 'primary.main',
              color: 'white',
              '&:hover': { bgcolor: 'primary.dark' },
            }}
          >
            <Call />
          </IconButton>
        ) : (
          <>
            <IconButton
              color={isMuted ? 'error' : 'default'}
              onClick={handleMute}
            >
              {isMuted ? <MicOff /> : <Mic />}
            </IconButton>

            <IconButton
              color={isOnHold ? 'warning' : 'default'}
              onClick={handleHold}
            >
              {isOnHold ? <PlayArrow /> : <Pause />}
            </IconButton>

            <IconButton
              color="error"
              size="large"
              onClick={handleHangup}
              sx={{
                bgcolor: 'error.main',
                color: 'white',
                '&:hover': { bgcolor: 'error.dark' },
              }}
            >
              <CallEnd />
            </IconButton>
          </>
        )}
      </Box>

      {/* Hidden audio element for remote stream */}
      <audio id="remoteAudio" autoPlay />
    </Paper>
  )
}

export default Softphone
