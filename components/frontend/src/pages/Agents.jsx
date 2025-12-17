import { useState, useEffect } from 'react'
import { Box, Typography, Grid, Paper, Chip } from '@mui/material'
import DataTable from '@components/DataTable'
import api from '@services/api'
import { toast } from 'react-toastify'

const Agents = () => {
  const [agents, setAgents] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchAgents()
  }, [])

  const fetchAgents = async () => {
    setLoading(true)
    try {
      const response = await api.get('/agents/status/')
      setAgents(response.data.results || response.data)
    } catch (error) {
      toast.error('Failed to fetch agents')
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'AVAILABLE':
        return 'success'
      case 'BUSY':
        return 'error'
      case 'ON_BREAK':
        return 'warning'
      case 'OFFLINE':
        return 'default'
      default:
        return 'default'
    }
  }

  const columns = [
    {
      field: 'agent',
      headerName: 'Agent',
      sortable: true,
      render: (value) => value?.username || 'N/A',
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
      field: 'current_call_id',
      headerName: 'Current Call',
      sortable: true,
      render: (value) => value || '-',
    },
    {
      field: 'calls_today',
      headerName: 'Calls Today',
      sortable: true,
    },
    {
      field: 'avg_call_duration',
      headerName: 'Avg Duration',
      sortable: true,
      render: (value) => {
        if (!value) return '-'
        const mins = Math.floor(value / 60)
        const secs = value % 60
        return `${mins}:${secs.toString().padStart(2, '0')}`
      },
    },
    {
      field: 'last_activity',
      headerName: 'Last Activity',
      sortable: true,
      render: (value) => (value ? new Date(value).toLocaleString() : '-'),
    },
  ]

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Agents
      </Typography>

      <DataTable columns={columns} data={agents} loading={loading} />
    </Box>
  )
}

export default Agents
