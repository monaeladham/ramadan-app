import streamlit as st
import pandas as pd
import google.generativeai as genai

# إعداد الـ API من الـ Secrets
if "api_key" in st.secrets:
    genai.configure(api_key=st.secrets["api_key"])

st.title("🌙 دليل مدبرة رمضان الذكي")

try:
    # تحميل الجداول
    df_health = pd.read_csv("table1.csv")
    df_meals = pd.read_csv("meals.csv")
    
    st.success("تم تحميل البيانات بنجاح!")
    
    num = st.number_input("عدد الأفراد", min_value=1, value=1)
    if st.button("توليد الخطة"):
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"اقترح وجبة من جدول {df_meals.to_string()} لعدد {num} أفراد")
        st.markdown(response.text)
except Exception as e:
    st.error(f"تأكد من وجود الملفات في GitHub: {e}")
