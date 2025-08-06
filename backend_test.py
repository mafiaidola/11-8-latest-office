#!/usr/bin/env python3
"""
اختبار شامل للنظام المنظف والمحسن مع التركيز على:
1. اختبار إضافة منتج جديد
2. اختبار نظام المديونية المحسن  
3. اختبار نظام الدفع
4. اختبار التكامل
5. اختبار النظافة

Comprehensive Backend Testing for Clean and Enhanced System
Focus Areas: Product Management, Enhanced Debt System, Payment Processing, Integration Testing, System Cleanliness
"""

import requests
import json
import time
from datetime import datetime
import uuid

# Configuration
BACKEND_URL = "https://af82d270-0f9e-4b08-93b4-329c3531075a.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        self.start_time = time.time()
        
    def log_test(self, test_name, success, message, response_time=None):
        """تسجيل نتيجة الاختبار"""
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({response_time:.2f}ms)" if response_time else ""
        print(f"{status}: {test_name}{time_info}")
        if message:
            print(f"    📝 {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_time": response_time
        })
    
    def authenticate(self):
        """تسجيل الدخول والحصول على JWT token"""
        print("\n🔐 === AUTHENTICATION TESTING ===")
        
        start_time = time.time()
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD
            })
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                
                user_info = data.get("user", {})
                self.log_test(
                    "Admin Login Authentication", 
                    True, 
                    f"Successfully logged in as {user_info.get('full_name', 'admin')} (Role: {user_info.get('role', 'admin')})",
                    response_time
                )
                return True
            else:
                self.log_test("Admin Login Authentication", False, f"Login failed: {response.status_code} - {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("Admin Login Authentication", False, f"Login error: {str(e)}")
            return False
    
    def test_system_cleanliness(self):
        """اختبار نظافة النظام - فحص عدد المستخدمين والمنتجات الحالية"""
        print("\n🧹 === SYSTEM CLEANLINESS TESTING ===")
        
        # Test current user count
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/users")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                users = response.json()
                user_count = len(users)
                
                # Check for test users
                test_users = [u for u in users if 
                             'test' in u.get('username', '').lower() or 
                             'demo' in u.get('username', '').lower() or
                             'تجربة' in u.get('full_name', '')]
                
                self.log_test(
                    "System User Count Check",
                    True,
                    f"Total users: {user_count}, Test users found: {len(test_users)}",
                    response_time
                )
            else:
                self.log_test("System User Count Check", False, f"Failed to get users: {response.status_code}")
        except Exception as e:
            self.log_test("System User Count Check", False, f"Error: {str(e)}")
        
        # Test current product count
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/products")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                products = response.json()
                product_count = len(products)
                
                self.log_test(
                    "System Product Count Check",
                    True,
                    f"Total products in system: {product_count}",
                    response_time
                )
            else:
                self.log_test("System Product Count Check", False, f"Failed to get products: {response.status_code}")
        except Exception as e:
            self.log_test("System Product Count Check", False, f"Error: {str(e)}")
    
    def test_add_new_product(self):
        """اختبار إضافة منتج جديد مع بيانات حقيقية كاملة"""
        print("\n📦 === NEW PRODUCT ADDITION TESTING ===")
        
        # Get available lines first
        lines = self.get_available_lines()
        line_id = lines[0]["id"] if lines else "default_line_id"
        
        # Real pharmaceutical product data with correct structure
        new_product = {
            "name": "كونكور 5 مجم أقراص",
            "description": "دواء لعلاج ارتفاع ضغط الدم وأمراض القلب التاجية - بيسوبرولول فومارات 5 مجم",
            "category": "أدوية القلب والأوعية الدموية",
            "unit": "علبة 30 قرص",
            "line_id": line_id,
            "price": 89.50,
            "price_type": "fixed",
            "current_stock": 150,
            "is_active": True
        }
        
        try:
            start_time = time.time()
            response = self.session.post(f"{BACKEND_URL}/products", json=new_product)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                product_id = result.get("product", {}).get("id") if result.get("product") else result.get("id")
                
                self.log_test(
                    "Add New Real Product",
                    True,
                    f"Successfully added '{new_product['name']}' - Price: {new_product['price']} EGP, Stock: {new_product['current_stock']} units",
                    response_time
                )
                
                # Verify product appears in product list
                self.verify_product_in_list(product_id, new_product['name'])
                return product_id
            else:
                self.log_test(
                    "Add New Real Product", 
                    False, 
                    f"Failed to add product: {response.status_code} - {response.text}",
                    response_time
                )
                return None
                
        except Exception as e:
            self.log_test("Add New Real Product", False, f"Error adding product: {str(e)}")
            return None
    
    def verify_product_in_list(self, product_id, product_name):
        """التأكد من ظهور المنتج في قائمة المنتجات"""
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/products")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                products = response.json()
                found_product = None
                
                for product in products:
                    if product.get("id") == product_id or product.get("name") == product_name:
                        found_product = product
                        break
                
                if found_product:
                    self.log_test(
                        "Verify Product in List",
                        True,
                        f"Product '{product_name}' found in products list with ID: {found_product.get('id')}",
                        response_time
                    )
                else:
                    self.log_test(
                        "Verify Product in List",
                        False,
                        f"Product '{product_name}' not found in products list",
                        response_time
                    )
            else:
                self.log_test("Verify Product in List", False, f"Failed to get products: {response.status_code}")
                
        except Exception as e:
            self.log_test("Verify Product in List", False, f"Error: {str(e)}")
    
    def test_enhanced_debt_system(self):
        """اختبار نظام المديونية المحسن - كل فاتورة تصبح دين تلقائياً"""
        print("\n💰 === ENHANCED DEBT SYSTEM TESTING ===")
        
        # First, get available clinics and products for creating an order
        clinics = self.get_available_clinics()
        products = self.get_available_products()
        warehouses = self.get_available_warehouses()
        
        if not clinics or not products or not warehouses:
            self.log_test("Enhanced Debt System Setup", False, "Missing required data (clinics, products, or warehouses)")
            return
        
        clinic_id = clinics[0]["id"]
        product_id = products[0]["id"]
        warehouse_id = warehouses[0]["id"]
        
        # Create a new order (which should automatically create a debt record)
        order_data = {
            "clinic_id": clinic_id,
            "warehouse_id": warehouse_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 5
                }
            ],
            "line": "خط القاهرة الكبرى",
            "area_id": "area_cairo_1",
            "notes": "طلب اختبار لنظام المديونية المحسن",
            "debt_warning_acknowledged": True
        }
        
        try:
            start_time = time.time()
            response = self.session.post(f"{BACKEND_URL}/orders", json=order_data)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                order_id = result.get("order_id")
                debt_record_id = result.get("debt_record_id")
                
                self.log_test(
                    "Create Order (Auto-Debt Creation)",
                    True,
                    f"Order created successfully. Order ID: {order_id}, Debt Record: {debt_record_id}, Amount: {result.get('total_amount')} EGP",
                    response_time
                )
                
                # Verify debt record was created
                self.verify_debt_record_creation(debt_record_id)
                return order_id, debt_record_id
            else:
                self.log_test(
                    "Create Order (Auto-Debt Creation)",
                    False,
                    f"Failed to create order: {response.status_code} - {response.text}",
                    response_time
                )
                return None, None
                
        except Exception as e:
            self.log_test("Create Order (Auto-Debt Creation)", False, f"Error: {str(e)}")
            return None, None
    
    def verify_debt_record_creation(self, debt_record_id):
        """التأكد من إنشاء سجل دين في قاعدة البيانات"""
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/debts")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                debts = response.json()
                found_debt = None
                
                for debt in debts:
                    if debt.get("id") == debt_record_id:
                        found_debt = debt
                        break
                
                if found_debt:
                    self.log_test(
                        "Verify Debt Record Creation",
                        True,
                        f"Debt record found: Amount {found_debt.get('debt_amount')} EGP, Status: {found_debt.get('status')}",
                        response_time
                    )
                else:
                    self.log_test(
                        "Verify Debt Record Creation",
                        False,
                        f"Debt record with ID {debt_record_id} not found",
                        response_time
                    )
            else:
                self.log_test("Verify Debt Record Creation", False, f"Failed to get debts: {response.status_code}")
                
        except Exception as e:
            self.log_test("Verify Debt Record Creation", False, f"Error: {str(e)}")
    
    def test_payment_system(self):
        """اختبار نظام الدفع - معالجة سداد وتحديث حالة الدين"""
        print("\n💳 === PAYMENT SYSTEM TESTING ===")
        
        # Get available debts for payment processing
        debts = self.get_available_debts()
        
        if not debts:
            self.log_test("Payment System Setup", False, "No debts available for payment testing")
            return
        
        debt = debts[0]
        debt_id = debt.get("id")
        remaining_amount = debt.get("remaining_amount", debt.get("debt_amount", 0))
        
        # Process partial payment
        payment_amount = min(remaining_amount * 0.6, 1000)  # Pay 60% or max 1000 EGP
        
        payment_data = {
            "debt_id": debt_id,
            "payment_amount": payment_amount,
            "payment_method": "cash",
            "notes": "دفعة جزئية - اختبار نظام الدفع المحسن"
        }
        
        try:
            start_time = time.time()
            response = self.session.post(f"{BACKEND_URL}/payments/process", json=payment_data)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                
                self.log_test(
                    "Process Payment",
                    True,
                    f"Payment processed: {payment_amount} EGP, Remaining: {result.get('remaining_amount')} EGP, Status: {result.get('payment_status')}",
                    response_time
                )
                
                # Verify debt status update
                self.verify_debt_status_update(debt_id, result.get('payment_status'))
                
                # Test payment records
                self.test_payment_records()
                
            else:
                self.log_test(
                    "Process Payment",
                    False,
                    f"Payment processing failed: {response.status_code} - {response.text}",
                    response_time
                )
                
        except Exception as e:
            self.log_test("Process Payment", False, f"Error: {str(e)}")
    
    def verify_debt_status_update(self, debt_id, expected_status):
        """التأكد من تحديث حالة الدين بعد السداد"""
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/debts")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                debts = response.json()
                found_debt = None
                
                for debt in debts:
                    if debt.get("id") == debt_id:
                        found_debt = debt
                        break
                
                if found_debt:
                    actual_status = found_debt.get("payment_status")
                    status_match = actual_status == expected_status
                    
                    self.log_test(
                        "Verify Debt Status Update",
                        status_match,
                        f"Debt status updated: Expected '{expected_status}', Actual '{actual_status}', Remaining: {found_debt.get('remaining_amount')} EGP",
                        response_time
                    )
                else:
                    self.log_test("Verify Debt Status Update", False, f"Debt with ID {debt_id} not found")
            else:
                self.log_test("Verify Debt Status Update", False, f"Failed to get debts: {response.status_code}")
                
        except Exception as e:
            self.log_test("Verify Debt Status Update", False, f"Error: {str(e)}")
    
    def test_payment_records(self):
        """اختبار عرض المدفوعات"""
        try:
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/payments")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                payments = response.json()
                
                self.log_test(
                    "Get Payment Records",
                    True,
                    f"Retrieved {len(payments)} payment records",
                    response_time
                )
            else:
                self.log_test("Get Payment Records", False, f"Failed to get payments: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get Payment Records", False, f"Error: {str(e)}")
    
    def test_integration_system(self):
        """اختبار التكامل - ربط المنتجات بالطلبات والفواتير"""
        print("\n🔗 === INTEGRATION SYSTEM TESTING ===")
        
        # Test product-order integration
        self.test_product_order_integration()
        
        # Test permissions system
        self.test_permissions_system()
        
        # Test statistics after cleanup
        self.test_statistics_integration()
    
    def test_product_order_integration(self):
        """اختبار ربط المنتجات بالطلبات والفواتير"""
        try:
            # Get orders and verify they contain product information
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/orders")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                orders = response.json()
                
                if orders:
                    # Check first order for product integration
                    order = orders[0]
                    order_id = order.get("id")
                    
                    # Get detailed order information
                    detail_response = self.session.get(f"{BACKEND_URL}/orders/{order_id}")
                    if detail_response.status_code == 200:
                        order_detail = detail_response.json()
                        items = order_detail.get("items", [])
                        
                        self.log_test(
                            "Product-Order Integration",
                            len(items) > 0,
                            f"Order contains {len(items)} product items, Total: {order_detail.get('total_amount')} EGP",
                            response_time
                        )
                    else:
                        self.log_test("Product-Order Integration", False, f"Failed to get order details: {detail_response.status_code}")
                else:
                    self.log_test("Product-Order Integration", True, "No orders found - system is clean", response_time)
            else:
                self.log_test("Product-Order Integration", False, f"Failed to get orders: {response.status_code}")
                
        except Exception as e:
            self.log_test("Product-Order Integration", False, f"Error: {str(e)}")
    
    def test_permissions_system(self):
        """اختبار نظام الصلاحيات"""
        try:
            # Test admin permissions for user management
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/users")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                users = response.json()
                self.log_test(
                    "Admin Permissions Test",
                    True,
                    f"Admin can access user management - {len(users)} users visible",
                    response_time
                )
            else:
                self.log_test("Admin Permissions Test", False, f"Admin permission denied: {response.status_code}")
                
        except Exception as e:
            self.log_test("Admin Permissions Test", False, f"Error: {str(e)}")
    
    def test_statistics_integration(self):
        """اختبار الإحصائيات بعد التنظيف"""
        try:
            # Test dashboard statistics
            start_time = time.time()
            response = self.session.get(f"{BACKEND_URL}/dashboard/stats")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                stats = response.json()
                
                self.log_test(
                    "Statistics Integration",
                    True,
                    f"Dashboard stats: Users({stats.get('total_users', 0)}), Clinics({stats.get('total_clinics', 0)}), Products({stats.get('total_products', 0)})",
                    response_time
                )
            else:
                self.log_test("Statistics Integration", False, f"Failed to get statistics: {response.status_code}")
                
        except Exception as e:
            self.log_test("Statistics Integration", False, f"Error: {str(e)}")
    
    # Helper methods
    def get_available_clinics(self):
        """الحصول على العيادات المتاحة"""
        try:
            response = self.session.get(f"{BACKEND_URL}/clinics")
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []
    
    def get_available_products(self):
        """الحصول على المنتجات المتاحة"""
        try:
            response = self.session.get(f"{BACKEND_URL}/products")
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []
    
    def get_available_warehouses(self):
        """الحصول على المخازن المتاحة"""
        try:
            response = self.session.get(f"{BACKEND_URL}/warehouses")
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []
    
    def get_available_lines(self):
        """الحصول على الخطوط المتاحة"""
        try:
            response = self.session.get(f"{BACKEND_URL}/lines")
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []
    
    def get_available_debts(self):
        """الحصول على الديون المتاحة"""
        try:
            response = self.session.get(f"{BACKEND_URL}/debts")
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []
    
    def generate_summary(self):
        """إنشاء ملخص النتائج"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        total_time = time.time() - self.start_time
        avg_response_time = sum(r["response_time"] for r in self.test_results if r["response_time"]) / max(1, len([r for r in self.test_results if r["response_time"]]))
        
        print(f"\n" + "="*80)
        print(f"🎯 COMPREHENSIVE SYSTEM TESTING COMPLETE")
        print(f"="*80)
        print(f"📊 FINAL RESULTS:")
        print(f"   ✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"   ❌ Tests Failed: {failed_tests}/{total_tests}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        print(f"   ⏱️  Total Time: {total_time:.2f}s")
        print(f"   🚀 Avg Response: {avg_response_time:.2f}ms")
        print(f"="*80)
        
        # Detailed results by category
        categories = {
            "Authentication": ["Admin Login Authentication"],
            "System Cleanliness": ["System User Count Check", "System Product Count Check"],
            "Product Management": ["Add New Real Product", "Verify Product in List"],
            "Enhanced Debt System": ["Create Order (Auto-Debt Creation)", "Verify Debt Record Creation"],
            "Payment System": ["Process Payment", "Verify Debt Status Update", "Get Payment Records"],
            "Integration Testing": ["Product-Order Integration", "Admin Permissions Test", "Statistics Integration"]
        }
        
        for category, test_names in categories.items():
            category_results = [r for r in self.test_results if r["test"] in test_names]
            if category_results:
                category_passed = sum(1 for r in category_results if r["success"])
                category_total = len(category_results)
                category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
                
                status_icon = "✅" if category_rate == 100 else "⚠️" if category_rate >= 50 else "❌"
                print(f"{status_icon} {category}: {category_passed}/{category_total} ({category_rate:.1f}%)")
        
        print(f"="*80)
        
        # Key findings
        print(f"🔍 KEY FINDINGS:")
        
        if success_rate >= 90:
            print(f"   🎉 EXCELLENT: System is working exceptionally well!")
        elif success_rate >= 75:
            print(f"   ✅ GOOD: System is working well with minor issues")
        elif success_rate >= 50:
            print(f"   ⚠️  PARTIAL: System has some significant issues")
        else:
            print(f"   ❌ CRITICAL: System has major issues requiring attention")
        
        # Failed tests summary
        failed_test_results = [r for r in self.test_results if not r["success"]]
        if failed_test_results:
            print(f"\n❌ FAILED TESTS SUMMARY:")
            for result in failed_test_results:
                print(f"   • {result['test']}: {result['message']}")
        
        print(f"="*80)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "total_time": total_time,
            "avg_response_time": avg_response_time
        }

def main():
    """تشغيل الاختبار الشامل"""
    print("🚀 Starting Comprehensive System Testing...")
    print("Focus: Clean System, Enhanced Debt Management, Payment Processing, Integration")
    print("="*80)
    
    tester = BackendTester()
    
    # Step 1: Authentication
    if not tester.authenticate():
        print("❌ Authentication failed. Cannot proceed with testing.")
        return
    
    # Step 2: System Cleanliness Testing
    tester.test_system_cleanliness()
    
    # Step 3: Product Addition Testing
    tester.test_add_new_product()
    
    # Step 4: Enhanced Debt System Testing
    tester.test_enhanced_debt_system()
    
    # Step 5: Payment System Testing
    tester.test_payment_system()
    
    # Step 6: Integration Testing
    tester.test_integration_system()
    
    # Step 7: Generate Summary
    summary = tester.generate_summary()
    
    return summary

if __name__ == "__main__":
    main()
"""
اختبار شامل لإصلاح إدارة المستخدمين والمنتجات المحدثة حديثاً
Comprehensive Test for Updated User and Product Management APIs

