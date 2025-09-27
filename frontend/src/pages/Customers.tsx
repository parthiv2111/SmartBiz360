import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Search, Filter, Download, Users, Pencil, Trash2, X } from 'lucide-react';
import DataTable from '../components/ui/DataTable';
import { customersAPI, exportImportAPI } from '../services/api';
import LoadingSpinner from '../components/ui/LoadingSpinner';

// --- Interface Definitions ---
interface Customer {
  id: string;
  name: string;
  email: string;
  company?: string;
  phone?: string;
  status: 'Active' | 'Inactive';
  join_date: string;
  total_orders?: number;
  total_spent?: number;
}

interface PaginationState {
  currentPage: number;
  totalItems: number;
  pageSize: number;
}

const Customers: React.FC = () => {
  // --- State Management ---
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [pagination, setPagination] = useState<PaginationState>({ currentPage: 1, totalItems: 0, pageSize: 10 });
  const [searchQuery, setSearchQuery] = useState('');
  const [sortColumn, setSortColumn] = useState<string>('join_date');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal and Form State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState<Customer | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // --- Data Fetching ---
  const fetchCustomers = useCallback(async () => {
    try {
      setLoading(true);
      const response = await customersAPI.getAll({
        page: pagination.currentPage,
        per_page: pagination.pageSize,
        search: searchQuery,
        // Note: Add sort_by and sort_direction to your backend API if available
      });
      
      if (response.success) {
        setCustomers(response.data);
        setPagination(prev => ({ ...prev, totalItems: response.pagination.total }));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred fetching customers');
    } finally {
      setLoading(false);
    }
  }, [pagination.currentPage, pagination.pageSize, searchQuery]);

  useEffect(() => {
    fetchCustomers();
  }, [fetchCustomers]);

  // --- Event Handlers ---
  const handleSort = (column: string, direction: 'asc' | 'desc') => {
    setSortColumn(column);
    setSortDirection(direction);
    // In a real scenario, you would refetch the data with sort parameters
    // For now, we'll sort the client-side data as a fallback
    setCustomers(prev => [...prev].sort((a, b) => {
      // Basic sort, can be enhanced
      if (a[column] < b[column]) return direction === 'asc' ? -1 : 1;
      if (a[column] > b[column]) return direction === 'asc' ? 1 : -1;
      return 0;
    }));
  };

  const handleDelete = async (customerId: string) => {
    if (window.confirm('Are you sure you want to delete this customer?')) {
      try {
        await customersAPI.delete(customerId);
        fetchCustomers(); // Refresh data after delete
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete customer');
      }
    }
  };

  const handleExport = async () => {
    try {
      const blob = await exportImportAPI.exportCustomers('csv');
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `customers_export_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export customers');
    }
  };
  
  const handleOpenModal = (customer: Customer | null = null) => {
    setEditingCustomer(customer);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingCustomer(null);
  };

  const handleFormSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    const formData = new FormData(event.currentTarget);
    const customerData = Object.fromEntries(formData.entries());

    try {
      if (editingCustomer) {
        // Update existing customer
        await customersAPI.update(editingCustomer.id, customerData);
      } else {
        // Create new customer
        await customersAPI.create(customerData);
      }
      handleCloseModal();
      fetchCustomers(); // Refresh data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save customer');
    } finally {
      setIsSubmitting(false);
    }
  };

  // --- Column Definitions for DataTable ---
  const columns = [
    { key: 'name', label: 'Customer Name', sortable: true, render: (value: string, row: Customer) => (
        <div>
          <div className="font-medium text-gray-900">{row.name}</div>
          <div className="text-sm text-gray-500">{row.company}</div>
        </div>
    )},
    { key: 'email', label: 'Contact', sortable: true, render: (value: string, row: Customer) => (
        <div>
          <div className="text-sm text-gray-900">{row.email}</div>
          <div className="text-sm text-gray-500">{row.phone}</div>
        </div>
    )},
    { key: 'status', label: 'Status', sortable: true, render: (value: string) => (
        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${ value === 'Active' ? 'bg-success-100 text-success-800' : 'bg-gray-100 text-gray-800' }`}>
          {value}
        </span>
    )},
    { key: 'total_spent', label: 'Total Spent', sortable: true, render: (value: number) => (
        <span className="font-medium">${(Number(value) || 0).toFixed(2)}</span>
    )},
    { key: 'actions', label: 'Actions', render: (_: any, row: Customer) => (
        <div className="flex space-x-2">
            <button onClick={() => handleOpenModal(row)} className="p-1 hover:text-blue-600"><Pencil size={16}/></button>
            <button onClick={() => handleDelete(row.id)} className="p-1 hover:text-red-600"><Trash2 size={16}/></button>
        </div>
    )}
  ];

  if (error) return <div className="text-red-500">Error: {error}</div>;

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Customers</h1>
          <p className="text-gray-600">Manage your customer relationships</p>
        </div>
        <div className="mt-4 sm:mt-0">
          <button onClick={() => handleOpenModal()} className="btn-primary flex items-center">
            <Plus className="w-4 h-4 mr-2" />
            Add Customer
          </button>
        </div>
      </div>

      {/* Filters and search */}
      <div className="card p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input type="text" placeholder="Search customers..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="input-field pl-10"/>
            </div>
          </div>
          <div className="flex gap-2">
            <button onClick={handleExport} className="btn-secondary flex items-center">
              <Download className="w-4 h-4 mr-2" />
              Export
            </button>
          </div>
        </div>
      </div>

      {/* Customers table */}
      <DataTable
        columns={columns}
        data={customers}
        currentPage={pagination.currentPage}
        totalItems={pagination.totalItems}
        pageSize={pagination.pageSize}
        onPageChange={(page) => setPagination(p => ({...p, currentPage: page}))}
        onSort={handleSort}
        sortColumn={sortColumn}
        sortDirection={sortDirection}
        loading={loading}
      />
      
      {/* Add/Edit Customer Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="card w-full max-w-md">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-lg font-semibold">{editingCustomer ? 'Edit Customer' : 'Add New Customer'}</h3>
              <button onClick={handleCloseModal}><X size={20}/></button>
            </div>
            <form onSubmit={handleFormSubmit} className="p-4 space-y-4">
              <input name="name" defaultValue={editingCustomer?.name} placeholder="Name" className="input-field" required />
              <input name="email" type="email" defaultValue={editingCustomer?.email} placeholder="Email" className="input-field" required />
              <input name="company" defaultValue={editingCustomer?.company} placeholder="Company" className="input-field" />
              <input name="phone" defaultValue={editingCustomer?.phone} placeholder="Phone" className="input-field" />
              <select name="status" defaultValue={editingCustomer?.status || 'Active'} className="input-field">
                <option value="Active">Active</option>
                <option value="Inactive">Inactive</option>
              </select>
              <div className="flex justify-end space-x-2 pt-2">
                <button type="button" onClick={handleCloseModal} className="btn-secondary">Cancel</button>
                <button type="submit" className="btn-primary" disabled={isSubmitting}>
                  {isSubmitting ? 'Saving...' : 'Save Customer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Customers;