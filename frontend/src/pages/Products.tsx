import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Search, Filter, Download, Upload, Pencil, Trash2, X } from 'lucide-react';
import DataTable from '../components/ui/DataTable';
import { productsAPI, exportImportAPI, uploadAPI } from '../services/api';
import { useApp } from '../contexts/AppContext';

// --- Interface Definitions ---
interface Product {
  id: string;
  name: string;
  sku: string;
  category: string;
  price: number;
  stock: number;
  status: string;
  image?: string;
  description?: string;
}

interface PaginationState {
  currentPage: number;
  totalItems: number;
  pageSize: number;
}

// --- Component ---
const Products: React.FC = () => {
  const { addNotification } = useApp();
  
  // Data and Loading State
  const [products, setProducts] = useState<Product[]>([]);
  const [pagination, setPagination] = useState<PaginationState>({ currentPage: 1, totalItems: 0, pageSize: 10 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // UI State
  const [searchQuery, setSearchQuery] = useState('');
  const [sortColumn, setSortColumn] = useState<string>('created_at');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [productImageFile, setProductImageFile] = useState<File | null>(null);

  // --- Data Fetching ---
  const fetchProducts = useCallback(async () => {
    try {
      setLoading(true);
      const response = await productsAPI.getAll({
        page: pagination.currentPage,
        per_page: pagination.pageSize,
        search: searchQuery,
        // Add sorting params here when backend supports it
      });
      
      if (response.success) {
        setProducts(response.data);
        setPagination(prev => ({ ...prev, totalItems: response.pagination.total }));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred fetching products');
    } finally {
      setLoading(false);
    }
  }, [pagination.currentPage, pagination.pageSize, searchQuery]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  // --- Event Handlers ---
  const handleSort = (column: string, direction: 'asc' | 'desc') => {
    setSortColumn(column);
    setSortDirection(direction);
    // Refetch data with new sort parameters
  };

  const handleDelete = async (productId: string) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await productsAPI.delete(productId);
        addNotification('success', 'Product deleted successfully');
        fetchProducts(); // Refresh data
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete product');
        addNotification('error', 'Failed to delete product');
      }
    }
  };

  const handleExport = async () => {
    try {
      const blob = await exportImportAPI.exportProducts('csv');
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `products_export_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      addNotification('success', 'Products exported successfully');
    } catch (err) {
      addNotification('error', 'Failed to export products');
    }
  };

  const handleOpenModal = (product: Product | null = null) => {
    setEditingProduct(product);
    setProductImageFile(null);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingProduct(null);
  };

  const handleFormSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    const formData = new FormData(event.currentTarget);
    const productData = Object.fromEntries(formData.entries());
    
    try {
      let imageUrl = editingProduct?.image || '';
      // If a new image file is selected, upload it first
      if (productImageFile) {
        const uploadResponse = await uploadAPI.uploadProductImage(productImageFile);
        if (uploadResponse.success) {
          imageUrl = uploadResponse.data.image_url;
        } else {
          throw new Error('Image upload failed');
        }
      }
      
      const finalProductData = { ...productData, image: imageUrl };

      if (editingProduct) {
        await productsAPI.update(editingProduct.id, finalProductData);
        addNotification('success', 'Product updated successfully');
      } else {
        await productsAPI.create(finalProductData);
        addNotification('success', 'Product created successfully');
      }
      handleCloseModal();
      fetchProducts(); // Refresh data
    } catch (err) {
      addNotification('error', err instanceof Error ? err.message : 'Failed to save product');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // --- Column Definitions ---
  const columns = [
    { key: 'name', label: 'Product', sortable: true, render: (value: string, row: Product) => (
        <div className="flex items-center space-x-3">
          <img src={row.image ? uploadAPI.getFileUrl(row.image.split('/').pop()!) : `https://via.placeholder.com/40`} alt={value} className="w-10 h-10 rounded-lg object-cover" />
          <div>
            <div className="font-medium text-gray-900">{value}</div>
            <div className="text-sm text-gray-500">SKU: {row.sku}</div>
          </div>
        </div>
    )},
    { key: 'category', label: 'Category', sortable: true },
    { key: 'price', label: 'Price', sortable: true, render: (value: number) => `$${(Number(value) || 0).toFixed(2)}` },
    { key: 'stock', label: 'Stock', sortable: true },
    { key: 'status', label: 'Status', sortable: true, render: (value: string) => (
        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${ value === 'In Stock' ? 'bg-success-100 text-success-800' : value === 'Low Stock' ? 'bg-warning-100 text-warning-800' : 'bg-error-100 text-error-800' }`}>
          {value}
        </span>
    )},
    { key: 'actions', label: 'Actions', render: (_: any, row: Product) => (
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
          <h1 className="text-2xl font-bold text-gray-900">Products</h1>
          <p className="text-gray-600">Manage your product catalog</p>
        </div>
        <div className="mt-4 sm:mt-0 flex space-x-2">
          <button onClick={handleExport} className="btn-secondary flex items-center"><Download className="w-4 h-4 mr-2" />Export</button>
          <button onClick={() => handleOpenModal()} className="btn-primary flex items-center"><Plus className="w-4 h-4 mr-2" />Add Product</button>
        </div>
      </div>
      
      {/* Products table */}
      <DataTable
        columns={columns}
        data={products}
        currentPage={pagination.currentPage}
        totalItems={pagination.totalItems}
        pageSize={pagination.pageSize}
        onPageChange={(page) => setPagination(p => ({...p, currentPage: page}))}
        onSort={handleSort}
        sortColumn={sortColumn}
        sortDirection={sortDirection}
        loading={loading}
      />

      {/* Add/Edit Product Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="card w-full max-w-lg">
            <div className="flex justify-between items-center p-4 border-b">
              <h3 className="text-lg font-semibold">{editingProduct ? 'Edit Product' : 'Add New Product'}</h3>
              <button onClick={handleCloseModal}><X size={20}/></button>
            </div>
            <form onSubmit={handleFormSubmit} className="p-4 grid grid-cols-2 gap-4">
              <div className="col-span-2"><input name="name" defaultValue={editingProduct?.name} placeholder="Product Name" className="input-field" required /></div>
              <div><input name="sku" defaultValue={editingProduct?.sku} placeholder="SKU" className="input-field" required /></div>
              <div><input name="category" defaultValue={editingProduct?.category} placeholder="Category" className="input-field" required /></div>
              <div><input name="price" type="number" step="0.01" defaultValue={editingProduct?.price} placeholder="Price" className="input-field" required /></div>
              <div><input name="stock" type="number" defaultValue={editingProduct?.stock} placeholder="Stock" className="input-field" required /></div>
              <div className="col-span-2"><textarea name="description" defaultValue={editingProduct?.description} placeholder="Description" className="input-field min-h-[80px]"></textarea></div>
              <div className="col-span-2"><label className="block text-sm font-medium text-gray-700">Product Image</label><input type="file" accept="image/*" onChange={(e) => setProductImageFile(e.target.files ? e.target.files[0] : null)} className="input-field mt-1"/></div>
              <div className="col-span-2 flex justify-end space-x-2 pt-2">
                <button type="button" onClick={handleCloseModal} className="btn-secondary">Cancel</button>
                <button type="submit" className="btn-primary" disabled={isSubmitting}>
                  {isSubmitting ? 'Saving...' : 'Save Product'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Products;