import { useState, useEffect } from 'react'
import { Box, Typography, Chip } from '@mui/material'
import DataTable from '@components/DataTable'
import api from '@services/api'
import { toast } from 'react-toastify'

const Calls = () => {
  const [calls, setCalls] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchCalls()
  }, [])

  const fetchCalls = async () => {
    setLoading(true)
    try {
      const response = await api.get('/calls/')
      setCalls(response.data.results || response.data)
    } catch (error) {
      toast.error('Failed to fetch calls')
    } finally {
      setLoading(false)
    }
  }

  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'COMPLETED':
        return 'success'
      case 'FAILED':
        return 'error'
      case 'BUSY':
        return 'warning'
      case 'NO_ANSWER':
        return 'default'
      default:
        return 'default'
    }
  }

  const columns = [
    {
      field: 'call_id',
      headerName: 'Call ID',
      sortable: true,
    },
    {
      field: 'caller_number',
      headerName: 'From',
      sortable: true,
    },
    {
      field: 'called_number',
      headerName: 'To',
      sortable: true,
    },
    {
      field: 'direction',
      headerName: 'Direction',
      sortable: true,
      render: (value) => (
        <Chip
          label={value}
          size="small"
          color={value === 'INBOUND' ? 'primary' : 'secondary'}
        />
      ),
    },
    {
      field: 'status',
      headerName: 'Status',
      sortable: true,
      render: (value) => (
        <Chip label={value} size="small" color={getStatusColor(value)} />
      ),
    },
    {
      field: 'duration',
      headerName: 'Duration',
      sortable: true,
      render: (value) => formatDuration(value || 0),
    },
    {
      field: 'start_time',
      headerName: 'Start Time',
      sortable: true,
      render: (value) => new Date(value).toLocaleString(),
    },
    {
      field: 'agent',
      headerName: 'Agent',
      sortable: true,
      render: (value) => value?.username || 'N/A',
    },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Call History
      </Typography>

      <DataTable columns={columns} data={calls} loading={loading} />
    </Box>
  )
}

export default Calls
