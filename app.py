import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# ==========================
# بيانات الموظفين والباركود
# ==========================
employees = {
    "FA112": "Farida Ahmed",
    "FM109": "Farida Muhammed",
    # ضيف باقي الموظفين بنفس الشكل
}

# ==========================
# دالة تنظيف الباركود
# ==========================
def clean_barcode(raw_code):
    # يشيل أي رموز مش حروف أو أرقام ويحولها لـ Uppercase
    return "".join(ch for ch in raw_code if ch.isalnum()).upper()

# ==========================
# دالة تسجيل الحضور
# ==========================
def log_attendance(emp_id):
    if emp_id in employees:
        emp_name = employees[emp_id]
        now = datetime.now(pytz.timezone("Africa/Cairo"))
        date_arabic = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        new_record = {
            "id": emp_id,
            "name": emp_name,
            "date_arabic": date_arabic,
            "time": time,
        }

        # لو ملف اكسل موجود افتحه
        try:
            df = pd.read_excel("attendance.xlsx")
        except FileNotFoundError:
            df = pd.DataFrame(columns=["id", "name", "date_arabic", "time"])

        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
        df.to_excel("attendance.xlsx", index=False)

        return f"✅ تم تسجيل الحضور للموظف: {emp_name} ({emp_id})"
    else:
        return f"❌ الكود {emp_id} غير مسجل لموظف"

# ==========================
# Streamlit UI
# ==========================
st.title("📌 نظام تسجيل الحضور بالباركود")

barcode_input = st.text_input("🔍 امسح الباركود هنا:")

if barcode_input:
    emp_id = clean_barcode(barcode_input.strip())  # تنظيف الكود
    result = log_attendance(emp_id)
    st.success(result)

# عرض جدول الحضور
try:
    df = pd.read_excel("attendance.xlsx")
    st.subheader("📑 سجل الحضور")
    st.dataframe(df, use_container_width=True)
except FileNotFoundError:
    st.info("ℹ️ لم يتم تسجيل أي حضور بعد.")