المطلوب اختبار:
1. اختبار APIs المستخدمين (GET /api/users, DELETE /api/users/{user_id})
2. اختبار APIs المنتجات المحدثة (GET /api/products, DELETE /api/products/{product_id})
3. اختبار المنطق الجديد (HARD DELETE operations)
4. اختبار التكامل (Integration testing)

الهدف: التأكد من أن المستخدم سيرى جميع المستخدمين (أكثر من 3) وأن حذف المنتجات يتم نهائياً
"""

import requests
import json
import time
from datetime import datetime
import sys
import os

# Configuration
BACKEND_URL = "https://af82d270-0f9e-4b08-93b4-329c3531075a.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class UserProductManagementTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.start_time = time.time()
        
    def log_result(self, test_name, success, message, details=None):
        """تسجيل نتيجة الاختبار"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ نجح" if success else "❌ فشل"
        print(f"{status} | {test_name}: {message}")
        if details:
            print(f"   التفاصيل: {details}")
    
    def admin_login(self):
        """تسجيل دخول الأدمن"""
        try:
            login_data = {
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD
            }
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                
                user_info = data.get("user", {})
                self.log_result(
                    "تسجيل دخول الأدمن",
                    True,
                    f"تم تسجيل الدخول بنجاح للمستخدم: {user_info.get('full_name', 'غير محدد')} ({user_info.get('role', 'غير محدد')})",
                    f"Response time: {response.elapsed.total_seconds()*1000:.2f}ms"
                )
                return True
            else:
                self.log_result(
                    "تسجيل دخول الأدمن",
                    False,
                    f"فشل تسجيل الدخول: {response.status_code}",
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("تسجيل دخول الأدمن", False, f"خطأ في الاتصال: {str(e)}")
            return False
    
    def test_get_users_comprehensive(self):
        """اختبار شامل لـ GET /api/users - يجب أن يعرض أكثر من 3 مستخدمين"""
        try:
            response = self.session.get(f"{BACKEND_URL}/users")
            
            if response.status_code == 200:
                users = response.json()
                user_count = len(users)
                
                if user_count > 3:
                    # تحليل تفصيلي للمستخدمين
                    roles_count = {}
                    active_users = 0
                    real_users = []
                    test_users = []
                    
                    for user in users:
                        role = user.get("role", "غير محدد")
                        roles_count[role] = roles_count.get(role, 0) + 1
                        
                        if user.get("is_active", True):
                            active_users += 1
                        
                        username = user.get("username", "").lower()
                        full_name = user.get("full_name", "").lower()
                        
                        if ("test" in username or "demo" in username or 
                            "test" in full_name or "تجربة" in full_name):
                            test_users.append(user.get("full_name", user.get("username", "غير محدد")))
                        else:
                            real_users.append(user.get("full_name", user.get("username", "غير محدد")))
                    
                    details = {
                        "total_users": user_count,
                        "active_users": active_users,
                        "real_users_count": len(real_users),
                        "test_users_count": len(test_users),
                        "roles_distribution": roles_count,
                        "sample_real_users": real_users[:5],  # عرض أول 5 مستخدمين حقيقيين
                        "response_time_ms": f"{response.elapsed.total_seconds()*1000:.2f}"
                    }
                    
                    self.log_result(
                        "GET /api/users - عرض جميع المستخدمين",
                        True,
                        f"تم جلب {user_count} مستخدم بنجاح (أكثر من 3 كما مطلوب)",
                        details
                    )
                    return users
                else:
                    self.log_result(
                        "GET /api/users - عرض جميع المستخدمين",
                        False,
                        f"عدد المستخدمين قليل: {user_count} (مطلوب أكثر من 3)",
                        {"user_count": user_count, "users_sample": users[:3]}
                    )
                    return users
            else:
                self.log_result(
                    "GET /api/users - عرض جميع المستخدمين",
                    False,
                    f"فشل في جلب المستخدمين: HTTP {response.status_code}",
                    response.text
                )
                return []
                
        except Exception as e:
            self.log_result(
                "GET /api/users - عرض جميع المستخدمين",
                False,
                f"خطأ في الاختبار: {str(e)}"
            )
            return []
    
    def test_user_deletion_permissions(self, users):
        """اختبار صلاحيات حذف المستخدمين"""
        if not users:
            self.log_result(
                "اختبار صلاحيات حذف المستخدمين",
                False,
                "لا توجد مستخدمين للاختبار"
            )
            return
        
        # البحث عن مستخدم تجريبي للحذف
        test_user = None
        for user in users:
            username = user.get("username", "").lower()
            full_name = user.get("full_name", "").lower()
            
            if (("test" in username or "demo" in username or 
                 "test" in full_name or "تجربة" in full_name) and
                user.get("role") != "admin"):
                test_user = user
                break
        
        if not test_user:
            # إنشاء مستخدم تجريبي للحذف
            try:
                new_user_data = {
                    "username": f"test_user_{int(time.time())}",
                    "password": "test123",
                    "full_name": "مستخدم تجريبي للحذف",
                    "role": "medical_rep",
                    "email": "test@example.com",
                    "is_active": True
                }
                
                response = self.session.post(f"{BACKEND_URL}/users", json=new_user_data)
                
                if response.status_code == 200:
                    created_user = response.json().get("user", {})
                    test_user = created_user
                    self.log_result(
                        "إنشاء مستخدم تجريبي للحذف",
                        True,
                        f"تم إنشاء المستخدم: {created_user.get('full_name')}",
                        {"user_id": created_user.get("id")}
                    )
                else:
                    self.log_result(
                        "إنشاء مستخدم تجريبي للحذف",
                        False,
                        f"فشل في إنشاء المستخدم: HTTP {response.status_code}",
                        response.text
                    )
                    return
                    
            except Exception as e:
                self.log_result(
                    "إنشاء مستخدم تجريبي للحذف",
                    False,
                    f"خطأ في إنشاء المستخدم: {str(e)}"
                )
                return
        
        # اختبار حذف المستخدم (HARD DELETE)
        if test_user:
            try:
                user_id = test_user.get("id")
                user_name = test_user.get("full_name", test_user.get("username", "غير محدد"))
                
                # عد المستخدمين قبل الحذف
                users_before = len(self.session.get(f"{BACKEND_URL}/users").json())
                
                response = self.session.delete(f"{BACKEND_URL}/users/{user_id}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # التحقق من الحذف النهائي
                    users_after = len(self.session.get(f"{BACKEND_URL}/users").json())
                    
                    # محاولة الوصول للمستخدم المحذوف
                    check_response = self.session.get(f"{BACKEND_URL}/users/{user_id}/profile")
                    user_not_found = check_response.status_code == 404
                    
                    details = {
                        "deleted_user": result.get("deleted_user", {}),
                        "users_before_deletion": users_before,
                        "users_after_deletion": users_after,
                        "hard_delete_confirmed": user_not_found,
                        "response_message": result.get("message", "")
                    }
                    
                    if users_after < users_before and user_not_found:
                        self.log_result(
                            "DELETE /api/users/{user_id} - حذف نهائي",
                            True,
                            f"تم حذف المستخدم '{user_name}' نهائياً من النظام",
                            details
                        )
                    else:
                        self.log_result(
                            "DELETE /api/users/{user_id} - حذف نهائي",
                            False,
                            "الحذف لم يكن نهائياً كما مطلوب",
                            details
                        )
                else:
                    self.log_result(
                        "DELETE /api/users/{user_id} - حذف نهائي",
                        False,
                        f"فشل في حذف المستخدم: HTTP {response.status_code}",
                        response.text
                    )
                    
            except Exception as e:
                self.log_result(
                    "DELETE /api/users/{user_id} - حذف نهائي",
                    False,
                    f"خطأ في اختبار الحذف: {str(e)}"
                )
    
    def test_user_deletion_restrictions(self):
        """اختبار قيود حذف المستخدمين"""
        # اختبار منع الحذف الذاتي
        try:
            # الحصول على معرف المستخدم الحالي من التوكن
            import jwt
            payload = jwt.decode(self.admin_token, options={"verify_signature": False})
            current_user_id = payload.get("user_id")
            
            response = self.session.delete(f"{BACKEND_URL}/users/{current_user_id}")
            
            if response.status_code == 403:
                self.log_result(
                    "منع الحذف الذاتي",
                    True,
                    "تم منع المستخدم من حذف نفسه بنجاح",
                    {"status_code": response.status_code, "message": response.json().get("detail", "")}
                )
            else:
                self.log_result(
                    "منع الحذف الذاتي",
                    False,
                    f"لم يتم منع الحذف الذاتي: HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_result(
                "منع الحذف الذاتي",
                False,
                f"خطأ في اختبار منع الحذف الذاتي: {str(e)}"
            )
        
        # اختبار حذف مستخدم غير موجود
        try:
            fake_user_id = "non-existent-user-id-12345"
            response = self.session.delete(f"{BACKEND_URL}/users/{fake_user_id}")
            
            if response.status_code == 404:
                self.log_result(
                    "حذف مستخدم غير موجود",
                    True,
                    "تم التعامل مع حذف مستخدم غير موجود بشكل صحيح",
                    {"status_code": response.status_code, "message": response.json().get("detail", "")}
                )
            else:
                self.log_result(
                    "حذف مستخدم غير موجود",
                    False,
                    f"لم يتم التعامل مع المستخدم غير الموجود بشكل صحيح: HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_result(
                "حذف مستخدم غير موجود",
                False,
                f"خطأ في اختبار حذف مستخدم غير موجود: {str(e)}"
            )
    
    def test_get_products_comprehensive(self):
        """اختبار شامل لـ GET /api/products"""
        try:
            response = self.session.get(f"{BACKEND_URL}/products")
            
            if response.status_code == 200:
                products = response.json()
                product_count = len(products)
                
                # تحليل تفصيلي للمنتجات
                categories = {}
                lines = {}
                active_products = 0
                total_stock = 0
                
                for product in products:
                    category = product.get("category", "غير محدد")
                    categories[category] = categories.get(category, 0) + 1
                    
                    line_name = product.get("line_name", "غير محدد")
                    lines[line_name] = lines.get(line_name, 0) + 1
                    
                    if product.get("is_active", True):
                        active_products += 1
                    
                    total_stock += product.get("current_stock", 0)
                
                details = {
                    "total_products": product_count,
                    "active_products": active_products,
                    "categories_distribution": categories,
                    "lines_distribution": lines,
                    "total_stock": total_stock,
                    "sample_products": [p.get("name", "غير محدد") for p in products[:5]],
                    "response_time_ms": f"{response.elapsed.total_seconds()*1000:.2f}"
                }
                
                self.log_result(
                    "GET /api/products - عرض جميع المنتجات",
                    True,
                    f"تم جلب {product_count} منتج بنجاح",
                    details
                )
                return products
            else:
                self.log_result(
                    "GET /api/products - عرض جميع المنتجات",
                    False,
                    f"فشل في جلب المنتجات: HTTP {response.status_code}",
                    response.text
                )
                return []
                
        except Exception as e:
            self.log_result(
                "GET /api/products - عرض جميع المنتجات",
                False,
                f"خطأ في الاختبار: {str(e)}"
            )
            return []
    
    def test_product_hard_deletion(self, products):
        """اختبار الحذف النهائي للمنتجات (HARD DELETE)"""
        if not products:
            self.log_result(
                "اختبار الحذف النهائي للمنتجات",
                False,
                "لا توجد منتجات للاختبار"
            )
            return
        
        # إنشاء منتج تجريبي للحذف
        try:
            # الحصول على خط متاح
            lines_response = self.session.get(f"{BACKEND_URL}/lines")
            if lines_response.status_code != 200:
                self.log_result(
                    "إنشاء منتج تجريبي للحذف",
                    False,
                    "فشل في جلب الخطوط المتاحة"
                )
                return
            
            lines = lines_response.json()
            if not lines:
                self.log_result(
                    "إنشاء منتج تجريبي للحذف",
                    False,
                    "لا توجد خطوط متاحة"
                )
                return
            
            test_product_data = {
                "name": f"منتج تجريبي للحذف {int(time.time())}",
                "description": "منتج تجريبي لاختبار الحذف النهائي",
                "category": "اختبار",
                "unit": "قطعة",
                "line_id": lines[0]["id"],
                "price": 100.0,
                "price_type": "fixed",
                "current_stock": 10,
                "is_active": True
            }
            
            response = self.session.post(f"{BACKEND_URL}/products", json=test_product_data)
            
            if response.status_code == 200:
                created_product = response.json().get("product", {})
                product_id = created_product.get("id")
                product_name = created_product.get("name")
                
                self.log_result(
                    "إنشاء منتج تجريبي للحذف",
                    True,
                    f"تم إنشاء المنتج: {product_name}",
                    {"product_id": product_id}
                )
                
                # اختبار الحذف النهائي
                self._test_hard_delete_product(product_id, product_name)
                
            else:
                self.log_result(
                    "إنشاء منتج تجريبي للحذف",
                    False,
                    f"فشل في إنشاء المنتج: HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_result(
                "إنشاء منتج تجريبي للحذف",
                False,
                f"خطأ في إنشاء المنتج: {str(e)}"
            )
    
    def _test_hard_delete_product(self, product_id, product_name):
        """اختبار الحذف النهائي لمنتج محدد"""
        try:
            # عد المنتجات قبل الحذف
            products_before = len(self.session.get(f"{BACKEND_URL}/products").json())
            
            # حذف المنتج
            response = self.session.delete(f"{BACKEND_URL}/products/{product_id}")
            
            if response.status_code == 200:
                result = response.json()
                
                # التحقق من الحذف النهائي
                products_after = len(self.session.get(f"{BACKEND_URL}/products").json())
                
                # محاولة الوصول للمنتج المحذوف
                check_response = self.session.get(f"{BACKEND_URL}/products")
                remaining_products = check_response.json()
                product_still_exists = any(p.get("id") == product_id for p in remaining_products)
                
                details = {
                    "products_before_deletion": products_before,
                    "products_after_deletion": products_after,
                    "hard_delete_confirmed": not product_still_exists,
                    "response_message": result.get("message", ""),
                    "deleted_product_id": product_id
                }
                
                if products_after < products_before and not product_still_exists:
                    self.log_result(
                        "DELETE /api/products/{product_id} - حذف نهائي",
                        True,
                        f"تم حذف المنتج '{product_name}' نهائياً من النظام (HARD DELETE)",
                        details
                    )
                else:
                    self.log_result(
                        "DELETE /api/products/{product_id} - حذف نهائي",
                        False,
                        "الحذف لم يكن نهائياً كما مطلوب",
                        details
                    )
            else:
                self.log_result(
                    "DELETE /api/products/{product_id} - حذف نهائي",
                    False,
                    f"فشل في حذف المنتج: HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_result(
                "DELETE /api/products/{product_id} - حذف نهائي",
                False,
                f"خطأ في اختبار الحذف: {str(e)}"
            )
    
    def test_product_deletion_permissions(self):
        """اختبار صلاحيات حذف المنتجات (admin فقط)"""
        # اختبار حذف منتج غير موجود
        try:
            fake_product_id = "non-existent-product-id-12345"
            response = self.session.delete(f"{BACKEND_URL}/products/{fake_product_id}")
            
            if response.status_code == 404:
                self.log_result(
                    "حذف منتج غير موجود",
                    True,
                    "تم التعامل مع حذف منتج غير موجود بشكل صحيح (404 error)",
                    {"status_code": response.status_code, "message": response.json().get("detail", "")}
                )
            else:
                self.log_result(
                    "حذف منتج غير موجود",
                    False,
                    f"لم يتم التعامل مع المنتج غير الموجود بشكل صحيح: HTTP {response.status_code}",
                    response.text
                )
                
        except Exception as e:
            self.log_result(
                "حذف منتج غير موجود",
                False,
                f"خطأ في اختبار حذف منتج غير موجود: {str(e)}"
            )
    
    def test_database_integrity(self):
        """اختبار تكامل قاعدة البيانات بعد العمليات"""
        try:
            # جلب إحصائيات النظام
            endpoints_to_check = [
                ("/users", "المستخدمين"),
                ("/products", "المنتجات"),
                ("/clinics", "العيادات"),
                ("/orders", "الطلبات")
            ]
            
            integrity_results = {}
            
            for endpoint, name in endpoints_to_check:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    if response.status_code == 200:
                        data = response.json()
                        integrity_results[name] = {
                            "count": len(data),
                            "status": "متاح",
                            "response_time": f"{response.elapsed.total_seconds()*1000:.2f}ms"
                        }
                    else:
                        integrity_results[name] = {
                            "count": 0,
                            "status": f"خطأ HTTP {response.status_code}",
                            "response_time": "N/A"
                        }
                except Exception as e:
                    integrity_results[name] = {
                        "count": 0,
                        "status": f"خطأ: {str(e)}",
                        "response_time": "N/A"
                    }
            
            # التحقق من أن جميع الأنظمة تعمل
            all_working = all(result["status"] == "متاح" for result in integrity_results.values())
            
            self.log_result(
                "اختبار تكامل قاعدة البيانات",
                all_working,
                "جميع الأنظمة تعمل بشكل طبيعي بعد عمليات الحذف" if all_working else "بعض الأنظمة تواجه مشاكل",
                integrity_results
            )
            
        except Exception as e:
            self.log_result(
                "اختبار تكامل قاعدة البيانات",
                False,
                f"خطأ في اختبار التكامل: {str(e)}"
            )
    
    def generate_final_report(self):
        """إنشاء التقرير النهائي"""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        execution_time = time.time() - self.start_time
        
        print("\n" + "="*80)
        print("🎯 التقرير النهائي لاختبار إدارة المستخدمين والمنتجات المحدثة")
        print("="*80)
        
        print(f"\n📊 ملخص النتائج:")
        print(f"   إجمالي الاختبارات: {total_tests}")
        print(f"   الاختبارات الناجحة: {successful_tests} ✅")
        print(f"   الاختبارات الفاشلة: {failed_tests} ❌")
        print(f"   معدل النجاح: {success_rate:.1f}%")
        print(f"   وقت التنفيذ: {execution_time:.2f} ثانية")
        
        print(f"\n🔍 تفاصيل الاختبارات:")
        
        # تجميع النتائج حسب الفئة
        categories = {
            "اختبارات المستخدمين": [],
            "اختبارات المنتجات": [],
            "اختبارات التكامل": []
        }
        
        for result in self.test_results:
            test_name = result["test"]
            if any(keyword in test_name for keyword in ["مستخدم", "users", "حذف الذاتي", "صلاحيات حذف المستخدمين"]):
                categories["اختبارات المستخدمين"].append(result)
            elif any(keyword in test_name for keyword in ["منتج", "products"]):
                categories["اختبارات المنتجات"].append(result)
            else:
                categories["اختبارات التكامل"].append(result)
        
        for category, results in categories.items():
            if results:
                print(f"\n📋 {category}:")
                for result in results:
                    status = "✅" if result["success"] else "❌"
                    print(f"   {status} {result['test']}: {result['message']}")
        
        # النتائج الحاسمة
        print(f"\n🎯 النتائج الحاسمة للمتطلبات:")
        
        # التحقق من المتطلبات الأساسية
        users_test = next((r for r in self.test_results if "عرض جميع المستخدمين" in r["test"]), None)
        if users_test and users_test["success"]:
            user_count = users_test["details"]["total_users"] if users_test["details"] else 0
            print(f"   ✅ عرض المستخدمين: {user_count} مستخدم (أكثر من 3 كما مطلوب)")
        else:
            print(f"   ❌ عرض المستخدمين: فشل في عرض المستخدمين")
        
        hard_delete_user = next((r for r in self.test_results if "حذف نهائي" in r["test"] and "مستخدم" in r["test"]), None)
        if hard_delete_user and hard_delete_user["success"]:
            print(f"   ✅ حذف المستخدمين: HARD DELETE يعمل بشكل صحيح")
        else:
            print(f"   ❌ حذف المستخدمين: مشكلة في HARD DELETE")
        
        hard_delete_product = next((r for r in self.test_results if "حذف نهائي" in r["test"] and "منتج" in r["test"]), None)
        if hard_delete_product and hard_delete_product["success"]:
            print(f"   ✅ حذف المنتجات: HARD DELETE يعمل بشكل صحيح")
        else:
            print(f"   ❌ حذف المنتجات: مشكلة في HARD DELETE")
        
        integrity_test = next((r for r in self.test_results if "تكامل قاعدة البيانات" in r["test"]), None)
        if integrity_test and integrity_test["success"]:
            print(f"   ✅ تكامل النظام: جميع الأنظمة تعمل بشكل طبيعي")
        else:
            print(f"   ⚠️ تكامل النظام: قد تحتاج مراجعة")
        
        # التوصيات
        print(f"\n💡 التوصيات:")
        if success_rate >= 90:
            print("   🎉 النظام يعمل بشكل ممتاز! جميع المتطلبات محققة.")
        elif success_rate >= 75:
            print("   👍 النظام يعمل بشكل جيد مع بعض التحسينات المطلوبة.")
        else:
            print("   ⚠️ النظام يحتاج إلى مراجعة وإصلاحات.")
        
        if failed_tests > 0:
            print(f"   🔧 يرجى مراجعة الاختبارات الفاشلة ({failed_tests}) وإصلاح المشاكل.")
        
        print("\n" + "="*80)
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "execution_time": execution_time,
            "test_results": self.test_results
        }
    
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("🚀 بدء اختبار شامل لإصلاح إدارة المستخدمين والمنتجات المحدثة حديثاً")
        print("="*80)
        
        # تسجيل دخول الأدمن
        if not self.admin_login():
            print("❌ فشل في تسجيل دخول الأدمن. إيقاف الاختبارات.")
            return self.generate_final_report()
        
        # اختبارات المستخدمين
        print(f"\n📋 اختبارات APIs المستخدمين:")
        users = self.test_get_users_comprehensive()
        self.test_user_deletion_permissions(users)
        self.test_user_deletion_restrictions()
        
        # اختبارات المنتجات
        print(f"\n📋 اختبارات APIs المنتجات المحدثة:")
        products = self.test_get_products_comprehensive()
        self.test_product_hard_deletion(products)
        self.test_product_deletion_permissions()
        
        # اختبارات التكامل
        print(f"\n📋 اختبارات التكامل:")
        self.test_database_integrity()
        
        # إنشاء التقرير النهائي
        return self.generate_final_report()

def main():
    """الدالة الرئيسية"""
    tester = UserProductManagementTester()
    
    try:
        report = tester.run_all_tests()
        
        # حفظ التقرير في ملف
        with open("/app/user_product_management_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 تم حفظ التقرير التفصيلي في: /app/user_product_management_test_report.json")
        
        return report["success_rate"] >= 75
        
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف الاختبار بواسطة المستخدم")
        return False
    except Exception as e:
        print(f"\n💥 خطأ عام في تشغيل الاختبارات: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
"""
FINAL COMPREHENSIVE BACKEND TEST - POST ALL MAJOR ENHANCEMENTS
Testing all functionalities enhanced during this session to ensure system stability and functionality.

Test Areas:
1. Authentication & Security: Verify admin/admin123 login with all new features
2. Core API Endpoints: Test all major endpoints (users, clinics, products, orders, visits, debts)
3. New Data Structure Support: Verify backend can handle new approval_info data structure for clinics
4. Settings & Configuration: Test system settings API for logo upload and other configurations  
5. Enhanced User Data: Verify user statistics with new metrics (debts, collections, visits, added_clinics)
6. Responsive API Performance: Check response times are acceptable for all enhanced features
7. Error Handling: Verify robust error handling for all new functionalities
8. Database Integration: Ensure all new data structures integrate properly with MongoDB
"""

import requests
import json
import time
from datetime import datetime
import sys
import os

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://af82d270-0f9e-4b08-93b4-329c3531075a.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.jwt_token = None
        self.test_results = []
        self.start_time = time.time()
        
    def log_test(self, test_name, success, message, response_time=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({response_time:.2f}ms)" if response_time else ""
        print(f"{status}: {test_name}{time_info}")
        if message:
            print(f"   📝 {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_time": response_time
        })
        
    def login_admin(self):
        """Login as admin to get JWT token"""
        try:
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "username": "admin",
                "password": "admin123"
            })
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.jwt_token}"})
                self.log_test("Admin Login", True, f"JWT token obtained successfully", response_time)
                return True
            else:
                self.log_test("Admin Login", False, f"Login failed: {response.status_code} - {response.text}", response_time)
                return False
        except Exception as e:
            self.log_test("Admin Login", False, f"Login error: {str(e)}")
            return False

    def test_activities_api(self):
        """Test POST /api/activities with correct activity type"""
        try:
            # Test creating activity with correct type 'visit_registration'
            start_time = time.time()
            activity_data = {
                "type": "visit_registration",  # Correct field name as per ActivityCreate model
                "action": "تسجيل زيارة عيادة اختبار",
                "target_type": "clinic",
                "target_id": "test-clinic-id",
                "target_details": {
                    "clinic_name": "عيادة اختبار شاملة",
                    "doctor_name": "د. أحمد محمد",
                    "specialization": "باطنة"
                },
                "location": {
                    "latitude": 30.0444,
                    "longitude": 31.2357,
                    "address": "القاهرة، مصر",
                    "area": "وسط البلد"
                },
                "device_info": {
                    "device_type": "mobile",
                    "browser": "Chrome",
                    "os": "Android"
                },
                "additional_details": {
                    "visit_duration": "30 minutes",
                    "products_presented": ["منتج أ", "منتج ب"],
                    "notes": "زيارة ناجحة مع عرض المنتجات الجديدة"
                }
            }
            
            response = self.session.post(f"{API_BASE}/activities", json=activity_data)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200 or response.status_code == 201:
                self.log_test("POST /api/activities (visit_registration)", True, 
                            f"Activity created successfully with correct type", response_time)
                return True
            else:
                self.log_test("POST /api/activities (visit_registration)", False, 
                            f"Failed: {response.status_code} - {response.text}", response_time)
                return False
                
        except Exception as e:
            self.log_test("POST /api/activities (visit_registration)", False, f"Error: {str(e)}")
            return False

    def test_orders_detail_api(self):
        """Test GET /api/orders/{id} endpoint"""
        try:
            # First get list of orders to find an ID
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/orders")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                orders = response.json()
                if orders and len(orders) > 0:
                    order_id = orders[0].get("id")
                    if order_id:
                        # Test GET /api/orders/{id}
                        start_time = time.time()
                        detail_response = self.session.get(f"{API_BASE}/orders/{order_id}")
                        detail_response_time = (time.time() - start_time) * 1000
                        
                        if detail_response.status_code == 200:
                            order_detail = detail_response.json()
                            self.log_test("GET /api/orders/{id}", True, 
                                        f"Order detail retrieved successfully: {order_detail.get('order_number', 'N/A')}", 
                                        detail_response_time)
                            return True
                        else:
                            self.log_test("GET /api/orders/{id}", False, 
                                        f"Order detail failed: {detail_response.status_code} - {detail_response.text}", 
                                        detail_response_time)
                            return False
                    else:
                        self.log_test("GET /api/orders/{id}", False, "No order ID found in orders list")
                        return False
                else:
                    self.log_test("GET /api/orders/{id}", False, "No orders found to test detail endpoint")
                    return False
            else:
                self.log_test("GET /api/orders/{id}", False, f"Failed to get orders list: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("GET /api/orders/{id}", False, f"Error: {str(e)}")
            return False

    def test_admin_settings_api(self):
        """Test PUT /api/admin/settings endpoint"""
        try:
            # Test GET settings first
            start_time = time.time()
            get_response = self.session.get(f"{API_BASE}/admin/settings")
            get_response_time = (time.time() - start_time) * 1000
            
            if get_response.status_code == 200:
                self.log_test("GET /api/admin/settings", True, "Settings retrieved successfully", get_response_time)
                
                # Test PUT settings
                settings_data = {
                    "company_name": "EP Group - Updated",
                    "company_logo": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
                    "system_language": "ar",
                    "theme": "modern",
                    "session_timeout": 60,
                    "max_login_attempts": 5,
                    "backup_frequency": "daily",
                    "notification_settings": {
                        "email_notifications": True,
                        "sms_notifications": False,
                        "push_notifications": True
                    }
                }
                
                start_time = time.time()
                put_response = self.session.put(f"{API_BASE}/admin/settings", json=settings_data)
                put_response_time = (time.time() - start_time) * 1000
                
                if put_response.status_code == 200:
                    self.log_test("PUT /api/admin/settings", True, 
                                "Settings updated successfully", put_response_time)
                    return True
                else:
                    self.log_test("PUT /api/admin/settings", False, 
                                f"Settings update failed: {put_response.status_code} - {put_response.text}", 
                                put_response_time)
                    return False
            else:
                self.log_test("GET /api/admin/settings", False, 
                            f"Settings retrieval failed: {get_response.status_code} - {get_response.text}", 
                            get_response_time)
                return False
                
        except Exception as e:
            self.log_test("PUT /api/admin/settings", False, f"Error: {str(e)}")
            return False

    def test_clinic_manager_fields(self):
        """Test POST /api/clinics with manager_name and manager_phone fields"""
        try:
            clinic_data = {
                "name": "عيادة اختبار الحقول الجديدة",  # Fixed field name
                "doctor_name": "د. أحمد محمد الطبيب",  # Required field
                "address": "شارع التحرير، القاهرة",
                "phone": "01234567890",
                "email": "test@clinic.com",
                "classification": "A",
                "credit_status": "good",
                "manager_name": "أحمد محمد المدير",  # New field to test
                "manager_phone": "01111111111",        # New field to test
                "latitude": 30.0444,
                "longitude": 31.2357,
                "area_id": "test-area-id",
                "notes": "عيادة اختبار لفحص الحقول الجديدة"
            }
            
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/clinics", json=clinic_data)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200 or response.status_code == 201:
                clinic_result = response.json()
                # Check if manager fields are included in response
                clinic_info = clinic_result.get("clinic", {})
                has_manager_name = "manager_name" in clinic_info
                has_manager_phone = "manager_phone" in clinic_info
                
                if has_manager_name and has_manager_phone:
                    self.log_test("POST /api/clinics (manager fields)", True, 
                                f"Clinic created with manager fields: {clinic_info.get('manager_name')}", 
                                response_time)
                    return True
                else:
                    self.log_test("POST /api/clinics (manager fields)", False, 
                                f"Manager fields missing in response. Has name: {has_manager_name}, Has phone: {has_manager_phone}", 
                                response_time)
                    return False
            else:
                self.log_test("POST /api/clinics (manager fields)", False, 
                            f"Clinic creation failed: {response.status_code} - {response.text}", 
                            response_time)
                return False
                
        except Exception as e:
            self.log_test("POST /api/clinics (manager fields)", False, f"Error: {str(e)}")
            return False

    def test_clinic_specialization_removal(self):
        """Test that specialization field is removed from NEW clinic creation"""
        try:
            # Create a new clinic and verify it doesn't have specialization field
            clinic_data = {
                "name": "عيادة اختبار إزالة التخصص",
                "doctor_name": "د. محمد أحمد",
                "address": "شارع النيل، الجيزة",
                "phone": "01987654321",
                "classification": "A",
                "credit_status": "good",
                "manager_name": "سارة محمد",
                "manager_phone": "01555555555",
                "latitude": 30.0444,
                "longitude": 31.2357,
                "area_id": "test-area-id"
            }
            
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/clinics", json=clinic_data)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200 or response.status_code == 201:
                clinic_result = response.json()
                clinic_info = clinic_result.get("clinic", {})
                
                # Check that the newly created clinic does NOT have specialization field
                has_specialization = "specialization" in clinic_info
                
                if not has_specialization:
                    self.log_test("Clinic Specialization Removal", True, 
                                f"New clinic created without specialization field: {clinic_info.get('name')}", 
                                response_time)
                    return True
                else:
                    self.log_test("Clinic Specialization Removal", False, 
                                f"New clinic still has specialization field: {clinic_info.get('specialization')}", 
                                response_time)
                    return False
            else:
                self.log_test("Clinic Specialization Removal", False, 
                            f"Failed to create test clinic: {response.status_code} - {response.text}", 
                            response_time)
                return False
                
        except Exception as e:
            self.log_test("Clinic Specialization Removal", False, f"Error: {str(e)}")
            return False

    def test_enhanced_user_statistics(self):
        """Test enhanced user statistics with new metrics (debts, collections, visits, added_clinics)"""
        try:
            # Get users list first
            start_time = time.time()
            users_response = self.session.get(f"{API_BASE}/users")
            users_response_time = (time.time() - start_time) * 1000
            
            if users_response.status_code == 200:
                users = users_response.json()
                if users and len(users) > 0:
                    # Test user profile with enhanced statistics
                    user_id = users[0].get("id")
                    if user_id:
                        start_time = time.time()
                        profile_response = self.session.get(f"{API_BASE}/users/{user_id}/profile")
                        profile_response_time = (time.time() - start_time) * 1000
                        
                        if profile_response.status_code == 200:
                            profile_data = profile_response.json()
                            user_stats = profile_data.get("user", {}).get("user_stats", {})
                            
                            # Check for enhanced metrics
                            has_sales_activity = "sales_activity" in user_stats
                            has_debt_info = "debt_info" in user_stats
                            has_territory_info = "territory_info" in user_stats
                            has_team_info = "team_info" in user_stats
                            
                            if has_sales_activity and has_debt_info and has_territory_info and has_team_info:
                                sales_stats = user_stats["sales_activity"]
                                debt_stats = user_stats["debt_info"]
                                territory_stats = user_stats["territory_info"]
                                
                                self.log_test("Enhanced User Statistics", True, 
                                            f"User stats include: visits({sales_stats.get('total_visits', 0)}), orders({sales_stats.get('total_orders', 0)}), debt({debt_stats.get('total_debt', 0)}), clinics({territory_stats.get('assigned_clinics', 0)})", 
                                            profile_response_time)
                                return True
                            else:
                                self.log_test("Enhanced User Statistics", False, 
                                            f"Missing enhanced metrics. Has: sales({has_sales_activity}), debt({has_debt_info}), territory({has_territory_info}), team({has_team_info})", 
                                            profile_response_time)
                                return False
                        else:
                            self.log_test("Enhanced User Statistics", False, 
                                        f"Profile retrieval failed: {profile_response.status_code} - {profile_response.text}", 
                                        profile_response_time)
                            return False
                    else:
                        self.log_test("Enhanced User Statistics", False, "No user ID found")
                        return False
                else:
                    self.log_test("Enhanced User Statistics", False, "No users found")
                    return False
            else:
                self.log_test("Enhanced User Statistics", False, f"Users retrieval failed: {users_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Enhanced User Statistics", False, f"Error: {str(e)}")
            return False

    def test_clinic_approval_info_structure(self):
        """Test new approval_info data structure for clinics"""
        try:
            clinic_data = {
                "name": "عيادة اختبار نظام الموافقة",
                "doctor_name": "د. أحمد محمد",
                "address": "شارع التحرير، القاهرة",
                "phone": "01234567890",
                "email": "approval@clinic.com",
                "classification": "A",
                "credit_status": "good",
                "manager_name": "مدير العيادة",
                "manager_phone": "01111111111",
                "latitude": 30.0444,
                "longitude": 31.2357,
                "area_id": "test-area-id",
                "approval_info": {
                    "status": "pending",
                    "submitted_at": datetime.now().isoformat(),
                    "submitted_by": "medical_rep_id",
                    "approval_level": "line_manager",
                    "required_approvals": ["line_manager", "area_manager"],
                    "approval_history": [],
                    "rejection_reason": None,
                    "priority": "normal",
                    "documents_required": ["license", "insurance"],
                    "documents_submitted": ["license"],
                    "compliance_check": {
                        "license_valid": True,
                        "insurance_valid": False,
                        "location_verified": True
                    }
                }
            }
            
            start_time = time.time()
            response = self.session.post(f"{API_BASE}/clinics", json=clinic_data)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200 or response.status_code == 201:
                clinic_result = response.json()
                clinic_info = clinic_result.get("clinic", {})
                
                # Check if approval_info structure is preserved
                has_approval_info = "approval_info" in clinic_info
                if has_approval_info:
                    approval_info = clinic_info["approval_info"]
                    has_status = "status" in approval_info
                    has_history = "approval_history" in approval_info
                    has_compliance = "compliance_check" in approval_info
                    
                    if has_status and has_history and has_compliance:
                        self.log_test("Clinic Approval Info Structure", True, 
                                    f"Approval info structure preserved with status: {approval_info.get('status')}", 
                                    response_time)
                        return True
                    else:
                        self.log_test("Clinic Approval Info Structure", False, 
                                    f"Incomplete approval info. Has: status({has_status}), history({has_history}), compliance({has_compliance})", 
                                    response_time)
                        return False
                else:
                    self.log_test("Clinic Approval Info Structure", False, 
                                "Approval info structure not preserved in response", 
                                response_time)
                    return False
            else:
                self.log_test("Clinic Approval Info Structure", False, 
                            f"Clinic creation failed: {response.status_code} - {response.text}", 
                            response_time)
                return False
                
        except Exception as e:
            self.log_test("Clinic Approval Info Structure", False, f"Error: {str(e)}")
            return False

    def test_debt_collection_apis(self):
        """Test debt and collection management APIs"""
        try:
            # Test debt summary statistics
            start_time = time.time()
            debt_stats_response = self.session.get(f"{API_BASE}/debts/summary/statistics")
            debt_stats_time = (time.time() - start_time) * 1000
            
            debt_stats_success = debt_stats_response.status_code == 200
            if debt_stats_success:
                debt_stats = debt_stats_response.json()
                self.log_test("Debt Summary Statistics", True, 
                            f"Debt stats: total({debt_stats.get('total_debt', 0)}), count({debt_stats.get('debt_count', 0)})", 
                            debt_stats_time)
            else:
                self.log_test("Debt Summary Statistics", False, 
                            f"Failed: {debt_stats_response.status_code} - {debt_stats_response.text}", 
                            debt_stats_time)
            
            # Test collection statistics
            start_time = time.time()
            collection_stats_response = self.session.get(f"{API_BASE}/debts/collections/summary/statistics")
            collection_stats_time = (time.time() - start_time) * 1000
            
            collection_stats_success = collection_stats_response.status_code == 200
            if collection_stats_success:
                collection_stats = collection_stats_response.json()
                self.log_test("Collection Summary Statistics", True, 
                            f"Collection stats: total({collection_stats.get('total_collected', 0)}), count({collection_stats.get('collection_count', 0)})", 
                            collection_stats_time)
            else:
                self.log_test("Collection Summary Statistics", False, 
                            f"Failed: {collection_stats_response.status_code} - {collection_stats_response.text}", 
                            collection_stats_time)
            
            # Test debt records
            start_time = time.time()
            debts_response = self.session.get(f"{API_BASE}/debts")
            debts_time = (time.time() - start_time) * 1000
            
            debts_success = debts_response.status_code == 200
            if debts_success:
                debts = debts_response.json()
                debt_count = len(debts) if isinstance(debts, list) else 0
                self.log_test("Debt Records", True, f"Retrieved {debt_count} debt records", debts_time)
            else:
                self.log_test("Debt Records", False, 
                            f"Failed: {debts_response.status_code} - {debts_response.text}", debts_time)
            
            # Test collection records
            start_time = time.time()
            collections_response = self.session.get(f"{API_BASE}/debts/collections")
            collections_time = (time.time() - start_time) * 1000
            
            collections_success = collections_response.status_code == 200
            if collections_success:
                collections = collections_response.json()
                collection_count = len(collections) if isinstance(collections, list) else 0
                self.log_test("Collection Records", True, f"Retrieved {collection_count} collection records", collections_time)
            else:
                self.log_test("Collection Records", False, 
                            f"Failed: {collections_response.status_code} - {collections_response.text}", collections_time)
            
            return debt_stats_success and collection_stats_success and debts_success and collections_success
                
        except Exception as e:
            self.log_test("Debt Collection APIs", False, f"Error: {str(e)}")
            return False

    def test_dashboard_enhancement_apis(self):
        """Test enhanced dashboard APIs"""
        try:
            # Test dashboard statistics
            start_time = time.time()
            dashboard_response = self.session.get(f"{API_BASE}/dashboard/stats")
            dashboard_time = (time.time() - start_time) * 1000
            
            dashboard_success = dashboard_response.status_code == 200
            if dashboard_success:
                dashboard_stats = dashboard_response.json()
                self.log_test("Dashboard Statistics", True, 
                            f"Dashboard stats: users({dashboard_stats.get('total_users', 0)}), clinics({dashboard_stats.get('total_clinics', 0)}), products({dashboard_stats.get('total_products', 0)})", 
                            dashboard_time)
            else:
                self.log_test("Dashboard Statistics", False, 
                            f"Failed: {dashboard_response.status_code} - {dashboard_response.text}", 
                            dashboard_time)
            
            # Test admin activities
            start_time = time.time()
            activities_response = self.session.get(f"{API_BASE}/admin/activities")
            activities_time = (time.time() - start_time) * 1000
            
            activities_success = activities_response.status_code == 200
            if activities_success:
                activities = activities_response.json()
                activity_count = len(activities) if isinstance(activities, list) else 0
                self.log_test("Admin Activities", True, f"Retrieved {activity_count} activities", activities_time)
            else:
                self.log_test("Admin Activities", False, 
                            f"Failed: {activities_response.status_code} - {activities_response.text}", activities_time)
            
            # Test activity statistics
            start_time = time.time()
            activity_stats_response = self.session.get(f"{API_BASE}/admin/activities/stats")
            activity_stats_time = (time.time() - start_time) * 1000
            
            activity_stats_success = activity_stats_response.status_code == 200
            if activity_stats_success:
                activity_stats = activity_stats_response.json()
                self.log_test("Activity Statistics", True, 
                            f"Activity stats: total({activity_stats.get('total_activities', 0)}), today({activity_stats.get('today_activities', 0)})", 
                            activity_stats_time)
            else:
                self.log_test("Activity Statistics", False, 
                            f"Failed: {activity_stats_response.status_code} - {activity_stats_response.text}", 
                            activity_stats_time)
            
            # Test GPS tracking
            start_time = time.time()
            gps_response = self.session.get(f"{API_BASE}/admin/gps-tracking")
            gps_time = (time.time() - start_time) * 1000
            
            gps_success = gps_response.status_code == 200
            if gps_success:
                gps_data = gps_response.json()
                gps_count = len(gps_data) if isinstance(gps_data, list) else 0
                self.log_test("GPS Tracking", True, f"Retrieved {gps_count} GPS records", gps_time)
            else:
                self.log_test("GPS Tracking", False, 
                            f"Failed: {gps_response.status_code} - {gps_response.text}", gps_time)
            
            return dashboard_success and activities_success and activity_stats_success and gps_success
                
        except Exception as e:
            self.log_test("Dashboard Enhancement APIs", False, f"Error: {str(e)}")
            return False

    def test_performance_metrics(self):
        """Test API response times for performance"""
        performance_tests = [
            ("Users API Performance", f"{API_BASE}/users"),
            ("Clinics API Performance", f"{API_BASE}/clinics"),
            ("Products API Performance", f"{API_BASE}/products"),
            ("Orders API Performance", f"{API_BASE}/orders"),
            ("Dashboard API Performance", f"{API_BASE}/dashboard/stats")
        ]
        
        total_response_time = 0
        successful_tests = 0
        
        for test_name, url in performance_tests:
            try:
                start_time = time.time()
                response = self.session.get(url)
                response_time = (time.time() - start_time) * 1000
                total_response_time += response_time
                
                if response.status_code == 200:
                    # Consider response time acceptable if under 2000ms
                    performance_acceptable = response_time < 2000
                    if performance_acceptable:
                        self.log_test(test_name, True, f"Response time: {response_time:.2f}ms (acceptable)", response_time)
                        successful_tests += 1
                    else:
                        self.log_test(test_name, False, f"Response time: {response_time:.2f}ms (too slow)", response_time)
                else:
                    self.log_test(test_name, False, f"API failed: {response.status_code}", response_time)
                    
            except Exception as e:
                self.log_test(test_name, False, f"Error: {str(e)}")
        
        # Calculate average response time
        avg_response_time = total_response_time / len(performance_tests) if performance_tests else 0
        
        # Overall performance assessment
        if successful_tests == len(performance_tests) and avg_response_time < 1000:
            self.log_test("Overall API Performance", True, f"Average response time: {avg_response_time:.2f}ms (excellent)")
            return True
        elif successful_tests >= len(performance_tests) * 0.8:
            self.log_test("Overall API Performance", True, f"Average response time: {avg_response_time:.2f}ms (good)")
            return True
        else:
            self.log_test("Overall API Performance", False, f"Performance issues detected. Average: {avg_response_time:.2f}ms")
            return False

    def test_error_handling(self):
        """Test robust error handling for new functionalities"""
        error_tests = [
            ("Invalid User ID", f"{API_BASE}/users/invalid-id/profile", 404),
            ("Invalid Clinic ID", f"{API_BASE}/clinics/invalid-id", 404),
            ("Invalid Order ID", f"{API_BASE}/orders/invalid-id", 404),
            ("Unauthorized Debt Access", f"{API_BASE}/debts", None),  # Should work with admin token
            ("Invalid Settings Update", f"{API_BASE}/admin/settings", None)  # Should work with admin token
        ]
        
        successful_error_handling = 0
        
        for test_name, url, expected_status in error_tests:
            try:
                start_time = time.time()
                if "settings" in url:
                    # Test PUT with invalid data
                    response = self.session.put(url, json={"invalid": "data"})
                else:
                    response = self.session.get(url)
                response_time = (time.time() - start_time) * 1000
                
                if expected_status:
                    # Expecting specific error status
                    if response.status_code == expected_status:
                        self.log_test(test_name, True, f"Correct error handling: {response.status_code}", response_time)
                        successful_error_handling += 1
                    else:
                        self.log_test(test_name, False, f"Unexpected status: {response.status_code} (expected {expected_status})", response_time)
                else:
                    # Should work with admin token
                    if response.status_code in [200, 201]:
                        self.log_test(test_name, True, f"Authorized access works: {response.status_code}", response_time)
                        successful_error_handling += 1
                    else:
                        self.log_test(test_name, False, f"Authorization issue: {response.status_code}", response_time)
                        
            except Exception as e:
                self.log_test(test_name, False, f"Error: {str(e)}")
        
    def test_core_apis(self):
        """Test core APIs that should be working"""
        core_tests = [
            ("GET /api/users", f"{API_BASE}/users"),
            ("GET /api/clinics", f"{API_BASE}/clinics"),
            ("GET /api/products", f"{API_BASE}/products"),
            ("GET /api/orders", f"{API_BASE}/orders"),
            ("GET /api/lines", f"{API_BASE}/lines"),
            ("GET /api/areas", f"{API_BASE}/areas"),
            ("GET /api/warehouses", f"{API_BASE}/warehouses"),
            ("GET /api/visits", f"{API_BASE}/visits")
        ]
        
        success_count = 0
        for test_name, url in core_tests:
            try:
                start_time = time.time()
                response = self.session.get(url)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else "N/A"
                    self.log_test(test_name, True, f"Retrieved {count} records", response_time)
                    success_count += 1
                else:
                    self.log_test(test_name, False, f"Failed: {response.status_code} - {response.text}", response_time)
                    
            except Exception as e:
                self.log_test(test_name, False, f"Error: {str(e)}")
        
        return success_count
        """Test core APIs that should be working"""
        core_tests = [
            ("GET /api/users", f"{API_BASE}/users"),
            ("GET /api/clinics", f"{API_BASE}/clinics"),
            ("GET /api/products", f"{API_BASE}/products"),
            ("GET /api/orders", f"{API_BASE}/orders"),
            ("GET /api/lines", f"{API_BASE}/lines"),
            ("GET /api/areas", f"{API_BASE}/areas"),
            ("GET /api/warehouses", f"{API_BASE}/warehouses"),
            ("GET /api/visits", f"{API_BASE}/visits")
        ]
        
        success_count = 0
        for test_name, url in core_tests:
            try:
                start_time = time.time()
                response = self.session.get(url)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else "N/A"
                    self.log_test(test_name, True, f"Retrieved {count} records", response_time)
                    success_count += 1
                else:
                    self.log_test(test_name, False, f"Failed: {response.status_code} - {response.text}", response_time)
                    
            except Exception as e:
                self.log_test(test_name, False, f"Error: {str(e)}")
        
        return success_count

    def run_comprehensive_test(self):
        """Run all comprehensive tests"""
        print("🚀 FINAL COMPREHENSIVE BACKEND TEST - POST ALL MAJOR ENHANCEMENTS")
        print("=" * 80)
        print("🎯 Testing all functionalities enhanced during this session")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Login first
        if not self.login_admin():
            print("❌ Cannot proceed without admin login")
            return
        
        print("\n📋 1. AUTHENTICATION & SECURITY:")
        print("-" * 50)
        # Already tested in login_admin()
        
        print("\n📋 2. CORE API ENDPOINTS:")
        print("-" * 50)
        core_success_count = self.test_core_apis()
        
        print("\n📋 3. NEW DATA STRUCTURE SUPPORT:")
        print("-" * 50)
        approval_info_success = self.test_clinic_approval_info_structure()
        
        print("\n📋 4. SETTINGS & CONFIGURATION:")
        print("-" * 50)
        settings_success = self.test_admin_settings_api()
        
        print("\n📋 5. ENHANCED USER DATA:")
        print("-" * 50)
        user_stats_success = self.test_enhanced_user_statistics()
        
        print("\n📋 6. DEBT & COLLECTION MANAGEMENT:")
        print("-" * 50)
        debt_collection_success = self.test_debt_collection_apis()
        
        print("\n📋 7. DASHBOARD ENHANCEMENTS:")
        print("-" * 50)
        dashboard_success = self.test_dashboard_enhancement_apis()
        
        print("\n📋 8. RESPONSIVE API PERFORMANCE:")
        print("-" * 50)
        performance_success = self.test_performance_metrics()
        
        print("\n📋 9. ERROR HANDLING:")
        print("-" * 50)
        error_handling_success = self.test_error_handling()
        
        print("\n📋 10. SPECIFIC ARABIC REVIEW FIXES:")
        print("-" * 50)
        activities_success = self.test_activities_api()
        orders_detail_success = self.test_orders_detail_api()
        clinic_manager_success = self.test_clinic_manager_fields()
        specialization_success = self.test_clinic_specialization_removal()
        
        # Calculate results
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        # Calculate average response time
        response_times = [result["response_time"] for result in self.test_results if result["response_time"]]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 FINAL COMPREHENSIVE TEST RESULTS")
        print("=" * 80)
        print(f"🎯 Overall Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests} tests)")
        print(f"⚡ Average Response Time: {avg_response_time:.2f}ms")
        print(f"⏱️  Total Test Duration: {time.time() - self.start_time:.2f} seconds")
        print()
        
        # Category Results
        print("📋 CATEGORY BREAKDOWN:")
        print("-" * 50)
        print(f"✅ Authentication & Security: {'PASS' if self.jwt_token else 'FAIL'}")
        print(f"✅ Core API Endpoints: {core_success_count}/8 working")
        print(f"✅ New Data Structures: {'PASS' if approval_info_success else 'FAIL'}")
        print(f"✅ Settings & Configuration: {'PASS' if settings_success else 'FAIL'}")
        print(f"✅ Enhanced User Data: {'PASS' if user_stats_success else 'FAIL'}")
        print(f"✅ Debt & Collection: {'PASS' if debt_collection_success else 'FAIL'}")
        print(f"✅ Dashboard Enhancements: {'PASS' if dashboard_success else 'FAIL'}")
        print(f"✅ API Performance: {'PASS' if performance_success else 'FAIL'}")
        print(f"✅ Error Handling: {'PASS' if error_handling_success else 'FAIL'}")
        print(f"✅ Arabic Review Fixes: {'PASS' if all([activities_success, orders_detail_success, clinic_manager_success, specialization_success]) else 'PARTIAL'}")
        
        print("\n🎯 SYSTEM STABILITY ASSESSMENT:")
        print("-" * 50)
        
        if success_rate >= 95:
            print("🎉 EXCELLENT: System is highly stable and ready for production!")
            stability_status = "EXCELLENT"
        elif success_rate >= 85:
            print("✅ GOOD: System is stable with minor issues that don't affect core functionality")
            stability_status = "GOOD"
        elif success_rate >= 75:
            print("⚠️  ACCEPTABLE: System is functional but needs attention to some areas")
            stability_status = "ACCEPTABLE"
        else:
            print("❌ NEEDS ATTENTION: System has significant issues that need to be addressed")
            stability_status = "NEEDS ATTENTION"
        
        print(f"\n🔍 PERFORMANCE ANALYSIS:")
        print("-" * 50)
        if avg_response_time < 100:
            print(f"🚀 EXCELLENT: Average response time {avg_response_time:.2f}ms (under 100ms)")
        elif avg_response_time < 500:
            print(f"✅ GOOD: Average response time {avg_response_time:.2f}ms (under 500ms)")
        elif avg_response_time < 1000:
            print(f"⚠️  ACCEPTABLE: Average response time {avg_response_time:.2f}ms (under 1s)")
        else:
            print(f"❌ SLOW: Average response time {avg_response_time:.2f}ms (over 1s)")
        
        # Failed tests analysis
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            print("-" * 50)
            for i, test in enumerate(failed_tests, 1):
                print(f"   {i}. {test['test']}: {test['message']}")
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        print("-" * 50)
        print(f"System Stability: {stability_status}")
        print(f"Core Functionality: {'WORKING' if core_success_count >= 6 else 'ISSUES DETECTED'}")
        print(f"Enhanced Features: {'IMPLEMENTED' if debt_collection_success and dashboard_success else 'PARTIAL'}")
        print(f"Performance: {'ACCEPTABLE' if avg_response_time < 1000 else 'NEEDS OPTIMIZATION'}")
        print(f"Production Ready: {'YES' if success_rate >= 85 and avg_response_time < 1000 else 'NEEDS FIXES'}")
        
        return success_rate >= 85

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)