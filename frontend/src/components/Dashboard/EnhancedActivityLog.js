// Enhanced Activity Log Component - مكون سجل الأنشطة المحسن والاحترافي
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const EnhancedActivityLog = ({ 
  activities = [], 
  title = 'سجل أنشطة النظام الحديثة',
  maxItems = 15,
  showFilters = true,
  showRefresh = true,
  onRefresh,
  language = 'ar'
}) => {
  const [filteredActivities, setFilteredActivities] = useState([]);
  const [typeFilter, setTypeFilter] = useState('all');
  const [timeFilter, setTimeFilter] = useState('all');
  const [loading, setLoading] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedActivity, setSelectedActivity] = useState(null);

  const API_URL = process.env.REACT_APP_BACKEND_URL;

  // تحميل الأنشطة المحسنة من قاعدة البيانات
  const loadEnhancedActivities = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      // جلب الأنشطة المختلفة من APIs مختلفة
      const [
        invoicesResponse,
        visitsResponse, 
        debtsResponse,
        usersResponse,
        clinicsResponse
      ] = await Promise.allSettled([
        axios.get(`${API_URL}/api/invoices`, { headers }),
        axios.get(`${API_URL}/api/visits`, { headers }),
        axios.get(`${API_URL}/api/debts`, { headers }),
        axios.get(`${API_URL}/api/users`, { headers }),
        axios.get(`${API_URL}/api/clinics`, { headers })
      ]);

      const enhancedActivities = [];

      // معالجة الفواتير
      if (invoicesResponse.status === 'fulfilled' && invoicesResponse.value.data) {
        invoicesResponse.value.data.forEach(invoice => {
          enhancedActivities.push({
            id: `invoice_${invoice.id}`,
            type: 'invoice_created',
            user_name: invoice.created_by || 'نظام',
            description: `قام ${invoice.created_by} بعمل فاتورة رقم ${invoice.invoice_number}`,
            details: `فاتورة بقيمة ${invoice.amount} ج.م للعيادة ${invoice.clinic_name}`,
            timestamp: invoice.created_at,
            related_entity: 'invoice',
            entity_id: invoice.id,
            amount: invoice.amount,
            clinic_name: invoice.clinic_name,
            navigation_target: 'IntegratedFinancialDashboard',
            priority: 'medium'
          });
        });
      }

      // معالجة الزيارات
      if (visitsResponse.status === 'fulfilled' && visitsResponse.value.data) {
        visitsResponse.value.data.forEach(visit => {
          enhancedActivities.push({
            id: `visit_${visit.id}`,
            type: 'visit_completed',
            user_name: visit.assigned_to || 'مندوب مجهول',
            description: `قام ${visit.assigned_to} بعمل زيارة للعيادة ${visit.clinic_name}`,
            details: `زيارة ${visit.visit_type} - حالة: ${visit.status}`,
            timestamp: visit.created_at,
            related_entity: 'visit',
            entity_id: visit.id,
            clinic_name: visit.clinic_name,
            visit_type: visit.visit_type,
            navigation_target: 'EnhancedVisitsManagement',
            priority: 'high'
          });
        });
      }

      // معالجة الديون
      if (debtsResponse.status === 'fulfilled' && debtsResponse.value.data) {
        debtsResponse.value.data.forEach(debt => {
          enhancedActivities.push({
            id: `debt_${debt.id}`,
            type: 'debt_created',
            user_name: debt.created_by || 'نظام',
            description: `قام ${debt.created_by} بعمل دين للعيادة ${debt.clinic_name}`,
            details: `دين بقيمة ${debt.amount} ج.م - تاريخ الاستحقاق: ${debt.due_date}`,
            timestamp: debt.created_at,
            related_entity: 'debt',
            entity_id: debt.id,
            amount: debt.amount,
            clinic_name: debt.clinic_name,
            navigation_target: 'IntegratedFinancialDashboard',
            priority: 'high'
          });
        });
      }

      // معالجة المستخدمين الجدد
      if (usersResponse.status === 'fulfilled' && usersResponse.value.data) {
        usersResponse.value.data.forEach(user => {
          enhancedActivities.push({
            id: `user_${user.user_id}`,
            type: 'user_created',
            user_name: 'مدير النظام',
            description: `تم إضافة مستخدم جديد: ${user.full_name}`,
            details: `مستخدم بدور ${user.role} - اسم المستخدم: ${user.username}`,
            timestamp: user.created_at || new Date().toISOString(),
            related_entity: 'user',
            entity_id: user.user_id,
            user_role: user.role,
            navigation_target: 'UserManagement',
            priority: 'medium'
          });
        });
      }

      // معالجة العيادات المسجلة
      if (clinicsResponse.status === 'fulfilled' && clinicsResponse.value.data) {
        clinicsResponse.value.data.forEach(clinic => {
          enhancedActivities.push({
            id: `clinic_${clinic.id}`,
            type: 'clinic_registered',
            user_name: clinic.registered_by || 'مندوب مجهول',
            description: `قام ${clinic.registered_by} بإضافة عيادة ${clinic.name}`,
            details: `عيادة د. ${clinic.doctor_name} - العنوان: ${clinic.address}`,
            timestamp: clinic.created_at,
            related_entity: 'clinic',
            entity_id: clinic.id,
            clinic_name: clinic.name,
            doctor_name: clinic.doctor_name,
            navigation_target: 'ClinicsManagement',
            priority: 'high'
          });
        });
      }

      // إضافة أنشطة تسجيل الدخول الوهمية للعرض
      enhancedActivities.push(
        {
          id: 'login_demo_1',
          type: 'user_login',
          user_name: 'أحمد محمد',
          description: 'قام أحمد محمد بتسجيل الدخول',
          details: 'تسجيل دخول ناجح من جهاز كمبيوتر',
          timestamp: new Date(Date.now() - 1800000).toISOString(), // 30 minutes ago
          related_entity: 'login',
          entity_id: 'login_demo_1',
          navigation_target: 'ActivityTrackingFixed',
          priority: 'low'
        },
        {
          id: 'order_demo_1',
          type: 'order_created',
          user_name: 'فاطمة علي',
          description: 'قام فاطمة علي بعمل طلب جديد',
          details: 'طلب يحتوي على 5 منتجات بقيمة 2,500 ج.م',
          timestamp: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
          related_entity: 'order',
          entity_id: 'order_demo_1',
          amount: 2500,
          navigation_target: 'ProductManagement',
          priority: 'medium'
        }
      );

      // ترتيب الأنشطة حسب التاريخ (الأحدث أولاً)
      enhancedActivities.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
      
      setFilteredActivities(enhancedActivities.slice(0, maxItems));
    } catch (error) {
      console.error('Error loading enhanced activities:', error);
      setFilteredActivities([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEnhancedActivities();
  }, []);

  useEffect(() => {
    if (onRefresh) {
      loadEnhancedActivities();
    }
  }, [onRefresh]);

  // تحديد أيقونة النشاط
  const getActivityIcon = (type) => {
    const icons = {
      'invoice_created': '📄',
      'visit_completed': '🏥',
      'clinic_registered': '🏢',
      'user_login': '🔐',
      'user_created': '👤',
      'debt_created': '💳',
      'debt_paid': '💰',
      'order_created': '🛒',
      'product_added': '📦'
    };
    return icons[type] || '📝';
  };

  // تحديد لون النشاط حسب الأولوية
  const getActivityColor = (priority, type) => {
    if (priority === 'high') {
      return 'bg-red-50 border-red-200 text-red-800';
    } else if (priority === 'medium') {
      return 'bg-yellow-50 border-yellow-200 text-yellow-800';
    } else {
      return 'bg-green-50 border-green-200 text-green-800';
    }
  };

  // تنسيق الوقت
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 60) {
      return `منذ ${diffInMinutes} دقيقة`;
    } else if (diffInMinutes < 1440) {
      return `منذ ${Math.floor(diffInMinutes / 60)} ساعة`;
    } else {
      return date.toLocaleDateString('ar-EG', {
        year: 'numeric',
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  };

  // معالجة النقر على زر التفاصيل
  const handleDetailsClick = (activity) => {
    if (activity.navigation_target) {
      // إرسال حدث للتنقل إلى القسم المناسب
      window.dispatchEvent(new CustomEvent('navigateToSection', { 
        detail: activity.navigation_target 
      }));
    }
  };

  // معالجة النقر على زر تفاصيل النشاط
  const handleActivityDetails = (activity) => {
    setSelectedActivity(activity);
    setShowDetailModal(true);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-2xl font-bold text-gray-900 flex items-center">
            <span className="text-indigo-600 mr-3 text-3xl">📊</span>
            {title}
          </h3>
          <p className="text-gray-600 mt-2">
            القلب النابض للنظام - متابعة شاملة لجميع الأنشطة والعمليات بشكل احترافي
          </p>
        </div>
        
        {showRefresh && (
          <button
            onClick={loadEnhancedActivities}
            disabled={loading}
            className="flex items-center px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg transition-all shadow-lg hover:shadow-xl"
          >
            <span className={`ml-2 ${loading ? 'animate-spin' : ''}`}>
              {loading ? '⏳' : '🔄'}
            </span>
            {loading ? 'جاري التحديث...' : 'تحديث الأنشطة'}
          </button>
        )}
      </div>

      {/* Activities List */}
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin text-4xl mb-4">⏳</div>
            <p className="text-gray-600">جاري تحميل الأنشطة...</p>
          </div>
        ) : filteredActivities.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-6xl mb-4">📭</div>
            <p className="text-gray-600 text-lg">لا توجد أنشطة حديثة للعرض</p>
          </div>
        ) : (
          filteredActivities.map((activity, index) => (
            <div
              key={activity.id}
              className={`${getActivityColor(activity.priority, activity.type)} border-2 rounded-xl p-4 hover:shadow-lg transition-all duration-300`}
            >
              <div className="flex justify-between items-start">
                <div className="flex items-start space-x-4 space-x-reverse flex-1">
                  {/* Icon */}
                  <div className="text-3xl">{getActivityIcon(activity.type)}</div>
                  
                  {/* Content */}
                  <div className="flex-1">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-bold text-lg text-gray-900">
                        {activity.description}
                      </h4>
                      <span className="text-sm font-medium text-gray-600">
                        {formatTimestamp(activity.timestamp)}
                      </span>
                    </div>
                    
                    <p className="text-gray-700 mb-3">{activity.details}</p>
                    
                    {/* Action Buttons */}
                    <div className="flex space-x-3 space-x-reverse">
                      <button
                        onClick={() => handleDetailsClick(activity)}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-all shadow-sm hover:shadow-md text-sm"
                      >
                        📋 تفاصيل من {activity.related_entity === 'invoice' ? 'الحسابات' : 
                                        activity.related_entity === 'visit' ? 'الزيارات' :
                                        activity.related_entity === 'debt' ? 'التحصيل والمديونيات' :
                                        activity.related_entity === 'clinic' ? 'إدارة العيادات' :
                                        activity.related_entity === 'user' ? 'إدارة المستخدمين' :
                                        activity.related_entity === 'login' ? 'تتبع الأنشطة' :
                                        'النظام'}
                      </button>
                      
                      {(activity.related_entity === 'clinic' || activity.related_entity === 'invoice') && (
                        <button
                          onClick={() => handleActivityDetails(activity)}
                          className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-all shadow-sm hover:shadow-md text-sm"
                        >
                          📄 {activity.related_entity === 'clinic' ? 'ملف العيادة' : 'تفاصيل الفاتورة'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Detail Modal */}
      {showDetailModal && selectedActivity && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-2xl w-full mx-4 max-h-96 overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">تفاصيل النشاط</h3>
              <button
                onClick={() => setShowDetailModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <strong>النوع:</strong> {selectedActivity.type}
              </div>
              <div>
                <strong>المستخدم:</strong> {selectedActivity.user_name}
              </div>
              <div>
                <strong>الوصف:</strong> {selectedActivity.description}
              </div>
              <div>
                <strong>التفاصيل:</strong> {selectedActivity.details}
              </div>
              <div>
                <strong>التوقيت:</strong> {formatTimestamp(selectedActivity.timestamp)}
              </div>
              {selectedActivity.amount && (
                <div>
                  <strong>المبلغ:</strong> {selectedActivity.amount} ج.م
                </div>
              )}
              {selectedActivity.clinic_name && (
                <div>
                  <strong>العيادة:</strong> {selectedActivity.clinic_name}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedActivityLog;