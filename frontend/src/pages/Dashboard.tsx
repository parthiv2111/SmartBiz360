import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Package, 
  DollarSign, 
  ShoppingCart,
  Activity
} from 'lucide-react';
import StatCard from '../components/ui/StatCard';
import { dashboardAPI } from '../services/api';

// --- Interface Definitions ---
interface DashboardData {
  stats: Array<{
    title: string;
    value: string;
    change: string;
    changeType: 'positive' | 'negative';
    iconColor: string;
    iconBgColor: string;
  }>;
  recent_orders: Array<{
    id: string;
    customer: string;
    product: string;
    amount: string;
    status: string;
  }>;
  top_products: Array<{
    name: string;
    sales: number;
    revenue: string;
  }>;
}

interface TrendData {
  month: string;
  revenue: number;
}

const Dashboard: React.FC = () => {
  // --- State Management ---
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [revenueData, setRevenueData] = useState<TrendData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // --- Data Fetching ---
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch stats and revenue data at the same time
        const [statsResponse, revenueResponse] = await Promise.all([
          dashboardAPI.getStats(),
          dashboardAPI.getRevenueTrends()
        ]);

        if (statsResponse.success) {
          setDashboardData(statsResponse.data);
        } else {
          throw new Error('Failed to fetch dashboard stats');
        }

        if (revenueResponse.success) {
          setRevenueData(revenueResponse.data);
        } else {
          throw new Error('Failed to fetch revenue trends');
        }

      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // --- Render Logic ---

  // Loading state
  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Loading dashboard data...</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="h-20 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-red-600">Error: {error}</p>
        </div>
      </div>
    );
  }

  // Default data if API fails
  if (!dashboardData) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">No data available</p>
        </div>
      </div>
    );
  }

  const { stats, recent_orders, top_products } = dashboardData;

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Welcome back! Here's what's happening with your business today.</p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          let Icon;
          switch (stat.title) {
            case 'Total Revenue': Icon = DollarSign; break;
            case 'Active Customers': Icon = Users; break;
            case 'Products Sold': Icon = Package; break;
            case 'Pending Orders': Icon = ShoppingCart; break;
            default: Icon = Activity;
          }
          return <StatCard key={index} {...stat} icon={Icon} />;
        })}
      </div>

      {/* Charts and tables section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Orders */}
        <div className="card">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Recent Orders</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {recent_orders.map((order) => (
                <div key={order.id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-primary-600 rounded-full"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{order.customer}</p>
                      <p className="text-xs text-gray-500">{order.product}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">{order.amount}</p>
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                      order.status === 'Completed' ? 'bg-success-100 text-success-800' :
                      order.status === 'Processing' ? 'bg-warning-100 text-warning-800' :
                      order.status === 'Shipped' ? 'bg-primary-100 text-primary-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {order.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Top Products */}
        <div className="card">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Top Products</h3>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {top_products.map((product, index) => (
                <div key={product.name} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                      <span className="text-primary-600 font-medium text-sm">{index + 1}</span>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{product.name}</p>
                      <p className="text-xs text-gray-500">{product.sales} sales</p>
                    </div>
                  </div>
                  <p className="text-sm font-medium text-gray-900">{product.revenue}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Revenue Chart */}
      <div className="card">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Revenue Overview</h3>
          <p className="text-sm text-gray-600">Monthly revenue performance</p>
        </div>
        <div className="p-6">
          <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
            {/* This is where you would integrate a charting library like Recharts or Chart.js.
              You would pass the 'revenueData' state variable to it as a prop.
              For example: <MyChartComponent data={revenueData} />
            */}
            <div className="text-center">
              <Activity className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-500">Revenue chart placeholder</p>
              <p className="text-sm text-gray-400">(Data is fetched and ready in the 'revenueData' state)</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;