import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. إعداد الـ API
if "api_key" in st.secrets:
    genai.configure(api_key=st.secrets["api_key"])
else:
    st.error("⚠️ يرجى ضبط الـ api_key في Secrets")

st.set_page_config(page_title="مدبرة رمضان", layout="wide")
st.title("🌙 دليل مدبرة رمضان الذكي")

try:
    # 2. تحميل البيانات بالأسماء الجديدة (بدون فواصل)
    @st.cache_data
    def load_data():
        df1 = pd.read_csv("table1.csv")
        df2 = pd.read_csv("table2.csv")
        df3 = pd.read_csv("table3.csv")
        df_m = pd.read_csv("meals.csv")
        # تنظيف أسامي الأعمدة من أي مسافات زائدة
        df1.columns = df1.columns.str.strip()
        return df1, df2, df3, df_m

    df_health, df_portions, df_alts, df_meals = load_data()
    st.success("✅ الجداول مربوطة وجاهزة!")

    # 3. إدخال بيانات العائلة
    num_people = st.number_input("عدد أفراد الأسرة", min_value=1, max_value=15, value=3)

    family_data = []
    st.write("### 👤 بيانات أفراد الأسرة:")
    for i in range(int(num_people)):
        cols = st.columns(2)
        with cols[0]:
            name = st.text_input(f"اسم الفرد {i+1}", key=f"n{i}", placeholder="الاسم")
        with cols[1]:
            # استخدام اسم العمود الصحيح "الحالة الصحية" من ملفك
            status = st.selectbox(f"حالة {name if name else i+1}", 
                                 options=df_health["الحالة الصحية"].unique(), 
                                 key=f"h{i}")
        family_data.append({"الاسم": name, "الحالة": status})

    # 4. زر التوليد والربط مع Gemini
    if st.button("🚀 توليد خطة اليوم المخصصة"):
        with st.spinner("جاري تحليل الجداول وتحضير المنيو..."):
            model = genai.GenerativeModel('models/gemini-1.5-flash')
            
            # برومبت يربط كل الملفات ببعضها
            prompt = f"""
            بصفتك خبير تغذية، استخدم الجداول التالية:
            - حالات الصحة: {df_health.to_string()}
            - حصص الطعام: {df_portions.to_string()}
            - البدائل الصحية: {df_alts.to_string()}
            - قائمة الأكلات: {df_meals.head(30).to_string()}

            اقترح منيو إفطار وسحور لأسرة مكونة من {num_people} أفراد: {family_data}
            
            المطلوب بدقة:
            1. وجبات مناسبة لكل حالة (مثلاً مريض السكر يقلل نشويات، مريض الضغط يقلل ملح).
            2. نصيحة لكل فرد بناءً على 'المسموح والنصيحة الذهبية' في جدول الصحة.
            3. تنبيه من 'علامات الخطر التي تستوجب الإفطار' لكل حالة.
            4. حساب كمية تقريبية بناءً على 'الحصة المقترحة للفرد' من جدول الحصص.
            """
            
            response = model.generate_content(prompt)
            st.markdown("---")
            st.markdown("### 📋 النتيجة المقترحة من مدبرة رمضان:")
            st.write(response.text)

except Exception as e:
    st.error(f"❌ حدث خطأ: {e}")
    st.info("تأكدي أن الملفات في GitHub هي: table1.csv, table2.csv, table3.csv, meals.csv")
