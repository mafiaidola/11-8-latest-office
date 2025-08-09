// Activity Log Component - مكون سجل الأنشطة المحسن
import React, { useState, useEffect } from 'react';
import CommonDashboardComponents from './CommonDashboardComponents';

const ActivityLog = ({ 
  activities = [], 
  title = 'سجل الأنشطة الحديثة',
  maxItems = 10,
  showFilters = true,
  showRefresh = false,
  onRefresh,
  quickActions = []
}) => {
  const [filteredActivities, setFilteredActivities] = useState([]);
  const [typeFilter, setTypeFilter] = useState('all');
  const [timeFilter, setTimeFilter] = useState('all');
  const [loading, setLoading] = useState(false);

  // تحديث الأنشطة المفلترة عند تغيير المرشحات
  useEffect(() => {
    let filtered = [...activities];

    // مرشح النوع
    if (typeFilter !== 'all') {
      filtered = filtered.filter(activity => activity.type === typeFilter);
    }

    // مرشح الوقت
    if (timeFilter !== 'all') {
      const now = new Date();
      const filterDate = new Date();
      
      switch (timeFilter) {
        case 'today':
          filterDate.setHours(0, 0, 0, 0);
          break;
        case 'week':
          filterDate.setDate(filterDate.getDate() - 7);
          break;
        case 'month':
          filterDate.setMonth(filterDate.getMonth() - 1);
          break;
        default:
          break;
      }

      if (timeFilter !== 'all') {
        filtered = filtered.filter(activity => {
          const activityDate = new Date(activity.timestamp);
          return activityDate >= filterDate;
        });
      }
    }

    // ترتيب حسب التاريخ (الأحدث أولاً)
    filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    // تحديد العدد الأقصى
    filtered = filtered.slice(0, maxItems);

    setFilteredActivities(filtered);
  }, [activities, typeFilter, timeFilter, maxItems]);

  // تحديد أيقونة النشاط
  const getActivityIcon = (type) => {
    const icons = {
      'order_created': '🛒',
      'payment_received': '💰',
      'visit_completed': '🏥',
      'clinic_registered': '🏢',
      'user_login': '🔐',
      'user_created': '👤',
      'product_added': '📦',
      'debt_created': '📋',
      'debt_paid': '💳',
      'system_alert': '⚠️',
      'report_generated': '📊',
      'target_achieved': '🎯'
    };
    return icons[type] || '📝';
  };

  // تحديد لون النشاط
  const getActivityColor = (type) => {
    const colors = {
      'order_created': 'bg-blue-100 text-blue-800 border-blue-200',
      'payment_received': 'bg-green-100 text-green-800 border-green-200',
      'visit_completed': 'bg-purple-100 text-purple-800 border-purple-200',
      'clinic_registered': 'bg-indigo-100 text-indigo-800 border-indigo-200',
      'user_login': 'bg-gray-100 text-gray-800 border-gray-200',
      'user_created': 'bg-cyan-100 text-cyan-800 border-cyan-200',
      'product_added': 'bg-orange-100 text-orange-800 border-orange-200',
      'debt_created': 'bg-red-100 text-red-800 border-red-200',
      'debt_paid': 'bg-green-100 text-green-800 border-green-200',
      'system_alert': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'report_generated': 'bg-teal-100 text-teal-800 border-teal-200',
      'target_achieved': 'bg-pink-100 text-pink-800 border-pink-200'
    };
    return colors[type] || 'bg-gray-100 text-gray-800 border-gray-200';
  };

  // تحديد أنواع الأنشطة المتاحة
  const activityTypes = [
    { value: 'all', label: 'جميع الأنشطة' },
    { value: 'order_created', label: 'طلبات جديدة' },
    { value: 'payment_received', label: 'مدفوعات' },
    { value: 'visit_completed', label: 'زيارات' },
    { value: 'clinic_registered', label: 'عيادات جديدة' },
    { value: 'user_login', label: 'تسجيل دخول' },
    { value: 'debt_created', label: 'ديون جديدة' },
    { value: 'system_alert', label: 'تنبيهات النظام' }
  ];

  // خيارات مرشح الوقت
  const timeFilterOptions = [
    { value: 'all', label: 'جميع الأوقات' },
    { value: 'today', label: 'اليوم' },
    { value: 'week', label: 'الأسبوع الماضي' },
    { value: 'month', label: 'الشهر الماضي' }
  ];

  // الإجراءات السريعة للأنشطة
  const defaultQuickActions = [
    {
      label: 'تصدير الأنشطة',
      icon: '📄',
      onClick: () => {
        const csvContent = filteredActivities.map(activity => 
          `"${activity.timestamp}","${activity.type}","${activity.description}","${activity.user_id || ''}"`
        ).join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `activities_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
      },
      color: 'bg-green-50 hover:bg-green-100 text-green-700 border-green-200'
    },
    {
      label: 'مسح المرشحات',
      icon: '🗑️',
      onClick: () => {
        setTypeFilter('all');
        setTimeFilter('all');
      },
      color: 'bg-red-50 hover:bg-red-100 text-red-700 border-red-200'
    },
    {
      label: 'إعدادات التنبيهات',
      icon: '🔔',
      onClick: () => console.log('إعدادات التنبيهات'),
      color: 'bg-yellow-50 hover:bg-yellow-100 text-yellow-700 border-yellow-200'
    }
  ];

  const handleRefresh = async () => {
    setLoading(true);
    try {
      if (onRefresh) {
        await onRefresh();
      }
    } catch (error) {
      console.error('خطأ في تحديث الأنشطة:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-sm border border-white/20 overflow-hidden">
      {/* رأس السجل مع الإجراءات السريعة */}
      <div className="bg-gradient-to-r from-gray-50 to-blue-50 px-6 py-4 border-b border-gray-100">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <span className="text-blue-600 mr-2">📊</span>
              {title}
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              {filteredActivities.length} من أصل {activities.length} نشاط
            </p>
          </div>
          
          {showRefresh && (
            <button
              onClick={handleRefresh}
              disabled={loading}
              className="flex items-center px-3 py-2 bg-white hover:bg-gray-50 text-gray-700 rounded-lg border border-gray-200 transition-colors text-sm font-medium disabled:opacity-50"
              title="تحديث سجل الأنشطة"
            >
              <span className={`mr-2 ${loading ? 'animate-spin' : ''}`}>
                {loading ? '⏳' : '🔄'}
              </span>
              {loading ? 'جاري التحديث...' : 'تحديث'}
            </button>
          )}
        </div>

        {/* الإجراءات السريعة */}
        <div className="flex flex-wrap gap-2">
          {[...defaultQuickActions, ...quickActions].map((action, index) => (
            <button
              key={index}
              onClick={action.onClick}
              className={`inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-medium transition-colors border ${action.color}`}
            >
              <span className="mr-1">{action.icon}</span>
              {action.label}
            </button>
          ))}
        </div>
      </div>

      {/* المرشحات */}
      {showFilters && (
        <div className="bg-gray-50 px-6 py-4 border-b border-gray-100">
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center space-x-2 space-x-reverse">
              <span className="text-sm font-medium text-gray-700">نوع النشاط:</span>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {activityTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-center space-x-2 space-x-reverse">
              <span className="text-sm font-medium text-gray-700">الفترة الزمنية:</span>
              <select
                value={timeFilter}
                onChange={(e) => setTimeFilter(e.target.value)}
                className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                {timeFilterOptions.map(time => (
                  <option key={time.value} value={time.value}>
                    {time.label}
                  </option>
                ))}
              </select>
            </div>

            {(typeFilter !== 'all' || timeFilter !== 'all') && (
              <button
                onClick={() => {
                  setTypeFilter('all');
                  setTimeFilter('all');
                }}
                className="text-sm text-red-600 hover:text-red-800 font-medium bg-red-50 hover:bg-red-100 px-3 py-2 rounded-lg border border-red-200 transition-colors"
              >
                مسح المرشحات ✕
              </button>
            )}
          </div>
        </div>
      )}

      {/* قائمة الأنشطة */}
      <div className="max-h-96 overflow-y-auto">
        {loading ? (
          <CommonDashboardComponents.LoadingSpinner message="جاري تحميل الأنشطة..." />
        ) : filteredActivities.length > 0 ? (
          <div className="divide-y divide-gray-100">
            {filteredActivities.map((activity, index) => (
              <div key={activity.id || index} className="group p-4 hover:bg-gray-50 transition-colors duration-150">
                <div className="flex items-start space-x-4 space-x-reverse">
                  {/* أيقونة النشاط */}
                  <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center border ${getActivityColor(activity.type)}`}>
                    <span className="text-lg">
                      {getActivityIcon(activity.type)}
                    </span>
                  </div>

                  {/* تفاصيل النشاط */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-medium text-gray-900 group-hover:text-blue-700 transition-colors">
                        {activity.description || 'نشاط غير محدد'}
                      </p>
                      <p className="text-xs text-gray-500 flex items-center">
                        <span className="mr-1">⏰</span>
                        {activity.timestamp ? 
                          new Date(activity.timestamp).toLocaleString('ar-EG', {
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          }) : 'وقت غير محدد'
                        }
                      </p>
                    </div>

                    {/* معلومات إضافية */}
                    {activity.details && (
                      <div className="flex flex-wrap gap-3 text-xs text-gray-600 mb-2">
                        {activity.details.amount && (
                          <span className="inline-flex items-center bg-green-50 text-green-700 px-2 py-1 rounded-full">
                            💰 {activity.details.amount.toLocaleString()} ج.م
                          </span>
                        )}
                        {activity.details.clinic_name && (
                          <span className="inline-flex items-center bg-blue-50 text-blue-700 px-2 py-1 rounded-full">
                            🏥 {activity.details.clinic_name}
                          </span>
                        )}
                        {activity.user_id && (
                          <span className="inline-flex items-center bg-purple-50 text-purple-700 px-2 py-1 rounded-full">
                            👤 {activity.user_id}
                          </span>
                        )}
                      </div>
                    )}

                    {/* تصنيف النشاط */}
                    <div className="flex items-center justify-between">
                      <span className={`inline-flex items-center px-2 py-1 text-xs font-medium rounded-full border ${getActivityColor(activity.type)}`}>
                        {activityTypes.find(t => t.value === activity.type)?.label || 'نشاط عام'}
                      </span>
                      
                      {/* إجراءات سريعة للنشاط */}
                      <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex space-x-1 space-x-reverse">
                        <button 
                          className="w-6 h-6 rounded-full bg-gray-100 hover:bg-blue-100 flex items-center justify-center transition-colors"
                          title="عرض التفاصيل"
                        >
                          <span className="text-xs">👁️</span>
                        </button>
                        <button 
                          className="w-6 h-6 rounded-full bg-gray-100 hover:bg-green-100 flex items-center justify-center transition-colors"
                          title="نسخ"
                        >
                          <span className="text-xs">📋</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8">
            <CommonDashboardComponents.EmptyState
              icon="📋"
              title="لا توجد أنشطة"
              description="لم يتم العثور على أي أنشطة حديثة مطابقة للمرشحات المحددة"
              suggestions={[
                {
                  label: 'عرض جميع الأنشطة',
                  onClick: () => {
                    setTypeFilter('all');
                    setTimeFilter('all');
                  }
                },
                {
                  label: 'تحديث القائمة',
                  onClick: handleRefresh
                }
              ]}
            />
          </div>
        )}
      </div>

      {/* عرض المزيد */}
      {activities.length > maxItems && (
        <div className="bg-gray-50 px-6 py-4 border-t border-gray-100 text-center">
          <button className="text-blue-600 hover:text-blue-800 text-sm font-medium hover:bg-blue-50 px-4 py-2 rounded-lg transition-colors">
            عرض المزيد من الأنشطة ({activities.length - maxItems} نشاط إضافي) ↓
          </button>
        </div>
      )}
    </div>
  );
};

export default ActivityLog;