import { useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import {
  AppBar,
  Toolbar,
  IconButton,
  Typography,
  Badge,
  Menu,
  MenuItem,
  Avatar,
  Box,
  Chip,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Notifications as NotificationsIcon,
  AccountCircle,
  Logout,
  Settings,
} from '@mui/icons-material'
import { logout } from '@store/slices/authSlice'

const Navbar = ({ onMenuClick }) => {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const { user } = useSelector((state) => state.auth)
  const { currentStatus } = useSelector((state) => state.agents)

  const [anchorEl, setAnchorEl] = useState(null)

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget)
  }

  const handleMenuClose = () => {
    setAnchorEl(null)
  }

  const handleLogout = () => {
    dispatch(logout())
    navigate('/login')
    handleMenuClose()
  }

  const handleProfile = () => {
    navigate('/profile')
    handleMenuClose()
  }

  const handleSettings = () => {
    navigate('/settings')
    handleMenuClose()
  }

  const getStatusColor = () => {
    switch (currentStatus) {
      case 'AVAILABLE':
        return 'success'
      case 'BUSY':
        return 'error'
      case 'ON_BREAK':
        return 'warning'
      default:
        return 'default'
    }
  }

  return (
    <AppBar
      position="fixed"
      sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
    >
      <Toolbar>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          onClick={onMenuClick}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          OmniVoIP Contact Center
        </Typography>

        {/* Agent Status */}
        <Box sx={{ mr: 2 }}>
          <Chip
            label={currentStatus}
            color={getStatusColor()}
            size="small"
            variant="outlined"
            sx={{ color: 'white', borderColor: 'white' }}
          />
        </Box>

        {/* Notifications */}
        <IconButton color="inherit" sx={{ mr: 2 }}>
          <Badge badgeContent={4} color="error">
            <NotificationsIcon />
          </Badge>
        </IconButton>

        {/* User Menu */}
        <IconButton
          edge="end"
          color="inherit"
          onClick={handleProfileMenuOpen}
          aria-label="account"
        >
          <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
            {user?.first_name?.[0] || 'U'}
          </Avatar>
        </IconButton>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
        >
          <MenuItem onClick={handleProfile}>
            <AccountCircle sx={{ mr: 1 }} />
            Profile
          </MenuItem>
          <MenuItem onClick={handleSettings}>
            <Settings sx={{ mr: 1 }} />
            Settings
          </MenuItem>
          <MenuItem onClick={handleLogout}>
            <Logout sx={{ mr: 1 }} />
            Logout
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  )
}

export default Navbar
