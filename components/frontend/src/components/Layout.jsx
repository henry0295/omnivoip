import { useState } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { Outlet } from 'react-router-dom'
import { Box, Toolbar } from '@mui/material'
import Navbar from './Navbar'
import Sidebar from './Sidebar'
import Softphone from './Softphone'
import { toggleSidebar } from '@store/slices/uiSlice'

const Layout = () => {
  const dispatch = useDispatch()
  const { sidebarOpen } = useSelector((state) => state.ui)
  const [softphoneOpen, setSoftphoneOpen] = useState(false)

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <Navbar onMenuClick={() => dispatch(toggleSidebar())} />
      <Sidebar open={sidebarOpen} />

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          backgroundColor: (theme) => theme.palette.background.default,
          overflow: 'auto',
        }}
      >
        <Toolbar />
        <Outlet />
      </Box>

      {/* Floating Softphone */}
      <Softphone open={softphoneOpen} onClose={() => setSoftphoneOpen(false)} />
    </Box>
  )
}

export default Layout
