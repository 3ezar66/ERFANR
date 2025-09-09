import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown,
  Calendar,
  Filter,
  Download,
  Eye,
  EyeOff
} from 'lucide-react';

const Analytics: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('week');
  const [showData, setShowData] = useState(true);

  const chartData = [
    { month: 'فروردین', users: 1200, revenue: 45000, growth: 12 },
    { month: 'اردیبهشت', users: 1350, revenue: 52000, growth: 8 },
    { month: 'خرداد', users: 1100, revenue: 48000, growth: -5 },
    { month: 'تیر', users: 1600, revenue: 61000, growth: 15 },
    { month: 'مرداد', users: 1800, revenue: 68000, growth: 12 },
    { month: 'شهریور', users: 2100, revenue: 75000, growth: 17 },
  ];

  const metrics = [
    {
      title: 'کاربران فعال',
      value: '2,847',
      change: '+12.5%',
      trend: 'up',
      color: 'primary'
    },
    {
      title: 'درآمد ماهانه',
      value: '$75,420',
      change: '+8.2%',
      trend: 'up',
      color: 'secondary'
    },
    {
      title: 'نرخ تبدیل',
      value: '3.2%',
      change: '-1.1%',
      trend: 'down',
      color: 'orange'
    },
    {
      title: 'زمان پاسخ',
      value: '2.4s',
      change: '+0.3s',
      trend: 'down',
      color: 'red'
    }
  ];

  const topProducts = [
    { name: 'محصول A', sales: 1250, revenue: 45000, growth: 15 },
    { name: 'محصول B', sales: 980, revenue: 32000, growth: 8 },
    { name: 'محصول C', sales: 750, revenue: 28000, growth: -2 },
    { name: 'محصول D', sales: 620, revenue: 22000, growth: 12 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">تحلیل‌ها</h1>
          <p className="text-gray-600 dark:text-gray-400">بررسی عملکرد و آمار سیستم</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowData(!showData)}
            className="btn-secondary flex items-center space-x-2"
          >
            {showData ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            <span>{showData ? 'مخفی کردن' : 'نمایش'}</span>
          </button>
          <button className="btn-primary flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>دانلود گزارش</span>
          </button>
        </div>
      </motion.div>

      {/* Period Selector */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">انتخاب دوره</h3>
          <Filter className="w-5 h-5 text-gray-500" />
        </div>
        <div className="flex space-x-2">
          {['week', 'month', 'quarter', 'year'].map((period) => (
            <button
              key={period}
              onClick={() => setSelectedPeriod(period)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedPeriod === period
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {period === 'week' && 'هفته'}
              {period === 'month' && 'ماه'}
              {period === 'quarter' && 'فصل'}
              {period === 'year' && 'سال'}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Metrics Grid */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {metrics.map((metric, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card hover:shadow-xl transition-shadow duration-300"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                  {metric.title}
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {metric.value}
                </p>
              </div>
              <div className={`p-3 rounded-lg bg-${metric.color}-100 dark:bg-${metric.color}-900/20`}>
                {metric.trend === 'up' ? (
                  <TrendingUp className={`w-6 h-6 text-${metric.color}-600`} />
                ) : (
                  <TrendingDown className={`w-6 h-6 text-${metric.color}-600`} />
                )}
              </div>
            </div>
            <div className="flex items-center mt-4">
              <span className={`text-sm font-medium ${
                metric.trend === 'up' ? 'text-green-600' : 'text-red-600'
              }`}>
                {metric.change}
              </span>
              <span className="text-sm text-gray-500 dark:text-gray-400 ml-2">
                از دوره قبل
              </span>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Chart Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        {/* Chart */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">روند رشد</h3>
            <BarChart3 className="w-5 h-5 text-primary-600" />
          </div>
          <div className="space-y-4">
            {chartData.map((data, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
                  <span className="font-medium text-gray-900 dark:text-white">{data.month}</span>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm text-gray-600 dark:text-gray-400">کاربران</p>
                    <p className="font-semibold text-gray-900 dark:text-white">{data.users.toLocaleString()}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600 dark:text-gray-400">درآمد</p>
                    <p className="font-semibold text-gray-900 dark:text-white">${data.revenue.toLocaleString()}</p>
                  </div>
                  <div className={`text-right ${data.growth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    <p className="text-sm">رشد</p>
                    <p className="font-semibold">{data.growth >= 0 ? '+' : ''}{data.growth}%</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Top Products */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">محصولات برتر</h3>
            <TrendingUp className="w-5 h-5 text-secondary-600" />
          </div>
          <div className="space-y-4">
            {topProducts.map((product, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                    index === 0 ? 'bg-yellow-100 dark:bg-yellow-900/20' :
                    index === 1 ? 'bg-gray-100 dark:bg-gray-700' :
                    index === 2 ? 'bg-orange-100 dark:bg-orange-900/20' : 'bg-blue-100 dark:bg-blue-900/20'
                  }`}>
                    <span className={`text-sm font-bold ${
                      index === 0 ? 'text-yellow-600' :
                      index === 1 ? 'text-gray-600' :
                      index === 2 ? 'text-orange-600' : 'text-blue-600'
                    }`}>
                      {index + 1}
                    </span>
                  </div>
                  <span className="font-medium text-gray-900 dark:text-white">{product.name}</span>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm text-gray-600 dark:text-gray-400">فروش</p>
                    <p className="font-semibold text-gray-900 dark:text-white">{product.sales.toLocaleString()}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600 dark:text-gray-400">درآمد</p>
                    <p className="font-semibold text-gray-900 dark:text-white">${product.revenue.toLocaleString()}</p>
                  </div>
                  <div className={`text-right ${product.growth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    <p className="text-sm">رشد</p>
                    <p className="font-semibold">{product.growth >= 0 ? '+' : ''}{product.growth}%</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Analytics;