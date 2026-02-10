import streamlit as st
import pandas as pd
import google.generativeai as genai

# إعداد الـ API
if "api_key" in st.secrets:
    genai.configure(api_key=st.secrets["api_key"])
else:
    st.error("⚠️ يرجى ضبط الـ api_key في Secrets")

# --- تصميم الواجهة (CSS) لجعلها ملونة وجميلة ---
st.markdown("""
    <style>
    .main {
        background-color: #fcf8f0;
    }
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 20px;
        border: None;
        width: 100%;
        height: 3em;
        font-weight: bold;
        font-size: 20px;
    }
    .stButton>button:hover {
        background-color: #1b5e20;
        color: #ffca28;
    }
    h1 {
        color: #1b5e20;
        text-align: center;
        font-family: 'Amiri', serif;
    }
    .stSelectbox, .stTextInput, .stNumberInput {
        background-color: #ffffff;
        border-radius: 10px;
        border: 1px solid #2e7d32;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌙 دليل مدبرة رمضان الذكي")
st.markdown("<h4 style='text-align: center; color: #555;'>نظمي مائدتك بذكاء وصحة لكل العيلة</h4>", unsafe_allow_html=True)

try:
    # تحميل البيانات
    @st.cache_data
    def load_data():
        df1 = pd.read_csv("table1.csv")
        df2 = pd.read_csv("table2.csv")
        df3 = pd.read_csv("table3.csv")
        df_m = pd.read_csv("meals.csv")
        df1.columns = df1.columns.str.strip()
        return df1, df2, df3, df_m

    df_health, df_portions, df_alts, df_meals = load_data()
    
    st.sidebar.success("✅ الجداول مربوطة")
    
    # واجهة إدخال بيانات العائلة
    with st.container():
        st.write("### 🏠 بيانات أفراد الأسرة")
        num_people = st.number_input("كم عدد أفراد الأسرة اليوم؟", min_value=1, value=3)
        
        family_data = []
        for i in range(int(num_people)):
            col1, col2 = st.columns([1, 2])
            with col1:
                name = st.text_input(f"الاسم {i+1}", key=f"n{i}")
            with col2:
                status = st.selectbox(f"الحالة الصحية لـ {name if name else i+1}", 
                                     options=df_health["الحالة الصحية"].unique(), 
                                     key=f"h{i}")
            family_data.append({"الاسم": name, "الحالة": status})

    st.write("---")

    # زر التوليد
    if st.button("🚀 اقترحي لي المنيو والنصائح"):
        with st.spinner("✨ جاري تحضير منيو رمضاني صحي..."):
            # استخدام الإصدار الأحدث لتجنب خطأ 404
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            
            prompt = f"""
            بصفتك خبير تغذية، استخدم هذه الجداول:
            - حالات الصحة: {df_health.to_string()}
            - حصص الطعام: {df_portions.to_string()}
            - البدائل: {df_alts.to_string()}
            - الأكلات: {df_meals.head(25).to_string()}

            المطلوب منيو إفطار وسحور لأسرة: {family_data}
            1. وجبات تناسب حالة كل فرد.
            2. لكل فرد: نصيحة من عمود 'المسموح والنصيحة الذهبية' وتنبيه من 'علامات الخطر'.
            3. اقترح بدائل صحية من جدول البدائل.
            4. اجعل الأسلوب مبهجاً ورمضانياً ومنظماً في نقاط.
            """
            
            response = model.generate_content(prompt)
            st.markdown("### 📋 مقترح مدبرة رمضان لليوم:")
            st.info(response.text)

except Exception as e:
    st.error(f"⚠️ حدث تنبيه: {e}")
    st.info("تأكدي من أن الـ API Key مفعل في إعدادات Streamlit Secrets.")
