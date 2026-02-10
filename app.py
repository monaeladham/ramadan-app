import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. إعداد الـ API
if "api_key" in st.secrets:
    genai.configure(api_key=st.secrets["api_key"])
else:
    st.error("⚠️ يرجى ضبط الـ api_key في Secrets")

# --- تنسيق الواجهة بألوان رمضانية ---
st.markdown("""
    <style>
    .main { background-color: #fdfaf5; }
    .stButton>button {
        background: linear-gradient(to right, #1e5128, #4e944f);
        color: white; border-radius: 15px; font-size: 20px; font-weight: bold; border: none; padding: 10px;
    }
    .status-card {
        background-color: #ffffff; padding: 15px; border-radius: 10px;
        border-right: 5px solid #1e5128; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    h1 { color: #1e5128; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌙 مدبرة رمضان الذكية")

try:
    # 2. تحميل البيانات (تأكدي أن الأسماء table1.csv وهكذا)
    @st.cache_data
    def load_data():
        d1 = pd.read_csv("table1.csv")
        d2 = pd.read_csv("table2.csv")
        d3 = pd.read_csv("table3.csv")
        dm = pd.read_csv("meals.csv")
        d1.columns = d1.columns.str.strip()
        return d1, d2, d3, dm

    df_h, df_p, df_a, df_m = load_data()
    st.sidebar.success("✅ الجداول متصلة")

    # 3. مدخلات المستخدم
    with st.expander("👤 إعدادات العائلة", expanded=True):
        num = st.number_input("عدد الأفراد", min_value=1, value=2)
        family = []
        for i in range(int(num)):
            c1, c2 = st.columns(2)
            with c1: name = st.text_input(f"اسم الفرد {i+1}", key=f"n{i}")
            with c2: status = st.selectbox(f"الحالة الصحية", options=df_h["الحالة الصحية"].unique(), key=f"h{i}")
            family.append({"الاسم": name, "الحالة": status})

    # 4. زر التوليد مع حل مشكلة الـ 404
    if st.button("🚀 اقترحي لي المنيو"):
        with st.spinner("✨ جاري الاتصال بالعقل الذكي..."):
            # محاولة مناداة الموديل بـ 3 طرق مختلفة لحل مشكلة الـ 404
            model_names = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'models/gemini-1.5-flash']
            success = False
            
            for m_name in model_names:
                try:
                    model = genai.GenerativeModel(m_name)
                    # البرومبت يربط كل جداولك
                    prompt = f"""
                    أنت خبير تغذية. بناءً على هذه الجداول:
                    الخلفية الطبية: {df_h.to_string()}
                    الحصص والبدائل: {df_p.to_string()}, {df_a.to_string()}
                    قائمة الأكلات: {df_m.head(20).to_string()}

                    اقترح منيو إفطار وسحور للأسرة: {family}
                    ركز على: نصيحة 'المسموح' و'علامات الخطر' من جدول الصحة لكل فرد.
                    اجعل الرد منظماً جداً بأسماء الأفراد.
                    """
                    response = model.generate_content(prompt)
                    st.markdown("### 📋 المنيو الصحي المقترح:")
                    st.success(response.text)
                    success = True
                    break # لو اشتغل يوقف تجربة الباقي
                except:
                    continue
            
            if not success:
                st.error("عذراً، جوجل يرفض الاتصال حالياً. تأكدي من صلاحية الـ API Key.")

except Exception as e:
    st.error(f"خطأ في البيانات: {e}")
