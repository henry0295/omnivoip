import { useNavigate, useLocation } from 'react-router-dom'
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Divider,
} from '@mui/material'
import {
  Dashboard,
  Campaign,
  Contacts,
  Call,
  People,
  Queue,
  Assessment,
  Settings,
} from '@mui/icons-material'

const drawerWidth = 240

const menuItems = [
  { text: 'Dashboard', icon: <Dashboard />, path: '/' },
  { text: 'Campaigns', icon: <Campaign />, path: '/campaigns' },
  { text: 'Contacts', icon: <Contacts />, path: '/contacts' },
  { text: 'Calls', icon: <Call />, path: '/calls' },
  { text: 'Agents', icon: <People />, path: '/agents' },
  { text: 'Queues', icon: <Queue />, path: '/queues' },
  { text: 'Reports', icon: <Assessment />, path: '/reports' },
  { text: 'Settings', icon: <Settings />, path: '/settings' },
]

const Sidebar = ({ open }) => {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <Drawer
      variant="persistent"
      open={open}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      <Toolbar />
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  )
}

export default Sidebar
