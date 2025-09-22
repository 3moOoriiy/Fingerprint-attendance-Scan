import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from io import BytesIO

# ==========================
# بيانات الموظفين والباركود
# ==========================
employees = {
    "FA112": "Farida Ahmed",
    "FM109": "Farida Muhammed",
}

# خريطة لربط الأرقام بالكود
barcode_map = {
    "112": "FA112",
    "109": "FM109",
}

# ==========================
# دالة تنظيف الباركود
# ==========================
def clean_barcode(raw_code):
    # يشيل أي رموز مش أرقام
    digits = "".join(ch for ch in raw_code if ch.isdigit())
    return digits

# ==========================
# دالة تسجيل الحضور
# ==========================
def log_attendance(raw_code):
    clean_code = clean_barcode(raw_code)

    if clean_code in barcode_map:
        emp_id = barcode_map[clean_code]
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

        try:
            df = pd.read_excel("attendance.xlsx", engine="openpyxl")
        except FileNotFoundError:
            df = pd.DataFrame(columns=["id", "name", "date_arabic", "time"])

        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
        df.to_excel("attendance.xlsx", index=False, engine="openpyxl")

        return f"✅ تم تسجيل الحضور للموظف: {emp_name} ({emp_id})"
    else:
        return f"❌ الكود {raw_code} غير مسجل لموظف"

# ==========================
# Streamlit UI
# ==========================
st.title("📌 نظام تسجيل الحضور بالباركود")

barcode_input = st.text_input("🔍 امسح الباركود هنا:")

if barcode_input:
    result = log_attendance(barcode_input.strip())
    st.success(result)

# عرض جدول الحضور
try:
    df = pd.read_excel("attendance.xlsx", engine="openpyxl")
    st.subheader("📑 سجل الحضور")
    st.dataframe(df, use_container_width=True)

    # زرار تحميل الجدول
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Attendance")
    st.download_button(
        label="⬇️ تحميل ملف الحضور Excel",
        data=buffer.getvalue(),
        file_name="attendance.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

except FileNotFoundError:
    st.info("ℹ️ لم يتم تسجيل أي حضور بعد.")
