import { Paper, Box, Typography, Skeleton } from '@mui/material'
import { TrendingUp, TrendingDown } from '@mui/icons-material'

const StatsCard = ({ title, value, icon, trend, loading = false }) => {
  const isPositive = trend && trend > 0

  return (
    <Paper elevation={2} sx={{ p: 2, height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
        <Typography variant="subtitle2" color="text.secondary">
          {title}
        </Typography>
        <Box sx={{ color: 'primary.main' }}>{icon}</Box>
      </Box>

      {loading ? (
        <Skeleton variant="text" width="60%" height={40} />
      ) : (
        <Typography variant="h4" fontWeight="bold">
          {value}
        </Typography>
      )}

      {trend !== undefined && !loading && (
        <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
          {isPositive ? (
            <TrendingUp sx={{ fontSize: 16, color: 'success.main', mr: 0.5 }} />
          ) : (
            <TrendingDown
              sx={{ fontSize: 16, color: 'error.main', mr: 0.5 }}
            />
          )}
          <Typography
            variant="caption"
            color={isPositive ? 'success.main' : 'error.main'}
          >
            {Math.abs(trend)}% vs last period
          </Typography>
        </Box>
      )}
    </Paper>
  )
}

export default StatsCard
