import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  Users, 
  DollarSign, 
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  Play,
  Pause,
  RotateCcw,
  Target,
  Zap,
  Shield
} from 'lucide-react';

const Dashboard: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRunning && progress < 100) {
      interval = setInterval(() => {
        setProgress(prev => Math.min(prev + 1, 100));
      }, 100);
    }
    return () => clearInterval(interval);
  }, [isRunning, progress]);

  const stats = [
    {
      title: 'کل کاربران',
      value: '12,847',
      change: '+12.5%',
      changeType: 'increase',
      icon: Users,
      color: 'primary'
    },
    {
      title: 'درآمد کل',
      value: '$45,231',
      change: '+8.2%',
      changeType: 'increase',
      icon: DollarSign,
      color: 'secondary'
    },
    {
      title: 'عملکرد سیستم',
      value: '98.5%',
      change: '+2.1%',
      changeType: 'increase',
      icon: Activity,
      color: 'green'
    },
    {
      title: 'ترافیک',
      value: '2.3M',
      change: '-1.2%',
      changeType: 'decrease',
      icon: TrendingUp,
      color: 'orange'
    }
  ];

  const recentActivities = [
    { id: 1, action: 'کاربر جدید ثبت نام کرد', time: '2 دقیقه پیش', type: 'user' },
    { id: 2, action: 'سیستم به‌روزرسانی شد', time: '5 دقیقه پیش', type: 'system' },
    { id: 3, action: 'پرداخت جدید دریافت شد', time: '10 دقیقه پیش', type: 'payment' },
    { id: 4, action: 'گزارش جدید تولید شد', time: '15 دقیقه پیش', type: 'report' },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">داشبورد</h1>
          <p className="text-gray-600 dark:text-gray-400">خوش آمدید به سیستم جامع ERFANR</p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setIsRunning(!isRunning)}
            className={`btn-primary flex items-center space-x-2 ${isRunning ? 'bg-red-600 hover:bg-red-700' : ''}`}
          >
            {isRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            <span>{isRunning ? 'توقف' : 'شروع'}</span>
          </button>
          <button
            onClick={() => setProgress(0)}
            className="btn-secondary flex items-center space-x-2"
          >
            <RotateCcw className="w-4 h-4" />
            <span>ریست</span>
          </button>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={index}
              variants={itemVariants}
              className="card hover:shadow-xl transition-shadow duration-300"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {stat.title}
                  </p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {stat.value}
                  </p>
                </div>
                <div className={`p-3 rounded-lg bg-${stat.color}-100 dark:bg-${stat.color}-900/20`}>
                  <Icon className={`w-6 h-6 text-${stat.color}-600`} />
                </div>
              </div>
              <div className="flex items-center mt-4">
                {stat.changeType === 'increase' ? (
                  <ArrowUpRight className="w-4 h-4 text-green-500" />
                ) : (
                  <ArrowDownRight className="w-4 h-4 text-red-500" />
                )}
                <span className={`text-sm font-medium ${
                  stat.changeType === 'increase' ? 'text-green-600' : 'text-red-600'
                }`}>
                  {stat.change}
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400 ml-2">
                  از ماه گذشته
                </span>
              </div>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Progress Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        {/* Progress Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              پیشرفت سیستم
            </h3>
            <Target className="w-5 h-5 text-primary-600" />
          </div>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600 dark:text-gray-400">پیشرفت کلی</span>
                <span className="font-medium text-gray-900 dark:text-white">{progress}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <motion.div
                  className="bg-gradient-to-r from-primary-500 to-secondary-500 h-2 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <Zap className="w-6 h-6 text-yellow-500 mx-auto mb-2" />
                <p className="text-sm text-gray-600 dark:text-gray-400">عملکرد</p>
                <p className="text-lg font-bold text-gray-900 dark:text-white">98%</p>
              </div>
              <div className="text-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <Shield className="w-6 h-6 text-green-500 mx-auto mb-2" />
                <p className="text-sm text-gray-600 dark:text-gray-400">امنیت</p>
                <p className="text-lg font-bold text-gray-900 dark:text-white">99%</p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activities */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            فعالیت‌های اخیر
          </h3>
          <div className="space-y-3">
            {recentActivities.map((activity) => (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
              >
                <div className={`w-2 h-2 rounded-full ${
                  activity.type === 'user' ? 'bg-blue-500' :
                  activity.type === 'system' ? 'bg-green-500' :
                  activity.type === 'payment' ? 'bg-yellow-500' : 'bg-purple-500'
                }`} />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {activity.action}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {activity.time}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;