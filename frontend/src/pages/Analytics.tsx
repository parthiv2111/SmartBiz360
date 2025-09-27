import React, { useState, useEffect } from 'react';
import { TrendingUp, Users, DollarSign, ShoppingCart, Activity } from 'lucide-react';
import StatCard from '../components/ui/StatCard';
import { analyticsAPI, dashboardAPI } from '../services/api'; // Import dashboardAPI

// --- Interface Definitions ---
interface AnalyticsData {
  total_revenue: number;
  new_customers: number;
  conversion_rate: number;
  avg_order_value: number;
  customer_satisfaction: number;
  profit_margin: number;
  avg_delivery_time: number;
}

interface TrendData {
  month: string;
  revenue?: number;
  customers?: number;
}

const Analytics: React.FC = () => {
  // --- State Management ---
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [revenueTrends, setRevenueTrends] = useState<TrendData[]>([]);
  const [customerGrowth, setCustomerGrowth] = useState<TrendData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // --- Data Fetching ---
  useEffect(() => {
    const fetchAnalyticsData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch all data concurrently for better performance
        const [overviewRes, revenueRes, customerRes] = await Promise.all([
          analyticsAPI.getOverview(),
          dashboardAPI.getRevenueTrends(),
          dashboardAPI.getCustomerGrowth(),
        ]);

        if (overviewRes.success) {
          setAnalyticsData(overviewRes.data);
        } else {
          throw new Error('Failed to fetch overview data');
        }

        if (revenueRes.success) {
          setRevenueTrends(revenueRes.data);
        } else {
          throw new Error('Failed to fetch revenue trends');
        }

        if (customerRes.success) {
          setCustomerGrowth(customerRes.data);
        } else {
          throw new Error('Failed to fetch customer growth');
        }

      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalyticsData();
  }, []);

  // --- Render Logic ---

  // Loading state
  if (loading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600">Loading analytics data...</p>
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
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-red-600">Error: {error}</p>
        </div>
      </div>
    );
  }

  // No data state
  if (!analyticsData) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600">No analytics data available</p>
        </div>
      </div>
    );
  }
  
  // Data for Stat Cards
  const stats = [
    {
      title: 'Total Revenue',
      value: `$${(Number(analyticsData.total_revenue) || 0).toLocaleString()}`,
      change: '+12.5%', // Note: This change value is still a placeholder
      changeType: 'positive' as const,
      iconColor: 'text-success-600',
      iconBgColor: 'bg-success-50'
    },
    {
      title: 'New Customers',
      value: (Number(analyticsData.new_customers) || 0).toLocaleString(),
      change: '+8.2%', // Note: This change value is still a placeholder
      changeType: 'positive' as const,
      iconColor: 'text-primary-600',
      iconBgColor: 'bg-primary-50'
    },
    {
      title: 'Conversion Rate',
      value: `${Number(analyticsData.conversion_rate) || 0}%`,
      change: '+0.8%', // Note: This change value is still a placeholder
      changeType: 'positive' as const,
      iconColor: 'text-warning-600',
      iconBgColor: 'bg-warning-50'
    },
    {
      title: 'Avg Order Value',
      value: `$${(Number(analyticsData.avg_order_value) || 0).toFixed(2)}`,
      change: '+2.1%', // Note: This change value is still a placeholder
      changeType: 'positive' as const,
      iconColor: 'text-secondary-600',
      iconBgColor: 'bg-secondary-50'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600">Track your business performance and insights</p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          let Icon;
          switch (stat.title) {
            case 'Total Revenue': Icon = DollarSign; break;
            case 'New Customers': Icon = Users; break;
            case 'Conversion Rate': Icon = TrendingUp; break;
            case 'Avg Order Value': Icon = ShoppingCart; break;
            default: Icon = Activity;
          }
          return <StatCard key={index} {...stat} icon={Icon} />;
        })}
      </div>

      {/* Charts section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Chart */}
        <div className="card">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Revenue Trends</h3>
            <p className="text-sm text-gray-600">Monthly revenue performance</p>
          </div>
          <div className="p-6">
            <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
              {/* TODO: Pass 'revenueTrends' data to a chart component */}
              <p className="text-gray-500">Revenue chart placeholder</p>
            </div>
          </div>
        </div>

        {/* Customer Growth Chart */}
        <div className="card">
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Customer Growth</h3>
            <p className="text-sm text-gray-600">New customer acquisition</p>
          </div>
          <div className="p-6">
            <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
              {/* TODO: Pass 'customerGrowth' data to a chart component */}
              <p className="text-gray-500">Customer growth chart placeholder</p>
            </div>
          </div>
        </div>
      </div>

      {/* Additional Analytics (now using live data) */}
      <div className="card">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Performance Metrics</h3>
          <p className="text-sm text-gray-600">Key performance indicators</p>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-600">{analyticsData.customer_satisfaction}%</div>
              <div className="text-sm text-gray-600 mt-1">Customer Satisfaction</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-success-600">{analyticsData.profit_margin}%</div>
              <div className="text-sm text-gray-600 mt-1">Profit Margin</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-warning-600">{analyticsData.avg_delivery_time} days</div>
              <div className="text-sm text-gray-600 mt-1">Avg Delivery Time</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;