import { useState, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material'
import { Add, Upload } from '@mui/icons-material'
import DataTable from '@components/DataTable'
import api from '@services/api'
import { toast } from 'react-toastify'

const Contacts = () => {
  const [contacts, setContacts] = useState([])
  const [loading, setLoading] = useState(false)
  const [openDialog, setOpenDialog] = useState(false)
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone_number: '',
    email: '',
    company: '',
  })

  useEffect(() => {
    fetchContacts()
  }, [])

  const fetchContacts = async () => {
    setLoading(true)
    try {
      const response = await api.get('/contacts/')
      setContacts(response.data.results || response.data)
    } catch (error) {
      toast.error('Failed to fetch contacts')
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    { field: 'first_name', headerName: 'First Name', sortable: true },
    { field: 'last_name', headerName: 'Last Name', sortable: true },
    { field: 'phone_number', headerName: 'Phone', sortable: true },
    { field: 'email', headerName: 'Email', sortable: true },
    { field: 'company', headerName: 'Company', sortable: true },
    { field: 'status', headerName: 'Status', type: 'chip', color: 'primary' },
  ]

  const handleCreate = async () => {
    try {
      await api.post('/contacts/', formData)
      toast.success('Contact created successfully')
      setOpenDialog(false)
      fetchContacts()
      setFormData({
        first_name: '',
        last_name: '',
        phone_number: '',
        email: '',
        company: '',
      })
    } catch (error) {
      toast.error('Failed to create contact')
    }
  }

  const handleEdit = (contact) => {
    setFormData(contact)
    setOpenDialog(true)
  }

  const handleDelete = async (contact) => {
    if (window.confirm(`Delete contact "${contact.first_name} ${contact.last_name}"?`)) {
      try {
        await api.delete(`/contacts/${contact.id}/`)
        toast.success('Contact deleted successfully')
        fetchContacts()
      } catch (error) {
        toast.error('Failed to delete contact')
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
        <Typography variant="h4">Contacts</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Upload />}
            sx={{ mr: 1 }}
          >
            Import
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setOpenDialog(true)}
          >
            New Contact
          </Button>
        </Box>
      </Box>

      <DataTable
        columns={columns}
        data={contacts}
        loading={loading}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />

      {/* Create/Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {formData.id ? 'Edit Contact' : 'Create Contact'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="First Name"
            value={formData.first_name}
            onChange={(e) =>
              setFormData({ ...formData, first_name: e.target.value })
            }
            margin="normal"
          />
          <TextField
            fullWidth
            label="Last Name"
            value={formData.last_name}
            onChange={(e) =>
              setFormData({ ...formData, last_name: e.target.value })
            }
            margin="normal"
          />
          <TextField
            fullWidth
            label="Phone Number"
            value={formData.phone_number}
            onChange={(e) =>
              setFormData({ ...formData, phone_number: e.target.value })
            }
            margin="normal"
          />
          <TextField
            fullWidth
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) =>
              setFormData({ ...formData, email: e.target.value })
            }
            margin="normal"
          />
          <TextField
            fullWidth
            label="Company"
            value={formData.company}
            onChange={(e) =>
              setFormData({ ...formData, company: e.target.value })
            }
            margin="normal"
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

export default Contacts
