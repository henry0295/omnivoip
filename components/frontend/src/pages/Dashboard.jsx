import { useEffect, useState } from 'react'
import { Grid, Typography, Box, Paper } from '@mui/material'
import {
  People,
  Call,
  Campaign,
  TrendingUp,
} from '@mui/icons-material'
import StatsCard from '@components/StatsCard'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalCalls: 1245,
    activeCalls: 23,
    totalAgents: 45,
    activeAgents: 32,
    campaignsRunning: 8,
    avgCallDuration: '4:35',
  })

  const [callsData] = useState([
    { time: '08:00', calls: 12 },
    { time: '09:00', calls: 28 },
    { time: '10:00', calls: 45 },
    { time: '11:00', calls: 38 },
    { time: '12:00', calls: 52 },
    { time: '13:00', calls: 41 },
    { time: '14:00', calls: 35 },
  ])

  const [agentStats] = useState([
    { name: 'Available', value: 32 },
    { name: 'Busy', value: 8 },
    { name: 'On Break', value: 3 },
    { name: 'Offline', value: 2 },
  ])

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Total Calls Today"
            value={stats.totalCalls}
            icon={<Call />}
            trend={12.5}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Active Calls"
            value={stats.activeCalls}
            icon={<Call />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Active Agents"
            value={`${stats.activeAgents}/${stats.totalAgents}`}
            icon={<People />}
            trend={5.2}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Running Campaigns"
            value={stats.campaignsRunning}
            icon={<Campaign />}
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Calls Over Time
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={callsData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="calls"
                  stroke="#1976d2"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Agent Status
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={agentStats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#1976d2" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default Dashboard
