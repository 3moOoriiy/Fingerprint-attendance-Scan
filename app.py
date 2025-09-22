import streamlit as st
import pandas as pd
from datetime import datetime

# تخزين بيانات الموظفين (ID: Name)
employees = {
    "FA112": "Farida Ahmed",
    "FM109": "Farida Muhammed"
}

# جدول الحضور
if "attendance" not in st.session_state:
    st.session_state.attendance = pd.DataFrame(columns=["ID", "Name", "Date", "Time In", "Time Out"])

st.title("📌 نظام تسجيل الحضور بالبصمة (Barcode)")

# إدخال الباركود
barcode = st.text_input("امسح الباركود هنا")

# عند المسح
if barcode:
    current_time = datetime.now().strftime("%I:%M %p")  # 12 ساعة
    current_date = datetime.now().strftime("%Y-%m-%d")

    if barcode in employees:
        employee_name = employees[barcode]

        # البحث هل الموظف سجل دخول النهارده
        existing = st.session_state.attendance[
            (st.session_state.attendance["ID"] == barcode) &
            (st.session_state.attendance["Date"] == current_date)
        ]

        if existing.empty:
            # تسجيل وقت دخول
            new_row = {"ID": barcode, "Name": employee_name, "Date": current_date,
                       "Time In": current_time, "Time Out": ""}
            st.session_state.attendance = pd.concat([st.session_state.attendance, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"✅ {employee_name} تم تسجيل وقت الدخول: {current_time}")
        else:
            # تحديث وقت الخروج
            idx = existing.index[0]
            st.session_state.attendance.at[idx, "Time Out"] = current_time
            st.success(f"✅ {employee_name} تم تسجيل وقت الخروج: {current_time}")
    else:
        st.error("❌ الباركود غير مسجل!")

# عرض الجدول
st.subheader("📊 سجل الحضور")
st.dataframe(st.session_state.attendance)

# زرار حفظ البيانات
if st.button("💾 حفظ البيانات إلى Excel"):
    file_name = f"Attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    st.session_state.attendance.to_excel(file_name, index=False)
    st.success(f"✅ تم حفظ الملف باسم: {file_name}")

# زرار مسح البيانات
if st.button("🗑️ مسح كل البيانات"):
    st.session_state.attendance = pd.DataFrame(columns=["ID", "Name", "Date", "Time In", "Time Out"])
    st.success("✅ تم مسح كل البيانات")
