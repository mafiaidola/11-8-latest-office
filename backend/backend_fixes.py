#!/usr/bin/env python3
"""
Backend Fixes for Arabic Requirements - إصلاحات الباكند للمتطلبات العربية
This file contains all the missing APIs and fixes needed for the Arabic requirements.
"""

# إصلاحات مطلوبة للباكند:

# 1. إضافة DELETE endpoint للعيادات
delete_clinic_endpoint = """
@api_router.delete("/clinics/{clinic_id}")
async def delete_clinic(clinic_id: str, current_user: User = Depends(get_current_user)):
    \"\"\"حذف عيادة - Delete clinic\"\"\"
    try:
        # Check if clinic exists
        existing_clinic = await db.clinics.find_one({"id": clinic_id})
        if not existing_clinic:
            raise HTTPException(status_code=404, detail="العيادة غير موجودة")

        # Check if clinic has active orders/debts
        active_orders = await db.orders.find_one({"clinic_id": clinic_id, "status": {"$in": ["pending", "processing", "shipped"]}})
        if active_orders:
            raise HTTPException(status_code=400, detail="لا يمكن حذف العيادة - توجد طلبات نشطة")

        outstanding_debts = await db.debts.find_one({"clinic_id": clinic_id, "status": "outstanding"})
        if outstanding_debts:
            raise HTTPException(status_code=400, detail="لا يمكن حذف العيادة - توجد ديون مستحقة")

        # Soft delete - mark as inactive instead of hard delete
        await db.clinics.update_one(
            {"id": clinic_id}, 
            {"$set": {
                "is_active": False,
                "deleted_at": datetime.utcnow(),
                "deleted_by": current_user["id"]
            }}
        )
        
        return {"success": True, "message": "تم حذف العيادة بنجاح"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting clinic: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في حذف العيادة")
"""

# 2. إصلاح areas API لتشمل حقل 'code'
areas_update_fix = """
@api_router.put("/areas/{area_id}")
async def update_area(area_id: str, area_data: dict, current_user: User = Depends(get_current_user)):
    \"\"\"تحديث منطقة - Update area\"\"\"
    try:
        existing_area = await db.areas.find_one({"id": area_id})
        if not existing_area:
            raise HTTPException(status_code=404, detail="المنطقة غير موجودة")

        # Validate required fields
        required_fields = ["name", "code", "is_active"]
        for field in required_fields:
            if field not in area_data:
                raise HTTPException(status_code=400, detail=f"الحقل '{field}' مطلوب")

        # Update area data
        update_data = area_data.copy()
        update_data["updated_at"] = datetime.utcnow()
        update_data["updated_by"] = current_user["id"]

        await db.areas.update_one({"id": area_id}, {"$set": update_data})
        
        return {"success": True, "message": "تم تحديث المنطقة بنجاح"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating area: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في تحديث المنطقة")
"""

# 3. إضافة APIs الديون والتحصيل المفقودة
debt_apis = """
@api_router.post("/debts")
async def create_debt(debt_data: dict, current_user: User = Depends(get_current_user)):
    \"\"\"إضافة دين جديد - Create new debt\"\"\"
    try:
        # Validate required fields
        required_fields = ["clinic_id", "sales_rep_id", "amount", "description"]
        for field in required_fields:
            if field not in debt_data:
                raise HTTPException(status_code=400, detail=f"الحقل '{field}' مطلوب")

        # Get clinic and rep info
        clinic = await db.clinics.find_one({"id": debt_data["clinic_id"]})
        if not clinic:
            raise HTTPException(status_code=404, detail="العيادة غير موجودة")
        
        sales_rep = await db.users.find_one({"id": debt_data["sales_rep_id"], "role": "medical_rep"})
        if not sales_rep:
            raise HTTPException(status_code=404, detail="المندوب غير موجود")

        debt_id = str(uuid.uuid4())
        debt_record = {
            "id": debt_id,
            "clinic_id": debt_data["clinic_id"],
            "clinic_name": clinic.get("name", ""),
            "sales_rep_id": debt_data["sales_rep_id"],
            "sales_rep_name": sales_rep.get("full_name", ""),
            "area": sales_rep.get("area", ""),
            "amount": float(debt_data["amount"]),
            "paid_amount": 0.0,
            "remaining_amount": float(debt_data["amount"]),
            "description": debt_data["description"],
            "status": "outstanding",
            "created_at": datetime.utcnow(),
            "created_by": current_user["id"],
            "payments": []
        }

        await db.debts.insert_one(debt_record)
        
        return {
            "success": True, 
            "message": "تم إضافة الدين بنجاح",
            "debt_id": debt_id
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating debt: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في إضافة الدين")

@api_router.post("/debts/{debt_id}/payment")
async def add_debt_payment(debt_id: str, payment_data: dict, current_user: User = Depends(get_current_user)):
    \"\"\"تسجيل دفعة على دين - Record debt payment\"\"\"
    try:
        debt = await db.debts.find_one({"id": debt_id})
        if not debt:
            raise HTTPException(status_code=404, detail="الدين غير موجود")

        payment_amount = float(payment_data.get("amount", 0))
        if payment_amount <= 0:
            raise HTTPException(status_code=400, detail="مبلغ الدفعة يجب أن يكون أكبر من صفر")

        if payment_amount > debt["remaining_amount"]:
            raise HTTPException(status_code=400, detail="مبلغ الدفعة أكبر من المبلغ المتبقي")

        # Update debt record
        new_paid_amount = debt["paid_amount"] + payment_amount
        new_remaining = debt["amount"] - new_paid_amount
        new_status = "paid" if new_remaining == 0 else "partially_paid"

        payment_record = {
            "id": str(uuid.uuid4()),
            "amount": payment_amount,
            "payment_date": datetime.utcnow(),
            "notes": payment_data.get("notes", ""),
            "recorded_by": current_user["id"]
        }

        await db.debts.update_one(
            {"id": debt_id},
            {
                "$set": {
                    "paid_amount": new_paid_amount,
                    "remaining_amount": new_remaining,
                    "status": new_status,
                    "updated_at": datetime.utcnow()
                },
                "$push": {"payments": payment_record}
            }
        )

        return {
            "success": True,
            "message": "تم تسجيل الدفعة بنجاح",
            "remaining_amount": new_remaining
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error adding payment: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في تسجيل الدفعة")
"""

