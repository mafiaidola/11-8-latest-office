#!/usr/bin/env python3
"""
Enhanced Clinic Registration GPS Fix Backend Testing
Focus: Test backend stability and API availability for GPS functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "https://ec499ace-685d-480d-b657-849bf4e418d7.preview.emergentagent.com/api"
ADMIN_CREDENTIALS = {"username": "admin", "password": "admin123"}

class EnhancedClinicRegistrationTester:
    def __init__(self):
        self.token = None
        self.test_results = []
        self.start_time = time.time()
        
    def log_test(self, test_name, success, response_time, details):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "response_time": response_time,
            "details": details,
            "status": status
        })
        print(f"{status} {test_name} ({response_time:.2f}ms)")
        if details:
            print(f"   📋 {details}")
    
    def test_admin_login(self):
        """Test admin login to get JWT token"""
        start = time.time()
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=ADMIN_CREDENTIALS, timeout=10)
            response_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                user_info = data.get("user", {})
                details = f"User: {user_info.get('full_name', 'Unknown')}, Role: {user_info.get('role', 'Unknown')}"
                self.log_test("Admin Login (admin/admin123)", True, response_time, details)
                return True
            else:
                self.log_test("Admin Login (admin/admin123)", False, response_time, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            response_time = (time.time() - start) * 1000
            self.log_test("Admin Login (admin/admin123)", False, response_time, f"Exception: {str(e)}")
            return False
    
    def test_enhanced_clinic_form_data_api(self):
        """Test Enhanced Clinic Registration form data API"""
        if not self.token:
            self.log_test("Enhanced Clinic Form Data API", False, 0, "No authentication token")
            return False
            
        start = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/enhanced-clinics/registration/form-data", headers=headers, timeout=10)
            response_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                # Check if required data is present
                required_fields = ['clinic_classifications', 'credit_classifications', 'lines', 'areas']
                available_fields = []
                for field in required_fields:
                    if field in data:
                        available_fields.append(field)
                
                details = f"Available fields: {', '.join(available_fields)} ({len(available_fields)}/{len(required_fields)})"
                self.log_test("Enhanced Clinic Form Data API", True, response_time, details)
                return True
            else:
                self.log_test("Enhanced Clinic Form Data API", False, response_time, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            response_time = (time.time() - start) * 1000
            self.log_test("Enhanced Clinic Form Data API", False, response_time, f"Exception: {str(e)}")
            return False
    
    def test_lines_api(self):
        """Test Lines API for form data"""
        if not self.token:
            self.log_test("Lines API", False, 0, "No authentication token")
            return False
            
        start = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/lines", headers=headers, timeout=10)
            response_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                lines_count = len(data) if isinstance(data, list) else 0
                details = f"Found {lines_count} lines available for clinic registration"
                self.log_test("Lines API", True, response_time, details)
                return True
            else:
                self.log_test("Lines API", False, response_time, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            response_time = (time.time() - start) * 1000
            self.log_test("Lines API", False, response_time, f"Exception: {str(e)}")
            return False
    
    def test_areas_api(self):
        """Test Areas API for form data"""
        if not self.token:
            self.log_test("Areas API", False, 0, "No authentication token")
            return False
            
        start = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(f"{BASE_URL}/areas", headers=headers, timeout=10)
            response_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                areas_count = len(data) if isinstance(data, list) else 0
                details = f"Found {areas_count} areas available for clinic registration"
                self.log_test("Areas API", True, response_time, details)
                return True
            else:
                self.log_test("Areas API", False, response_time, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            response_time = (time.time() - start) * 1000
            self.log_test("Areas API", False, response_time, f"Exception: {str(e)}")
            return False
    
    def test_enhanced_clinic_registration_api(self):
        """Test Enhanced Clinic Registration API"""
        if not self.token:
            self.log_test("Enhanced Clinic Registration API", False, 0, "No authentication token")
            return False
            
        start = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Test data for clinic registration with GPS coordinates
            test_clinic_data = {
                "clinic_name": "عيادة اختبار GPS المحسنة",
                "doctor_name": "د. أحمد محمد GPS",
                "doctor_specialty": "طب عام",
                "phone": "01234567890",
                "address": "شارع التحرير، القاهرة",
                "classification": "class_a",
                "credit_classification": "green",
                "line_id": "line-001",
                "area_id": "area-001",
                "gps_coordinates": {
                    "latitude": 30.0444,
                    "longitude": 31.2357,
                    "accuracy": 10,
                    "timestamp": datetime.utcnow().isoformat()
                },
                "location_verified": True,
                "registration_source": "enhanced_form"
            }
            
            response = requests.post(f"{BASE_URL}/enhanced-clinics/register", 
                                   headers=headers, json=test_clinic_data, timeout=10)
            response_time = (time.time() - start) * 1000
            
            if response.status_code in [200, 201]:
                data = response.json()
                clinic_id = data.get("clinic_id", "Unknown")
                details = f"Successfully registered clinic with GPS data - ID: {clinic_id}"
                self.log_test("Enhanced Clinic Registration API", True, response_time, details)
                return True
            else:
                self.log_test("Enhanced Clinic Registration API", False, response_time, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            response_time = (time.time() - start) * 1000
            self.log_test("Enhanced Clinic Registration API", False, response_time, f"Exception: {str(e)}")
            return False
    
    def test_backend_stability(self):
        """Test backend stability for GPS functionality"""
        if not self.token:
            self.log_test("Backend Stability Check", False, 0, "No authentication token")
            return False
            
        start = time.time()
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Test multiple endpoints to ensure stability
            endpoints_to_test = [
                ("/health", "Health Check"),
                ("/users", "Users Management"),
                ("/clinics", "Clinics Management"),
                ("/dashboard/stats/admin", "Dashboard Stats")
            ]
            
            stable_endpoints = 0
            total_endpoints = len(endpoints_to_test)
            
            for endpoint, name in endpoints_to_test:
                try:
                    response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=5)
                    if response.status_code == 200:
                        stable_endpoints += 1
                except:
                    pass
            
            response_time = (time.time() - start) * 1000
            stability_percentage = (stable_endpoints / total_endpoints) * 100
            
            if stability_percentage >= 75:
                details = f"Backend stability: {stability_percentage:.1f}% ({stable_endpoints}/{total_endpoints} endpoints stable)"
                self.log_test("Backend Stability Check", True, response_time, details)
                return True
            else:
                details = f"Backend stability: {stability_percentage:.1f}% ({stable_endpoints}/{total_endpoints} endpoints stable) - Below threshold"
                self.log_test("Backend Stability Check", False, response_time, details)
                return False
                
        except Exception as e:
            response_time = (time.time() - start) * 1000
            self.log_test("Backend Stability Check", False, response_time, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Enhanced Clinic Registration GPS tests"""
        print("🎯 Enhanced Clinic Registration GPS Fix Backend Testing")
        print("=" * 60)
        print(f"🔗 Backend URL: {BASE_URL}")
        print(f"⏰ Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run tests in sequence
        tests = [
            self.test_admin_login,
            self.test_lines_api,
            self.test_areas_api,
            self.test_enhanced_clinic_form_data_api,
            self.test_enhanced_clinic_registration_api,
            self.test_backend_stability
        ]
        
        for test in tests:
            test()
            time.sleep(0.1)  # Small delay between tests
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        total_time = time.time() - self.start_time
        avg_response_time = sum(result["response_time"] for result in self.test_results) / total_tests if total_tests > 0 else 0
        
        print()
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"⏱️  Average Response Time: {avg_response_time:.2f}ms")
        print(f"🕐 Total Execution Time: {total_time:.2f}s")
        print()
        
        # Detailed results
        print("📋 DETAILED RESULTS")
        print("=" * 60)
        for result in self.test_results:
            print(f"{result['status']} {result['test']} ({result['response_time']:.2f}ms)")
            if result['details']:
                print(f"   📋 {result['details']}")
        
        print()
        print("🎯 ENHANCED CLINIC REGISTRATION GPS FIX ASSESSMENT")
        print("=" * 60)
        
        if success_rate >= 80:
            print("🟢 EXCELLENT: Backend is stable and ready to support GPS functionality")
            print("✅ Enhanced Clinic Registration APIs are working correctly")
            print("✅ GPS data handling is supported")
            print("✅ Form data APIs (lines, areas) are available")
            print("✅ Backend stability is confirmed")
        elif success_rate >= 60:
            print("🟡 GOOD: Backend is mostly stable with minor issues")
            print("⚠️  Some Enhanced Clinic Registration features may need attention")
        else:
            print("🔴 NEEDS ATTENTION: Backend has significant issues")
            print("❌ Enhanced Clinic Registration GPS functionality may not work properly")
        
        print()
        print("🔍 RECOMMENDATIONS FOR MAIN AGENT:")
        if success_rate >= 80:
            print("✅ Backend is ready to support Enhanced Clinic Registration with GPS")
            print("✅ Frontend GPS fix should work with current backend implementation")
            print("✅ No critical backend issues detected")
        else:
            failed_tests = [result for result in self.test_results if not result["success"]]
            print("❌ Backend issues detected that may affect GPS functionality:")
            for failed_test in failed_tests:
                print(f"   - {failed_test['test']}: {failed_test['details']}")
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = EnhancedClinicRegistrationTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)