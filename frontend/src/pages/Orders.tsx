import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Search, Filter, Download, ShoppingCart } from 'lucide-react';
import DataTable from '../components/ui/DataTable';
import { ordersAPI, exportImportAPI } from '../services/api';
import { useApp } from '../contexts/AppContext';

// --- Interface Definitions ---
interface Order {
  id: string;
  order_number: string;
  customer: string;
  products: string;
  total: number;
  status: string;
  date: string;
  payment: string;
}

interface OrderStats {
  total_orders: number;
  completed: number;
  processing: number;
  shipped: number;
  pending: number;
  cancelled: number;
}

// --- Component ---
const Orders: React.FC = () => {
  const { addNotification } = useApp();
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortColumn, setSortColumn] = useState<string>('date');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [orders, setOrders] = useState<Order[]>([]);
  const [stats, setStats] = useState<OrderStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalItems, setTotalItems] = useState(0);
  const [pageSize] = useState(10);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const [ordersResponse, statsResponse] = await Promise.all([
          ordersAPI.getAll({ page: currentPage, per_page: pageSize, search: searchQuery }),
          ordersAPI.getStats()
        ]);
        
        if (ordersResponse.success) {
          setOrders(ordersResponse.data);
          setTotalItems(ordersResponse.pagination.total);
        }
        
        if (statsResponse.success) {
          setStats(statsResponse.data);
        }
        
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [currentPage, searchQuery, pageSize]);

  const handleSort = (column: string, direction: 'asc' | 'desc') => {
    setSortColumn(column);
    setSortDirection(direction);
  };

  const handleExport = async () => {
    try {
      const blob = await exportImportAPI.exportOrders('csv');
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `orders_export_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      addNotification('success', 'Orders exported successfully');
    } catch (err) {
      addNotification('error', 'Failed to export orders');
    }
  };

  const columns = [
    { key: 'order_number', label: 'Order ID', sortable: true, render: (value: string) => <span className="font-mono font-medium text-primary-600">{value}</span> },
    { key: 'customer', label: 'Customer', sortable: true },
    { key: 'total', label: 'Total', sortable: true, render: (value: number) => `$${(Number(value) || 0).toFixed(2)}` },
    { key: 'status', label: 'Status', sortable: true, render: (value: string) => {
        const statusConfig = {
          'Completed': 'bg-success-100 text-success-800', 'Processing': 'bg-warning-100 text-warning-800',
          'Shipped': 'bg-primary-100 text-primary-800', 'Pending': 'bg-gray-100 text-gray-800',
          'Cancelled': 'bg-error-100 text-error-800'
        };
        return <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${statusConfig[value as keyof typeof statusConfig] || 'bg-gray-100 text-gray-800'}`}>{value}</span>;
    }},
    { key: 'date', label: 'Date', sortable: true, render: (value: string) => new Date(value).toLocaleDateString() },
    { key: 'payment', label: 'Payment', sortable: true }
  ];

  if (error) return <div className="text-red-500">Error: {error}</div>;

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Orders</h1>
          <p className="text-gray-600">Manage customer orders and fulfillment</p>
        </div>
        <div className="mt-4 sm:mt-0 flex space-x-2">
          <button onClick={handleExport} className="btn-secondary flex items-center"><Download className="w-4 h-4 mr-2" />Export</button>
          <button className="btn-primary flex items-center"><Plus className="w-4 h-4 mr-2" />Create Order</button>
        </div>
      </div>

      {/* Stats cards - NOW USES 'stats' STATE FROM API */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <div className="card p-6"><div className="flex items-center"><div className="p-2 bg-primary-100 rounded-lg"><ShoppingCart className="w-6 h-6 text-primary-600"/></div><div className="ml-4"><p className="text-sm font-medium text-gray-600">Total Orders</p><p className="text-2xl font-bold text-gray-900">{loading ? '...' : stats?.total_orders || 0}</p></div></div></div>
        <div className="card p-6"><div className="flex items-center"><div className="p-2 bg-success-100 rounded-lg"><ShoppingCart className="w-6 h-6 text-success-600"/></div><div className="ml-4"><p className="text-sm font-medium text-gray-600">Completed</p><p className="text-2xl font-bold text-gray-900">{loading ? '...' : stats?.completed || 0}</p></div></div></div>
        <div className="card p-6"><div className="flex items-center"><div className="p-2 bg-warning-100 rounded-lg"><ShoppingCart className="w-6 h-6 text-warning-600"/></div><div className="ml-4"><p className="text-sm font-medium text-gray-600">Processing</p><p className="text-2xl font-bold text-gray-900">{loading ? '...' : stats?.processing || 0}</p></div></div></div>
        <div className="card p-6"><div className="flex items-center"><div className="p-2 bg-primary-100 rounded-lg"><ShoppingCart className="w-6 h-6 text-primary-600"/></div><div className="ml-4"><p className="text-sm font-medium text-gray-600">Shipped</p><p className="text-2xl font-bold text-gray-900">{loading ? '...' : stats?.shipped || 0}</p></div></div></div>
        <div className="card p-6"><div className="flex items-center"><div className="p-2 bg-gray-100 rounded-lg"><ShoppingCart className="w-6 h-6 text-gray-600"/></div><div className="ml-4"><p className="text-sm font-medium text-gray-600">Pending</p><p className="text-2xl font-bold text-gray-900">{loading ? '...' : stats?.pending || 0}</p></div></div></div>
      </div>
      
      {/* Orders table */}
      <DataTable
        columns={columns}
        data={orders}
        currentPage={currentPage}
        totalItems={totalItems}
        pageSize={pageSize}
        onPageChange={setCurrentPage}
        onSort={handleSort}
        sortColumn={sortColumn}
        sortDirection={sortDirection}
        loading={loading}
      />
    </div>
  );
};

export default Orders;