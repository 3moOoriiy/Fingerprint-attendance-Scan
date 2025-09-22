import streamlit as st
import json
import os
import time
from datetime import datetime
import pandas as pd
from io import BytesIO
import pytz

# ==============================
# 📌 إعدادات أساسية
# ==============================
st.set_page_config(page_title="نظام الحضور بالبصمة", page_icon="🕒", layout="centered")

DATA_FILE = "attendance_data.json"
TIMEZONE = "Africa/Cairo"

# ==============================
# 📌 دوال مساعدة
# ==============================
def load_attendance_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_attendance_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_local_time():
    tz = pytz.timezone(TIMEZONE)
    return datetime.now(tz)

def export_to_excel(data):
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="الحضور")
    output.seek(0)
    return output

# ==============================
# 📌 بيانات التطبيق
# ==============================
if "attendance_log" not in st.session_state:
    st.session_state.attendance_log = load_attendance_data()

if "users" not in st.session_state:
    st.session_state.users = [
        {"id": "101", "name": "أحمد محمد"},
        {"id": "102", "name": "محمود علي"},
        {"id": "103", "name": "سارة أحمد"},
        {"id": "104", "name": "منى خالد"},
    ]

# ==============================
# 📌 واجهة التطبيق
# ==============================
st.title("🕒 نظام تسجيل الحضور بالبصمة")

# ==============================
# ✅ خانة اسكان الباركود (بصمة تلقائية)
# ==============================
barcode_input = st.text_input("📷 اسكان باركود الموظف", value="", placeholder="وجّه الاسكانر على باركود الموظف")

if barcode_input:
    matched_user = next((user for user in st.session_state.users if str(user["id"]) == barcode_input.strip()), None)
    
    if matched_user:
        now = get_local_time()
        entry = {
            'name': matched_user["name"],
            'id': matched_user["id"],
            'time': now.strftime("%I:%M:%S %p"),
            'time_24': now.strftime("%H:%M:%S"),
            'date': now.strftime("%Y-%m-%d"),
            'date_arabic': now.strftime("%d/%m/%Y"),
            'timestamp': now.timestamp()
        }
        
        st.session_state.attendance_log.insert(0, entry)
        save_attendance_data(st.session_state.attendance_log)
        
        st.success(f"✅ تم تسجيل بصمة الموظف: {matched_user['name']}")
        st.info(f"📅 التاريخ: {entry['date_arabic']} | 🕐 الوقت: {entry['time']}")
        st.balloons()
        
        st.session_state["barcode_cleared"] = True
        st.rerun()
    else:
        st.error("❌ الكود غير مسجل. تأكد من أن الموظف مضاف في النظام.")

# ==============================
# 📋 عرض السجلات
# ==============================
st.subheader("📋 سجلات الحضور")

if st.session_state.attendance_log:
    df = pd.DataFrame(st.session_state.attendance_log)
    st.dataframe(df[["id", "name", "date_arabic", "time"]], use_container_width=True)

    excel_file = export_to_excel(st.session_state.attendance_log)
    st.download_button(
        label="⬇️ تحميل ملف Excel",
        data=excel_file,
        file_name="attendance.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("ℹ️ لا توجد سجلات حضور بعد.")
