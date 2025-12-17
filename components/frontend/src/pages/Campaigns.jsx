import { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material'
import { Add } from '@mui/icons-material'
import DataTable from '@components/DataTable'
import { fetchCampaigns } from '@store/slices/campaignsSlice'
import api from '@services/api'
import { toast } from 'react-toastify'

const Campaigns = () => {
  const dispatch = useDispatch()
  const { items: campaigns, loading } = useSelector((state) => state.campaigns)
  const [openDialog, setOpenDialog] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    campaign_type: 'OUTBOUND',
    status: 'ACTIVE',
    description: '',
  })

  useEffect(() => {
    dispatch(fetchCampaigns())
  }, [dispatch])

  const columns = [
    { field: 'name', headerName: 'Name', sortable: true },
    { field: 'campaign_type', headerName: 'Type', sortable: true },
    {
      field: 'status',
      headerName: 'Status',
      type: 'chip',
      color: 'primary',
    },
    { field: 'total_contacts', headerName: 'Contacts', sortable: true },
    { field: 'calls_made', headerName: 'Calls Made', sortable: true },
    { field: 'success_rate', headerName: 'Success Rate', sortable: true },
  ]

  const handleCreate = async () => {
    try {
      await api.post('/campaigns/', formData)
      toast.success('Campaign created successfully')
      setOpenDialog(false)
      dispatch(fetchCampaigns())
      setFormData({
        name: '',
        campaign_type: 'OUTBOUND',
        status: 'ACTIVE',
        description: '',
      })
    } catch (error) {
      toast.error('Failed to create campaign')
    }
  }

  const handleEdit = (campaign) => {
    setFormData(campaign)
    setOpenDialog(true)
  }

  const handleDelete = async (campaign) => {
    if (window.confirm(`Delete campaign "${campaign.name}"?`)) {
      try {
        await api.delete(`/campaigns/${campaign.id}/`)
        toast.success('Campaign deleted successfully')
        dispatch(fetchCampaigns())
      } catch (error) {
        toast.error('Failed to delete campaign')
      }
    }
  }

  return (
    <Box>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 3,
        }}
      >
        <Typography variant="h4">Campaigns</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setOpenDialog(true)}
        >
          New Campaign
        </Button>
      </Box>

      <DataTable
        columns={columns}
        data={campaigns}
        loading={loading}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />

      {/* Create/Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {formData.id ? 'Edit Campaign' : 'Create Campaign'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            margin="normal"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Type</InputLabel>
            <Select
              value={formData.campaign_type}
              label="Type"
              onChange={(e) =>
                setFormData({ ...formData, campaign_type: e.target.value })
              }
            >
              <MenuItem value="INBOUND">Inbound</MenuItem>
              <MenuItem value="OUTBOUND">Outbound</MenuItem>
              <MenuItem value="BLENDED">Blended</MenuItem>
            </Select>
          </FormControl>
          <FormControl fullWidth margin="normal">
            <InputLabel>Status</InputLabel>
            <Select
              value={formData.status}
              label="Status"
              onChange={(e) =>
                setFormData({ ...formData, status: e.target.value })
              }
            >
              <MenuItem value="ACTIVE">Active</MenuItem>
              <MenuItem value="PAUSED">Paused</MenuItem>
              <MenuItem value="COMPLETED">Completed</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Description"
            value={formData.description}
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
            margin="normal"
            multiline
            rows={3}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreate}>
            {formData.id ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default Campaigns
