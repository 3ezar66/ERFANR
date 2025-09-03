import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Settings, 
  Bell, 
  Shield, 
  Palette, 
  Globe, 
  Database,
  Save,
  RotateCcw,
  Eye,
  EyeOff,
  Lock,
  User,
  Mail,
  Phone
} from 'lucide-react';

const SettingsPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState('general');
  const [notifications, setNotifications] = useState({
    email: true,
    push: false,
    sms: true,
    marketing: false
  });
  const [privacy, setPrivacy] = useState({
    profile: 'public',
    data: 'private',
    analytics: true
  });
  const [showPassword, setShowPassword] = useState(false);

  const tabs = [
    { id: 'general', label: 'عمومی', icon: Settings },
    { id: 'notifications', label: 'اعلان‌ها', icon: Bell },
    { id: 'privacy', label: 'حریم خصوصی', icon: Shield },
    { id: 'appearance', label: 'ظاهر', icon: Palette },
    { id: 'language', label: 'زبان', icon: Globe },
    { id: 'data', label: 'داده‌ها', icon: Database },
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'general':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  نام کامل
                </label>
                <input
                  type="text"
                  defaultValue="احمد محمدی"
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  نام کاربری
                </label>
                <input
                  type="text"
                  defaultValue="ahmad_mohammadi"
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  ایمیل
                </label>
                <input
                  type="email"
                  defaultValue="ahmad@example.com"
                  className="input-field"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  شماره تلفن
                </label>
                <input
                  type="tel"
                  defaultValue="+98 912 345 6789"
                  className="input-field"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                رمز عبور
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  defaultValue="••••••••"
                  className="input-field pr-10"
                />
                <button
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
          </div>
        );

      case 'notifications':
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Mail className="w-5 h-5 text-blue-500" />
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">اعلان‌های ایمیل</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">دریافت اعلان‌ها از طریق ایمیل</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={notifications.email}
                    onChange={(e) => setNotifications({...notifications, email: e.target.checked})}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Bell className="w-5 h-5 text-green-500" />
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">اعلان‌های مرورگر</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">دریافت اعلان‌ها در مرورگر</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={notifications.push}
                    onChange={(e) => setNotifications({...notifications, push: e.target.checked})}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                </label>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Phone className="w-5 h-5 text-purple-500" />
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">پیامک</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">دریافت اعلان‌ها از طریق پیامک</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={notifications.sms}
                    onChange={(e) => setNotifications({...notifications, sms: e.target.checked})}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                </label>
              </div>
            </div>
          </div>
        );

      case 'privacy':
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  نمایش پروفایل
                </label>
                <select
                  value={privacy.profile}
                  onChange={(e) => setPrivacy({...privacy, profile: e.target.value})}
                  className="input-field"
                >
                  <option value="public">عمومی</option>
                  <option value="private">خصوصی</option>
                  <option value="friends">فقط دوستان</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  اشتراک‌گذاری داده‌ها
                </label>
                <select
                  value={privacy.data}
                  onChange={(e) => setPrivacy({...privacy, data: e.target.value})}
                  className="input-field"
                >
                  <option value="private">خصوصی</option>
                  <option value="public">عمومی</option>
                  <option value="anonymous">ناشناس</option>
                </select>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Shield className="w-5 h-5 text-green-500" />
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">تحلیل‌های آماری</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">اجازه استفاده از داده‌ها برای بهبود سیستم</p>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={privacy.analytics}
                    onChange={(e) => setPrivacy({...privacy, analytics: e.target.checked})}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                </label>
              </div>
            </div>
          </div>
        );

      case 'appearance':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  اندازه فونت
                </label>
                <select className="input-field">
                  <option value="small">کوچک</option>
                  <option value="medium" selected>متوسط</option>
                  <option value="large">بزرگ</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  رنگ اصلی
                </label>
                <select className="input-field">
                  <option value="blue" selected>آبی</option>
                  <option value="green">سبز</option>
                  <option value="purple">بنفش</option>
                  <option value="orange">نارنجی</option>
                </select>
              </div>
            </div>
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900 dark:text-white">پیش‌نمایش</h4>
              <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-primary-500 rounded-lg"></div>
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">نمونه متن</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">توضیحات نمونه</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );

      case 'language':
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                زبان سیستم
              </label>
              <select className="input-field">
                <option value="fa" selected>فارسی</option>
                <option value="en">English</option>
                <option value="ar">العربية</option>
                <option value="tr">Türkçe</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                منطقه زمانی
              </label>
              <select className="input-field">
                <option value="tehran" selected>تهران (UTC+3:30)</option>
                <option value="london">London (UTC+0)</option>
                <option value="newyork">New York (UTC-5)</option>
                <option value="tokyo">Tokyo (UTC+9)</option>
              </select>
            </div>
          </div>
        );

      case 'data':
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Database className="w-5 h-5 text-blue-500" />
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">دانلود داده‌ها</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">دریافت کپی از تمام داده‌های شما</p>
                  </div>
                </div>
                <button className="btn-primary">دانلود</button>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <RotateCcw className="w-5 h-5 text-orange-500" />
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">بازنشانی داده‌ها</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">حذف تمام داده‌ها و شروع مجدد</p>
                  </div>
                </div>
                <button className="btn-secondary">بازنشانی</button>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Lock className="w-5 h-5 text-red-500" />
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">حذف حساب</h4>
                    <p className="text-sm text-gray-500 dark:text-gray-400">حذف دائمی حساب کاربری</p>
                  </div>
                </div>
                <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors">
                  حذف
                </button>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
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
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">تنظیمات</h1>
          <p className="text-gray-600 dark:text-gray-400">مدیریت تنظیمات حساب کاربری</p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="btn-secondary flex items-center space-x-2">
            <RotateCcw className="w-4 h-4" />
            <span>بازنشانی</span>
          </button>
          <button className="btn-primary flex items-center space-x-2">
            <Save className="w-4 h-4" />
            <span>ذخیره</span>
          </button>
        </div>
      </motion.div>

      {/* Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="mt-6">
          {renderTabContent()}
        </div>
      </motion.div>
    </div>
  );
};

export default SettingsPanel;