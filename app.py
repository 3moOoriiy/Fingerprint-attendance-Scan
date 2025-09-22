import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="جدول الحضور والانصراف", layout="centered")

# تهيئة البيانات في session_state
if "data" not in st.session_state:
    st.session_state.data = []

st.title("📊 جدول الحضور والانصراف")

# إدخال بيانات
with st.form("data_form", clear_on_submit=True):
    name = st.text_input("اسم الموظف")
    col1, col2 = st.columns(2)
    with col1:
        time_in = st.time_input("وقت الدخول", format="hh:mm a")
    with col2:
        time_out = st.time_input("وقت الخروج", format="hh:mm a")

    submitted = st.form_submit_button("إضافة")

    if submitted and name:
        st.session_state.data.append({
            "اسم الموظف": name,
            "وقت الدخول": time_in.strftime("%I:%M %p"),
            "وقت الخروج": time_out.strftime("%I:%M %p")
        })
        st.success("✅ تم إضافة البيانات")

# تحويل البيانات إلى DataFrame
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)

    st.subheader("📌 البيانات المدخلة")
    st.dataframe(df, use_container_width=True)

    # أزرار التحكم
    colA, colB, colC = st.columns(3)

    # زر حفظ (يثبت البيانات كما هي)
    with colA:
        if st.button("💾 حفظ البيانات"):
            st.success("✅ تم حفظ البيانات بنجاح (موجودة بالفعل في الجدول)")

    # زر تحميل Excel
    with colB:
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="الحضور")
        st.download_button(
            label="⬇️ تحميل Excel",
            data=buffer.getvalue(),
            file_name="attendance.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # زر مسح البيانات
    with colC:
        if st.button("🗑️ مسح البيانات"):
            st.session_state.data = []
            st.warning("⚠️ تم مسح كل البيانات")
else:
    st.info("ℹ️ لم يتم إدخال أي بيانات بعد.")
