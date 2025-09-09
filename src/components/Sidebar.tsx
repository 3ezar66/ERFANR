import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  Home, 
  BarChart3, 
  Settings, 
  Users, 
  FileText, 
  Globe, 
  Shield,
  Zap,
  Heart,
  Star
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  currentView: string;
  onViewChange: (view: string) => void;
}

const menuItems = [
  { id: 'dashboard', label: 'داشبورد', icon: Home },
  { id: 'analytics', label: 'تحلیل‌ها', icon: BarChart3 },
  { id: 'users', label: 'کاربران', icon: Users },
  { id: 'documents', label: 'مستندات', icon: FileText },
  { id: 'global', label: 'جهانی', icon: Globe },
  { id: 'security', label: 'امنیت', icon: Shield },
  { id: 'performance', label: 'عملکرد', icon: Zap },
  { id: 'favorites', label: 'مورد علاقه', icon: Heart },
  { id: 'settings', label: 'تنظیمات', icon: Settings },
];

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose, currentView, onViewChange }) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          />
          
          {/* Sidebar */}
          <motion.aside
            initial={{ x: -300 }}
            animate={{ x: 0 }}
            exit={{ x: -300 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed left-0 top-0 h-full w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 z-50 lg:relative lg:translate-x-0"
          >
            <div className="flex flex-col h-full">
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
                    <Star className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-gray-900 dark:text-white">ERFANR</h2>
                    <p className="text-sm text-gray-500 dark:text-gray-400">سیستم جامع</p>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <X className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                </button>
              </div>

              {/* Navigation */}
              <nav className="flex-1 p-4 space-y-2">
                {menuItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = currentView === item.id;
                  
                  return (
                    <motion.button
                      key={item.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => {
                        onViewChange(item.id);
                        onClose();
                      }}
                      className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                        isActive
                          ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-700 dark:text-primary-300 border border-primary-200 dark:border-primary-700'
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                      }`}
                    >
                      <Icon className={`w-5 h-5 ${isActive ? 'text-primary-600' : 'text-gray-500'}`} />
                      <span className="font-medium">{item.label}</span>
                    </motion.button>
                  );
                })}
              </nav>

              {/* Footer */}
              <div className="p-4 border-t border-gray-200 dark:border-gray-700">
                <div className="bg-gradient-to-r from-primary-50 to-secondary-50 dark:from-primary-900/20 dark:to-secondary-900/20 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-2">
                    نسخه پیشرفته
                  </h3>
                  <p className="text-xs text-gray-600 dark:text-gray-400 mb-3">
                    دسترسی به تمام ویژگی‌های پیشرفته
                  </p>
                  <button className="w-full btn-primary text-sm">
                    ارتقا دهید
                  </button>
                </div>
              </div>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
};

export default Sidebar;