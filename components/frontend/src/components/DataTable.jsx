import { useState } from 'react'
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  TextField,
  Box,
  IconButton,
  Chip,
} from '@mui/material'
import { Edit, Delete, Visibility } from '@mui/icons-material'

const DataTable = ({
  columns,
  data,
  onEdit,
  onDelete,
  onView,
  loading = false,
}) => {
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [orderBy, setOrderBy] = useState('')
  const [order, setOrder] = useState('asc')
  const [search, setSearch] = useState('')

  const handleChangePage = (event, newPage) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const handleRequestSort = (property) => {
    const isAsc = orderBy === property && order === 'asc'
    setOrder(isAsc ? 'desc' : 'asc')
    setOrderBy(property)
  }

  const filteredData = data.filter((row) =>
    Object.values(row).some((value) =>
      String(value).toLowerCase().includes(search.toLowerCase())
    )
  )

  const sortedData = filteredData.sort((a, b) => {
    if (!orderBy) return 0
    const aValue = a[orderBy]
    const bValue = b[orderBy]
    if (aValue < bValue) return order === 'asc' ? -1 : 1
    if (aValue > bValue) return order === 'asc' ? 1 : -1
    return 0
  })

  const paginatedData = sortedData.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  )

  const renderCell = (column, row) => {
    const value = row[column.field]

    if (column.render) {
      return column.render(value, row)
    }

    if (column.type === 'chip') {
      return <Chip label={value} size="small" color={column.color || 'default'} />
    }

    if (column.type === 'boolean') {
      return value ? 'Yes' : 'No'
    }

    return value
  }

  return (
    <Paper>
      <Box sx={{ p: 2 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Search..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </Box>

      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell key={column.field}>
                  {column.sortable ? (
                    <TableSortLabel
                      active={orderBy === column.field}
                      direction={orderBy === column.field ? order : 'asc'}
                      onClick={() => handleRequestSort(column.field)}
                    >
                      {column.headerName}
                    </TableSortLabel>
                  ) : (
                    column.headerName
                  )}
                </TableCell>
              ))}
              {(onEdit || onDelete || onView) && (
                <TableCell align="right">Actions</TableCell>
              )}
            </TableRow>
          </TableHead>

          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={columns.length + 1} align="center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : paginatedData.length === 0 ? (
              <TableRow>
                <TableCell colSpan={columns.length + 1} align="center">
                  No data available
                </TableCell>
              </TableRow>
            ) : (
              paginatedData.map((row, index) => (
                <TableRow key={row.id || index} hover>
                  {columns.map((column) => (
                    <TableCell key={column.field}>
                      {renderCell(column, row)}
                    </TableCell>
                  ))}
                  {(onEdit || onDelete || onView) && (
                    <TableCell align="right">
                      {onView && (
                        <IconButton
                          size="small"
                          onClick={() => onView(row)}
                          color="info"
                        >
                          <Visibility fontSize="small" />
                        </IconButton>
                      )}
                      {onEdit && (
                        <IconButton
                          size="small"
                          onClick={() => onEdit(row)}
                          color="primary"
                        >
                          <Edit fontSize="small" />
                        </IconButton>
                      )}
                      {onDelete && (
                        <IconButton
                          size="small"
                          onClick={() => onDelete(row)}
                          color="error"
                        >
                          <Delete fontSize="small" />
                        </IconButton>
                      )}
                    </TableCell>
                  )}
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <TablePagination
        rowsPerPageOptions={[5, 10, 25, 50]}
        component="div"
        count={filteredData.length}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Paper>
  )
}

export default DataTable
