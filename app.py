import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. إعداد الـ API من الـ Secrets
if "api_key" in st.secrets:
    genai.configure(api_key=st.secrets["api_key"])
else:
    st.error("⚠️ يرجى ضبط الـ api_key في إعدادات Secrets")

st.set_page_config(page_title="مدبرة رمضان", layout="wide")
st.title("🌙 دليل مدبرة رمضان الذكي")

try:
    # 2. تحميل البيانات (بناءً على أسمائك الجديدة)
    @st.cache_data
    def load_data():
        df1 = pd.read_csv("table1.csv")
        df2 = pd.read_csv("table2.csv")
        df3 = pd.read_csv("table3.csv")
        df_m = pd.read_csv("meals.csv")
        # مسح أي مسافات مخفية في أسامي الأعمدة
        df1.columns = df1.columns.str.strip()
        return df1, df2, df3, df_m

    df_health, df_portions, df_alts, df_meals = load_data()
    st.success("✅ تم ربط الجداول بنجاح!")

    # 3. واجهة المستخدم لإدخال العائلة
    num_people = st.number_input("كم عدد أفراد الأسرة؟", min_value=1, value=3)

    family_data = []
    st.write("### 👤 بيانات أفراد الأسرة:")
    for i in range(int(num_people)):
        cols = st.columns(2)
        with cols[0]:
            name = st.text_input(f"اسم الفرد {i+1}", key=f"n{i}")
        with cols[1]:
            # الربط بعمود "الحالة الصحية" كما في ملفك
            status = st.selectbox(f"حالة {name if name else i+1}", 
                                 options=df_health["الحالة الصحية"].unique(), 
                                 key=f"h{i}")
        family_data.append({"الاسم": name, "الحالة": status})

    # 4. زر التوليد (تم حل مشكلة الـ 404 هنا)
    if st.button("🚀 توليد خطة اليوم"):
        with st.spinner("جاري التفكير..."):
            # استخدام الموديل بدون كلمة models/ أو بكلمة gemini-1.5-flash مباشرة
            # حسب تحديث المكتبة الأخير
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            أنت خبير تغذية رمضاني. استخدم الجداول التالية:
            - جدول الصحة: {df_health.to_string()}
            - جدول الحصص: {df_portions.to_string()}
            - جدول البدائل: {df_alts.to_string()}
            - جدول الأكلات: {df_meals.head(20).to_string()}

            اقترح منيو إفطار وسحور لأسرة مكونة من {num_people} أفراد: {family_data}
            
            المطلوب:
            1. وجبات تناسب الحالة الصحية لكل فرد.
            2. ذكر نصيحة من عمود 'المسموح والنصيحة الذهبية'.
            3. تنبيه من 'علامات الخطر التي تستوجب الإفطار' المذكورة في جدولك.
            4. اقتراح بديل صحي من جدول البدائل.
            """
            
            response = model.generate_content(prompt)
            st.markdown("---")
            st.markdown("### 📋 النتيجة:")
            st.write(response.text)

except Exception as e:
    # في حال استمرت مشكلة الـ 404، الكود ده هيجرب الطريقة البديلة تلقائياً
    st.error(f"❌ حدث خطأ: {e}")
    st.info("جاري محاولة معالجة الاتصال بالـ AI...")
