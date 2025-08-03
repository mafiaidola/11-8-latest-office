// Enhanced Clinic Registration Component - تسجيل العيادات المحسن
import React, { useState, useEffect } from 'react';
import { useTranslation } from '../../localization/translations.js';
import axios from 'axios';

const RepClinicRegistration = ({ user, language, isRTL }) => {
  const [clinicData, setClinicData] = useState({
    clinic_name: '',
    address: '',
    phone: '',
    doctor_name: '',
    clinic_class: 'Class A', // تصنيف العيادة
    credit_status: 'green', // الحالة الائتمانية: green, yellow, red
    // إزالة specialization كما طلب المستخدم
    latitude: null,
    longitude: null,
    classification: 'class_c',
    // إضافة حقول المسؤول الجديدة
    manager_name: '',
    manager_phone: ''
  });
  const [currentLocation, setCurrentLocation] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [locationError, setLocationError] = useState('');
  
  const { t } = useTranslation(language);
  const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001/api';

  useEffect(() => {
    getCurrentLocation();
  }, []);

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setCurrentLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            timestamp: new Date().toISOString()
          });
          
          // Auto-set clinic location to current location initially
          setClinicData(prev => ({
            ...prev,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          }));
          
          console.log('تم الحصول على الموقع الحالي بنجاح');
        },
        (error) => {
          console.error('خطأ في الحصول على الموقع:', error);
          setLocationError('لا يمكن الحصول على الموقع الحالي');
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 300000
        }
      );
    } else {
      setLocationError('المتصفح لا يدعم تحديد الموقع');
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setClinicData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const getClassificationColor = (classification) => {
    const colors = {
      'class_a': 'bg-green-500',
      'class_b': 'bg-blue-500',
      'class_c': 'bg-yellow-500',
      'class_d': 'bg-red-500'
    };
    return colors[classification] || 'bg-gray-500';
  };

  const getClassificationLabel = (classification) => {
    const labels = {
      'class_a': 'الفئة أ - ممتاز',
      'class_b': 'الفئة ب - جيد جداً',
      'class_c': 'الفئة ج - جيد',
      'class_d': 'الفئة د - مقبول'
    };
    return labels[classification] || classification;
  };

  const getCreditStatusColor = (status) => {
    const colors = {
      'green': 'bg-green-500',
      'yellow': 'bg-yellow-500',
      'red': 'bg-red-500'
    };
    return colors[status] || 'bg-gray-500';
  };

  const getCreditStatusLabel = (status) => {
    const labels = {
      'green': 'ممتاز - ائتمان عالي',
      'yellow': 'متوسط - ائتمان محدود',
      'red': 'ضعيف - ائتمان منخفض'
    };
    return labels[status] || status;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!clinicData.latitude || !clinicData.longitude) {
      setError('يرجى تحديد موقع العيادة');
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      const token = localStorage.getItem('access_token');
      const clinicPayload = {
        clinic_name: clinicData.clinic_name,
        address: clinicData.address,
        phone: clinicData.phone,
        doctor_name: clinicData.doctor_name,
        classification: clinicData.classification,
        credit_status: clinicData.credit_status,
        // إزالة specialization
        latitude: clinicData.latitude,
        longitude: clinicData.longitude,
        // إضافة حقول المسؤول الجديدة
        manager_name: clinicData.manager_name,
        manager_phone: clinicData.manager_phone,
        status: 'approved',
        added_by: user?.id,
        registration_metadata: {
          registered_by: user?.id,
          registered_by_name: user?.full_name || user?.username,
          registered_by_role: user?.role,
          registration_time: new Date().toISOString(),
          registration_location: currentLocation,
          rep_actual_location: currentLocation,
          approval_status: 'auto_approved',
          approved_by: user?.id,
          approved_by_name: user?.full_name || user?.username,
          approved_by_role: user?.role,
          approved_at: new Date().toISOString()
        }
      };

      const response = await axios.post(`${API}/clinics`, clinicPayload, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setSuccess('تم تسجيل العيادة بنجاح! ✅');
      
      // إعادة تعيين النموذج
      setClinicData({
        clinic_name: '',
        address: '',
        phone: '',
        doctor_name: '',
        clinic_class: 'Class A',
        credit_status: 'green',
        // إزالة specialization
        latitude: currentLocation?.latitude || null,
        longitude: currentLocation?.longitude || null,
        classification: 'class_c',
        // إعادة تعيين حقول المسؤول الجديدة
        manager_name: '',
        manager_phone: ''
      });

    } catch (error) {
      console.error('خطأ في تسجيل العيادة:', error);
      
      let errorMessage = 'فشل في تسجيل العيادة';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.status === 403) {
        errorMessage = 'ليس لديك صلاحية لتسجيل العيادات';
      } else if (error.response?.status === 401) {
        errorMessage = 'يرجى تسجيل الدخول مرة أخرى';
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="clinic-registration-container">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center">
            <span className="text-2xl text-white">🏥</span>
          </div>
          <div>
            <h1 className="text-3xl font-bold">{t('clinics', 'registerClinic')}</h1>
            <p className="text-lg opacity-75">إضافة عيادة طبية جديدة إلى النظام مع تصنيف وتقييم ائتماني</p>
          </div>
        </div>
      </div>

      {/* Status Messages */}
      {success && (
        <div className="mb-6 p-4 bg-green-500/20 border border-green-500/30 rounded-lg text-green-200 flex items-center gap-2">
          <span>✅</span>
          {success}
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 bg-red-500/20 border border-red-500/30 rounded-lg text-red-200 flex items-center gap-2">
          <span>❌</span>
          {error}
        </div>
      )}

      {locationError && (
        <div className="mb-6 p-4 bg-yellow-500/20 border border-yellow-500/30 rounded-lg text-yellow-200 flex items-center gap-2">
          <span>⚠️</span>
          {locationError}
        </div>
      )}

      {/* Registration Form */}
      <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 border border-white/20">
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Information */}
          <div className="form-section">
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
              <span>📋</span>
              المعلومات الأساسية
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-2">
                  {t('clinics', 'clinicName')} *
                </label>
                <input
                  type="text"
                  name="clinic_name"
                  value={clinicData.clinic_name}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="أدخل اسم العيادة"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  {t('clinics', 'doctorName')} *
                </label>
                <input
                  type="text"
                  name="doctor_name"
                  value={clinicData.doctor_name}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="أدخل اسم الطبيب"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  {t('clinics', 'clinicPhone')} *
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={clinicData.phone}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="أدخل رقم الهاتف"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  اسم المسؤول *
                </label>
                <input
                  type="text"
                  name="manager_name"
                  value={clinicData.manager_name}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="أدخل اسم المسؤول عن العيادة"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  رقم المسؤول *
                </label>
                <input
                  type="tel"
                  name="manager_phone"
                  value={clinicData.manager_phone}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  placeholder="أدخل رقم هاتف المسؤول"
                  required
                />
              </div>
            </div>

            <div className="mt-6">
              <label className="block text-sm font-medium mb-2">
                {t('clinics', 'clinicAddress')} *
              </label>
              <textarea
                name="address"
                value={clinicData.address}
                onChange={handleInputChange}
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                rows="3"
                placeholder="أدخل عنوان العيادة التفصيلي"
                required
              />
            </div>
          </div>

          {/* Classification & Credit Status */}
          <div className="form-section">
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
              <span>🏆</span>
              التصنيف والتقييم الائتماني
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium mb-3">
                  تصنيف العيادة
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {[
                    { value: 'class_a', label: 'الفئة أ', desc: 'ممتاز', icon: '🥇', color: 'gold' },
                    { value: 'class_b', label: 'الفئة ب', desc: 'جيد جداً', icon: '🥈', color: 'silver' },
                    { value: 'class_c', label: 'الفئة ج', desc: 'جيد', icon: '🥉', color: 'bronze' },
                    { value: 'class_d', label: 'الفئة د', desc: 'مقبول', icon: '🎖️', color: 'gray' }
                  ].map((classification) => (
                    <button
                      key={classification.value}
                      type="button"
                      onClick={() => setClinicData(prev => ({ ...prev, classification: classification.value }))}
                      className={`p-4 rounded-xl border-2 transition-all duration-300 flex items-center gap-3 hover:scale-105 ${
                        clinicData.classification === classification.value
                          ? 'border-blue-400 bg-blue-500/20 text-blue-300 shadow-lg shadow-blue-500/20'
                          : 'border-white/20 bg-white/10 hover:bg-white/20 hover:border-blue-300/50'
                      }`}
                    >
                      <span className="text-2xl">{classification.icon}</span>
                      <div className="text-right flex-1">
                        <div className="font-medium">{classification.label}</div>
                        <div className="text-xs opacity-75">{classification.desc}</div>
                      </div>
                    </button>
                  ))}
                </div>
                {clinicData.classification && (
                  <div className="mt-3 p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
                    <span className="text-sm text-blue-300">
                      ✅ تم اختيار: {getClassificationLabel(clinicData.classification)}
                    </span>
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium mb-3">
                  الحالة الائتمانية
                </label>
                <div className="space-y-3">
                  {[
                    { value: 'green', label: 'أخضر', desc: 'ائتمان ممتاز', icon: '🟢', bgColor: 'green' },
                    { value: 'yellow', label: 'أصفر', desc: 'ائتمان متوسط', icon: '🟡', bgColor: 'yellow' },
                    { value: 'red', label: 'أحمر', desc: 'ائتمان ضعيف', icon: '🔴', bgColor: 'red' }
                  ].map((creditStatus) => (
                    <button
                      key={creditStatus.value}
                      type="button"
                      onClick={() => setClinicData(prev => ({ ...prev, credit_status: creditStatus.value }))}
                      className={`w-full p-4 rounded-xl border-2 transition-all duration-300 flex items-center gap-3 hover:scale-105 ${
                        clinicData.credit_status === creditStatus.value
                          ? creditStatus.value === 'green' 
                            ? 'border-green-400 bg-green-500/20 text-green-300 shadow-lg shadow-green-500/20'
                            : creditStatus.value === 'yellow'
                            ? 'border-yellow-400 bg-yellow-500/20 text-yellow-300 shadow-lg shadow-yellow-500/20'
                            : 'border-red-400 bg-red-500/20 text-red-300 shadow-lg shadow-red-500/20'
                          : 'border-white/20 bg-white/10 hover:bg-white/20 hover:border-white/40'
                      }`}
                    >
                      <span className="text-2xl">{creditStatus.icon}</span>
                      <div className="text-right flex-1">
                        <div className="font-medium">{creditStatus.label}</div>
                        <div className="text-xs opacity-75">{creditStatus.desc}</div>
                      </div>
                      {clinicData.credit_status === creditStatus.value && (
                        <span className="text-lg">✅</span>
                      )}
                    </button>
                  ))}
                </div>
                {clinicData.credit_status && (
                  <div className={`mt-3 p-3 rounded-lg border ${
                    clinicData.credit_status === 'green' ? 'bg-green-500/10 border-green-500/20' :
                    clinicData.credit_status === 'yellow' ? 'bg-yellow-500/10 border-yellow-500/20' :
                    'bg-red-500/10 border-red-500/20'
                  }`}>
                    <span className={`text-sm ${
                      clinicData.credit_status === 'green' ? 'text-green-300' :
                      clinicData.credit_status === 'yellow' ? 'text-yellow-300' :
                      'text-red-300'
                    }`}>
                      ✅ تم اختيار: {getCreditStatusLabel(clinicData.credit_status)}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Location Information */}
          <div className="form-section">
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
              <span>📍</span>
              معلومات الموقع
            </h3>
            
            <div className="space-y-6">
              {/* Current Location Status */}
              {currentLocation && (
                <div className="p-4 bg-green-500/20 border border-green-500/30 rounded-lg">
                  <p className="text-green-300 text-sm flex items-center gap-2 mb-2">
                    <span>✅</span>
                    تم تحديد موقعك الحالي بنجاح
                  </p>
                  <p className="text-xs text-green-200">
                    دقة التحديد: {currentLocation.accuracy?.toFixed(0)} متر
                  </p>
                </div>
              )}

              {/* Interactive Google Maps */}
              {clinicData.latitude && clinicData.longitude ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-lg font-semibold text-white flex items-center gap-2">
                      <span>🗺️</span>
                      موقع العيادة على الخريطة
                    </h4>
                    <button
                      type="button"
                      onClick={getCurrentLocation}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                    >
                      📍 تحديث الموقع
                    </button>
                  </div>
                  
                  {/* Interactive Google Maps with Draggable Marker */}
                  <div className="relative">
                    <div className="w-full h-80 bg-gray-900 rounded-xl border-2 border-white/20 overflow-hidden shadow-lg">
                      {process.env.REACT_APP_GOOGLE_MAPS_API_KEY ? (
                        <div className="relative w-full h-full">
                          {/* Enhanced Google Maps with Draggable Marker */}
                          <div 
                            className="w-full h-full relative"
                            id="interactive-map"
                          >
                            <iframe
                              src={`https://www.google.com/maps/embed/v1/view?key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}&center=${clinicData.latitude},${clinicData.longitude}&zoom=16&maptype=roadmap`}
                              width="100%"
                              height="100%"
                              style={{ border: 0 }}
                              allowFullScreen
                              loading="lazy"
                              referrerPolicy="no-referrer-when-downgrade"
                              className="rounded-xl opacity-90"
                              title="موقع العيادة على Google Maps"
                              onLoad={() => console.log('✅ Google Maps loaded successfully')}
                              onError={(e) => {
                                console.error('❌ Google Maps failed to load:', e);
                                e.target.style.display = 'none';
                                if (e.target.nextElementSibling) {
                                  e.target.nextElementSibling.style.display = 'block';
                                }
                              }}
                            />
                            
                            {/* Fixed Pin Marker Overlay - Center Pin for Reference */}
                            <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
                              <div className="relative">
                                <div className="text-red-500 text-4xl animate-bounce" style={{ textShadow: '0 0 10px rgba(0,0,0,0.8)' }}>
                                  📍
                                </div>
                                <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 bg-red-500/80 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                                  موقع العيادة
                                </div>
                              </div>
                            </div>
                            
                            {/* Location Precision Indicator */}
                            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none">
                              <div className="w-8 h-8 border-4 border-red-500 rounded-full bg-red-500/20 animate-pulse"></div>
                            </div>

                            {/* Interactive Map Instructions */}
                            <div className="absolute top-4 right-4 bg-black/90 backdrop-blur-sm rounded-xl p-3 text-white shadow-2xl border border-white/20 max-w-xs">
                              <div className="text-xs space-y-1">
                                <div className="font-bold text-green-300 flex items-center gap-1">
                                  <span>💡</span>
                                  تعليمات الخريطة
                                </div>
                                <div>• انقر على "موقع مخصص" أسفل لتغيير الموقع</div>
                                <div>• استخدم الحقول أسفل للتعديل الدقيق</div>
                                <div>• أو اضغط "استخدم موقعي" للموقع الحالي</div>
                              </div>
                            </div>
                          </div>
                          
                          {/* Fallback: Static Map Link */}
                          <div 
                            className="w-full h-full bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 flex items-center justify-center"
                            style={{ display: 'none' }}
                          >
                            <div className="text-center">
                              <div className="text-5xl mb-3">🗺️</div>
                              <h4 className="text-lg font-bold text-white mb-2">خريطة موقع العيادة</h4>
                              <p className="text-white/80 text-sm mb-4">
                                📍 الموقع: {clinicData.latitude?.toFixed(6)}, {clinicData.longitude?.toFixed(6)}
                              </p>
                              <button
                                type="button"
                                onClick={() => {
                                  const googleMapsUrl = `https://www.google.com/maps?q=${clinicData.latitude},${clinicData.longitude}&zoom=16`;
                                  window.open(googleMapsUrl, '_blank');
                                }}
                                className="bg-green-600 text-white px-6 py-3 rounded-lg text-sm hover:bg-green-700 transition-colors font-medium"
                              >
                                🔗 فتح في Google Maps
                              </button>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl">
                          <div className="text-center">
                            <div className="text-5xl mb-3">🗺️</div>
                            <p className="text-white text-lg font-semibold mb-2">موقع العيادة</p>
                            <div className="text-4xl text-red-500 mb-2">📍</div>
                            <p className="text-gray-300 text-sm mb-4">
                              الإحداثيات: {clinicData.latitude?.toFixed(6)}, {clinicData.longitude?.toFixed(6)}
                            </p>
                            <button
                              type="button"
                              onClick={() => {
                                const googleMapsUrl = `https://www.google.com/maps?q=${clinicData.latitude},${clinicData.longitude}&zoom=16`;
                                window.open(googleMapsUrl, '_blank');
                              }}
                              className="bg-blue-600 text-white px-6 py-3 rounded-lg text-sm hover:bg-blue-700 transition-colors font-medium"
                            >
                              🔗 فتح في Google Maps
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    {/* Enhanced Control Overlay */}
                    <div className="absolute top-4 left-4 bg-black/90 backdrop-blur-sm rounded-xl p-4 text-white shadow-2xl border border-white/20">
                      <div className="text-sm font-bold flex items-center gap-2 mb-2">
                        <span>📍</span>
                        موقع العيادة
                      </div>
                      <div className="text-xs space-y-1 text-gray-200">
                        <div><strong>العرض:</strong> {clinicData.latitude?.toFixed(6)}</div>
                        <div><strong>الطول:</strong> {clinicData.longitude?.toFixed(6)}</div>
                        <div className="text-green-300"><strong>الحالة:</strong> ✅ محدد</div>
                      </div>
                    </div>

                    {/* Enhanced Control Buttons */}
                    <div className="absolute bottom-4 right-4 flex gap-3">
                      <button
                        type="button"
                        onClick={() => {
                          const googleMapsUrl = `https://www.google.com/maps?q=${clinicData.latitude},${clinicData.longitude}&zoom=16`;
                          window.open(googleMapsUrl, '_blank');
                          console.log('🔗 فتح الخريطة في Google Maps');
                        }}
                        className="bg-green-600 text-white px-4 py-3 rounded-xl text-sm hover:bg-green-700 transition-all duration-300 flex items-center gap-2 font-medium shadow-lg border border-green-500/30"
                        title="فتح في Google Maps"
                      >
                        <span>🔗</span>
                        فتح الخريطة
                      </button>
                      
                      <button
                        type="button"
                        onClick={() => {
                          if (currentLocation) {
                            setClinicData(prev => ({
                              ...prev,
                              latitude: currentLocation.latitude,
                              longitude: currentLocation.longitude
                            }));
                            console.log('📱 تم تحديث موقع العيادة لموقعك الحالي');
                            setSuccess('تم تحديث موقع العيادة لموقعك الحالي ✅');
                          } else {
                            getCurrentLocation();
                          }
                        }}
                        className="bg-blue-600 text-white px-4 py-3 rounded-xl text-sm hover:bg-blue-700 transition-all duration-300 flex items-center gap-2 font-medium shadow-lg border border-blue-500/30"
                        title="استخدام موقعي الحالي"
                      >
                        <span>📱</span>
                        استخدم موقعي
                      </button>

                      <button
                        type="button"
                        onClick={() => {
                          getCurrentLocation();
                          console.log('🔄 جاري تحديث الموقع...');
                        }}
                        className="bg-orange-600 text-white px-4 py-3 rounded-xl text-sm hover:bg-orange-700 transition-all duration-300 flex items-center gap-2 font-medium shadow-lg border border-orange-500/30"
                        title="تحديث الموقع"
                      >
                        <span>🔄</span>
                        تحديث
                      </button>
                      
                      <button
                        type="button"
                        onClick={() => {
                          // مطالبة المستخدم بإدخال إحداثيات جديدة
                          const newLat = prompt('أدخل خط العرض الجديد:', clinicData.latitude);
                          if (newLat) {
                            const newLng = prompt('أدخل خط الطول الجديد:', clinicData.longitude);
                            if (newLng) {
                              setClinicData(prev => ({
                                ...prev,
                                latitude: parseFloat(newLat),
                                longitude: parseFloat(newLng)
                              }));
                              setSuccess('تم تحديث الإحداثيات بنجاح ✅');
                              console.log('📍 تم تحديث إحداثيات العيادة يدوياً');
                            }
                          }
                        }}
                        className="bg-purple-600 text-white px-4 py-3 rounded-xl text-sm hover:bg-purple-700 transition-all duration-300 flex items-center gap-2 font-medium shadow-lg border border-purple-500/30"
                        title="تحديد موقع مخصص"
                      >
                        <span>🎯</span>
                        موقع مخصص
                      </button>
                    </div>
                  </div>

                  {/* Manual Location Input - Enhanced */}
                  <div className="bg-white/5 rounded-xl p-4 border border-white/10">
                    <h5 className="text-sm font-medium text-white mb-3 flex items-center gap-2">
                      <span>⚙️</span>
                      تعديل الإحداثيات يدوياً (دقة عالية)
                    </h5>
                    <div className="grid grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-xs font-medium text-gray-300 mb-1">
                          خط العرض (Latitude)
                        </label>
                        <input
                          type="number"
                          step="any"
                          name="latitude"
                          value={clinicData.latitude || ''}
                          onChange={(e) => {
                            handleInputChange(e);
                            if (e.target.value) {
                              console.log('🔄 تم تحديث خط العرض:', e.target.value);
                            }
                          }}
                          className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                          placeholder="30.0444"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-xs font-medium text-gray-300 mb-1">
                          خط الطول (Longitude)
                        </label>
                        <input
                          type="number"
                          step="any"
                          name="longitude"
                          value={clinicData.longitude || ''}
                          onChange={(e) => {
                            handleInputChange(e);
                            if (e.target.value) {
                              console.log('🔄 تم تحديث خط الطول:', e.target.value);
                            }
                          }}
                          className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                          placeholder="31.2357"
                        />
                      </div>
                    </div>
                    
                    {/* Quick Coordinate Actions */}
                    <div className="flex gap-2 flex-wrap">
                      <button
                        type="button"
                        onClick={() => {
                          if (navigator.clipboard) {
                            navigator.clipboard.writeText(`${clinicData.latitude},${clinicData.longitude}`);
                            setSuccess('تم نسخ الإحداثيات ✅');
                          }
                        }}
                        className="px-3 py-2 bg-blue-500/20 text-blue-300 text-xs rounded-lg hover:bg-blue-500/30 transition-colors border border-blue-500/30"
                      >
                        📋 نسخ الإحداثيات
                      </button>
                      
                      <button
                        type="button"
                        onClick={async () => {
                          if (navigator.clipboard) {
                            try {
                              const clipboardText = await navigator.clipboard.readText();
                              const coords = clipboardText.split(',');
                              if (coords.length === 2) {
                                const lat = parseFloat(coords[0].trim());
                                const lng = parseFloat(coords[1].trim());
                                if (!isNaN(lat) && !isNaN(lng)) {
                                  setClinicData(prev => ({
                                    ...prev,
                                    latitude: lat,
                                    longitude: lng
                                  }));
                                  setSuccess('تم لصق الإحداثيات بنجاح ✅');
                                } else {
                                  setError('تنسيق الإحداثيات غير صحيح');
                                }
                              }
                            } catch (error) {
                              console.error('خطأ في قراءة الحافظة:', error);
                            }
                          }
                        }}
                        className="px-3 py-2 bg-green-500/20 text-green-300 text-xs rounded-lg hover:bg-green-500/30 transition-colors border border-green-500/30"
                      >
                        📥 لصق من الحافظة
                      </button>
                      
                      <button
                        type="button"
                        onClick={() => {
                          const googleMapsShareUrl = `https://www.google.com/maps/@${clinicData.latitude},${clinicData.longitude},16z`;
                          window.open(googleMapsShareUrl, '_blank');
                        }}
                        className="px-3 py-2 bg-purple-500/20 text-purple-300 text-xs rounded-lg hover:bg-purple-500/30 transition-colors border border-purple-500/30"
                      >
                        🗺️ عرض في خرائط جوجل
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 bg-white/5 rounded-xl border border-white/10">
                  <div className="text-4xl mb-2">🗺️</div>
                  <h4 className="text-lg font-semibold text-white mb-2">لم يتم تحديد الموقع بعد</h4>
                  <p className="text-gray-400 text-sm mb-4">
                    يرجى السماح بالوصول للموقع لتحديد موقع العيادة تلقائياً
                  </p>
                  <button
                    type="button"
                    onClick={getCurrentLocation}
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    📍 تحديد الموقع الحالي
                  </button>
                </div>
              )}

              {locationError && (
                <div className="p-4 bg-red-500/20 border border-red-500/30 rounded-lg">
                  <p className="text-red-300 text-sm flex items-center gap-2">
                    <span>⚠️</span>
                    {locationError}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-center pt-6">
            <button
              type="submit"
              disabled={isLoading}
              className="bg-gradient-to-r from-green-600 to-green-700 text-white px-8 py-3 rounded-lg font-medium hover:from-green-700 hover:to-green-800 transition-all duration-200 disabled:opacity-50 flex items-center gap-2 min-w-[200px] justify-center"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  جاري التسجيل...
                </>
              ) : (
                <>
                  <span>✅</span>
                  تسجيل العيادة
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Help Section */}
      <div className="mt-8 bg-white/5 backdrop-blur-lg rounded-xl p-6 border border-white/20">
        <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
          <span>💡</span>
          إرشادات التسجيل
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm opacity-75">
          <div>
            <h4 className="font-bold mb-2">📋 المعلومات الأساسية</h4>
            <ul className="space-y-1">
              <li>• تأكد من إدخال جميع المعلومات بدقة</li>
              <li>• اسم العيادة يجب أن يكون واضحاً ومحدداً</li>
              <li>• أدخل رقم هاتف صحيح للتواصل</li>
            </ul>
          </div>
          <div>
            <h4 className="font-bold mb-2">🏆 التصنيف والتقييم</h4>
            <ul className="space-y-1">
              <li>• الفئة أ: عيادات ممتازة بمعايير عالية</li>
              <li>• الأخضر: ائتمان ممتاز، عمليات سلسة</li>
              <li>• الأصفر: يحتاج متابعة ائتمانية</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RepClinicRegistration;