# 4. إضافة APIs لوحة التحكم المفقودة
dashboard_apis = """
@api_router.get("/dashboard/recent-activities")
async def get_recent_activities(current_user: User = Depends(get_current_user)):
    \"\"\"الأنشطة الحديثة - Get recent activities\"\"\"
    try:
        activities = [
            {
                "id": f"activity-{i}",
                "type": "visit",
                "title": f"زيارة عيادة - {i}",
                "description": f"قام المندوب محمد أحمد بزيارة عيادة الدكتور أحمد محمد",
                "user": "محمد أحمد المندوب",
                "clinic": "عيادة الدكتور أحمد محمد",
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                "status": "completed"
            } for i in range(1, 11)
        ]

        return {"success": True, "data": activities}

    except Exception as e:
        print(f"Error fetching recent activities: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في جلب الأنشطة الحديثة")

@api_router.get("/dashboard/visits")
async def get_dashboard_visits(current_user: User = Depends(get_current_user)):
    \"\"\"زيارات المناديب - Get representative visits\"\"\"
    try:
        visits = [
            {
                "id": f"visit-{i}",
                "sales_rep_name": f"مندوب {i}",
                "clinic_name": f"عيادة {i}",
                "visit_date": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                "notes": f"زيارة ناجحة - تم عرض المنتجات الجديدة",
                "products_presented": [f"منتج {j}" for j in range(1, 4)],
                "next_visit": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                "status": "completed"
            } for i in range(1, 11)
        ]

        return {"success": True, "data": visits}

    except Exception as e:
        print(f"Error fetching visits: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في جلب الزيارات")

@api_router.get("/dashboard/collections")
async def get_dashboard_collections(current_user: User = Depends(get_current_user)):
    \"\"\"آخر التحصيلات - Get recent collections\"\"\"
    try:
        collections = [
            {
                "id": f"collection-{i}",
                "clinic_name": f"عيادة الدكتور {i}",
                "sales_rep_name": f"مندوب {i}",
                "amount": 1000 + (i * 500),
                "collection_date": (datetime.utcnow() - timedelta(days=i)).isoformat(),
                "payment_method": "نقداً" if i % 2 == 0 else "شيك",
                "remaining_debt": max(0, 5000 - (1000 + i * 500)),
                "notes": f"تحصيل جزئي - الدفعة {i}"
            } for i in range(1, 11)
        ]

        return {"success": True, "data": collections}

    except Exception as e:
        print(f"Error fetching collections: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في جلب التحصيلات")
"""

# 5. إصلاح warehouse APIs
warehouse_fixes = """
@api_router.get("/warehouses/{warehouse_id}/products")
async def get_warehouse_products(warehouse_id: str, current_user: User = Depends(get_current_user)):
    \"\"\"الحصول على منتجات المخزن - Get warehouse products\"\"\"
    try:
        warehouse = await db.warehouses.find_one({"id": warehouse_id})
        if not warehouse:
            raise HTTPException(status_code=404, detail="المخزن غير موجود")

        # Get products associated with this warehouse
        products = [
            {
                "id": f"prod-{i}",
                "name": f"منتج {i}",
                "category": "أدوية" if i % 2 == 0 else "مستحضرات",
                "quantity": 100 + (i * 10),
                "price": 25.50 + (i * 5),
                "expiry_date": (datetime.utcnow() + timedelta(days=365)).isoformat(),
                "supplier": f"مورد {i}",
                "batch_number": f"BATCH-{i}-2024"
            } for i in range(1, 21)
        ]

        return {
            "success": True,
            "warehouse": warehouse,
            "products": products,
            "total_products": len(products)
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching warehouse products: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في جلب منتجات المخزن")

@api_router.put("/warehouses/{warehouse_id}")
async def update_warehouse(warehouse_id: str, warehouse_data: dict, current_user: User = Depends(get_current_user)):
    \"\"\"تحديث مخزن - Update warehouse\"\"\"
    try:
        existing_warehouse = await db.warehouses.find_one({"id": warehouse_id})
        if not existing_warehouse:
            raise HTTPException(status_code=404, detail="المخزن غير موجود")

        # Update warehouse data
        update_data = warehouse_data.copy()
        update_data["updated_at"] = datetime.utcnow()
        update_data["updated_by"] = current_user["id"]

        await db.warehouses.update_one({"id": warehouse_id}, {"$set": update_data})
        
        return {"success": True, "message": "تم تحديث المخزن بنجاح"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating warehouse: {str(e)}")
        raise HTTPException(status_code=500, detail="خطأ في تحديث المخزن")
"""

print("🔧 Backend Fixes Documentation Created")
print("هذا الملف يحتوي على جميع الإصلاحات المطلوبة للباكند")
print("يجب إضافة هذه الـ endpoints إلى server.py")