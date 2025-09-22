import streamlit as st
import pandas as pd
from datetime import datetime
import time
import json
import os
from io import BytesIO
import pytz

# إعداد الصفحة
st.set_page_config(
    page_title="Siwa_Barcode",
    page_icon="📱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# إعداد CSS مخصص
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700&display=swap');
    .rtl {direction: rtl; text-align: right; font-family: 'Tajawal', sans-serif;}
    .main-title {text-align: center; font-size: 3rem; font-weight: bold; color: #667eea;
        margin-bottom: 2rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);}
    .success-message {background: linear-gradient(45deg, #56ab2f, #a8e6cf); color: #2d5016;
        padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; margin: 20px 0;}
    .error-message {background: linear-gradient(45deg, #ff416c, #ff4b2b); color: white;
        padding: 15px; border-radius: 10px; text-align: center; font-weight: bold; margin: 20px 0;}
    .attendance-log {background: rgba(255, 255, 255, 0.95); border-radius: 15px; padding: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);}
    .log-entry {padding: 12px; margin-bottom: 10px; background: linear-gradient(135deg, #f093fb, #f5576c);
        color: white; border-radius: 10px; display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0 3px 10px rgba(240, 147, 251, 0.3);}
    .stDeployButton {display:none;} footer {visibility: hidden;} .stApp > header {visibility: hidden;}
    .stButton > button {width: 100%; border-radius: 12px; border: none; padding: 15px; font-size: 1.1rem;
        font-weight: bold; transition: all 0.3s ease;}
    .dataframe {direction: rtl; text-align: right;}
</style>
""", unsafe_allow_html=True)

# ملف حفظ البيانات
DATA_FILE = "attendance_data.json"

# تحميل البيانات
def load_attendance_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

# حفظ البيانات
def save_attendance_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# إنشاء ملف Excel
def create_excel_file(data):
    if not data:
        return None
    
    df = pd.DataFrame(data)
    df = df[['id', 'name', 'date', 'time', 'timestamp']] if 'id' in df.columns else df[['name', 'date', 'time', 'timestamp']]
    df.columns = ['ID', 'الاسم', 'التاريخ', 'الوقت', 'الطابع الزمني'] if 'id' in df.columns else ['الاسم', 'التاريخ', 'الوقت', 'الطابع الزمني']
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='سجل الحضور', index=False)
        workbook = writer.book
        worksheet = writer.sheets['سجل الحضور']
        header_format = workbook.add_format({'bold': True,'text_wrap': True,'valign': 'top',
                                             'fg_color': '#667eea','font_color': 'white','border': 1})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        worksheet.set_column('A:E', 20)
    output.seek(0)
    return output

# توقيت الإسكندرية
ALEXANDRIA_TZ = pytz.timezone('Africa/Cairo')
def get_local_time():
    utc_time = datetime.utcnow()
    utc_time = pytz.utc.localize(utc_time)
    local_time = utc_time.astimezone(ALEXANDRIA_TZ)
    return local_time

# تهيئة الجلسة
if 'attendance_log' not in st.session_state:
    st.session_state.attendance_log = load_attendance_data()

if 'scanning' not in st.session_state:
    st.session_state.scanning = False

# العنوان الرئيسي
st.markdown('<div class="rtl main-title">📱 Siwa_Barcode</div>', unsafe_allow_html=True)

# إدخال ID الموظف (من الاسكانر)
st.markdown('<div class="rtl"><h3>📱 اسكان ID الموظف:</h3></div>', unsafe_allow_html=True)
employee_id = st.text_input("➡️ امسح الكود هنا:", placeholder="اسكان ID الموظف بالباركود")

# تسجيل الحضور عند إدخال ID
if employee_id:
    now = get_local_time()
    entry = {
        'id': employee_id.strip(),
        'name': f"موظف {employee_id.strip()}",
        'time': now.strftime("%I:%M:%S %p"),
        'time_24': now.strftime("%H:%M:%S"),
        'date': now.strftime("%Y-%m-%d"),
        'date_arabic': now.strftime("%d/%m/%Y"),
        'timestamp': now.timestamp()
    }
    st.session_state.attendance_log.insert(0, entry)
    save_attendance_data(st.session_state.attendance_log)
    st.balloons()
    st.success(f"✅ تم تسجيل حضور الموظف: {employee_id}")
    st.info(f"📅 التاريخ: {entry['date_arabic']} | 🕐 الوقت: {entry['time']}")
    time.sleep(1)
    st.rerun()

# عرض السجلات
st.subheader("📋 سجل الحضور")

if st.session_state.attendance_log:
    df = pd.DataFrame(st.session_state.attendance_log)
    # تأكد من وجود الأعمدة
    for col in ["id", "name", "date_arabic", "time"]:
        if col not in df.columns:
            df[col] = ""
    st.dataframe(df[["id", "name", "date_arabic", "time"]], use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 تحميل Excel"):
            excel_file = create_excel_file(st.session_state.attendance_log)
            if excel_file:
                st.download_button(
                    label="📥 تحميل ملف Excel",
                    data=excel_file,
                    file_name=f"attendance_log_{get_local_time().strftime('%Y-%m-%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    with col2:
        if st.button("🗑️ مسح السجل"):
            st.session_state.attendance_log = []
            save_attendance_data([])
            st.success("🗑️ تم مسح السجل بنجاح")
            st.rerun()
else:
    st.info("📝 لا توجد سجلات حضور بعد")

# الشريط الجانبي
with st.sidebar:
    st.markdown("### ℹ️ معلومات النظام")
    st.info("نظام الباركود الذكي لتسجيل الحضور\n\n✅ حفظ البيانات\n✅ تصدير إلى Excel\n✅ إحصائيات فورية")
    current_time = get_local_time()
    st.markdown(f"**التوقيت الحالي (الإسكندرية):**\n\n📅 {current_time.strftime('%d/%m/%Y')}\n\n🕐 {current_time.strftime('%I:%M:%S %p')}")
    if st.button("🔄 تحديث الوقت"):
        st.rerun()
