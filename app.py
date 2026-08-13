import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import os
import io
import requests
import json
from matplotlib.backends.backend_pdf import PdfPages

# ==========================================
# 1. СҮЛЖЭЭ, ПАГЕТИЙН ТОХИРГОО БОЛОН CSS СТАЙЛ
# ==========================================
st.set_page_config(
    page_title="Аутизм Монгол-АНД - Үнэлгээний Систем",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Байгууллагын брэнд өнгө төрх бүхий CSS
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .header-banner {
        background: linear-gradient(135deg, #005088 0%, #002d4d 100%);
        color: white;
        padding: 20px 25px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 12px rgba(0, 80, 136, 0.15);
    }
    .header-banner h1 {
        color: #ffffff !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }
    .header-banner p {
        color: #e2e8f0 !important;
        margin: 5px 0 0 0 !important;
        font-size: 14px !important;
    }
    .stButton>button {
        background-color: #005088;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #00365d;
        color: white;
    }
    .login-box {
        max-width: 450px;
        margin: 60px auto;
        padding: 30px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0, 80, 136, 0.1);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 2. НУУЦ ҮГИЙН ТОХИРГОО (AUTH)
# ==========================================
SYSTEM_PASSWORD = "and2026"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def check_password():
    if not st.session_state["authenticated"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if os.path.exists("logo.jpg"):
                st.image("logo.jpg", width=150)
            st.markdown("""
                <div class="login-box" style="margin-top: 10px;">
                    <h2 style='color: #005088; margin-bottom: 5px;'>Аутизм Монгол-АНД</h2>
                    <p style='color: #64748b; font-size: 14px;'>Ганцаарчилсан сургалтын үнэлгээний систем</p>
                    <hr style='border: 0.5px solid #e2e8f0; margin: 15px 0;'>
                </div>
            """, unsafe_allow_html=True)
            
            pwd_input = st.text_input("Нэвтрэх нууц үг бичнэ үү:", type="password")
            if st.button("Нэвтрэх", use_container_width=True):
                if pwd_input == SYSTEM_PASSWORD:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("🔒 Нууц үг буруу байна! Дахин оролдоно уу.")
        return False
    return True

if not check_password():
    st.stop()


# ==========================================
# 3. GOOGLE SHEETS ДАТА ХОЛБООС
# ==========================================
GSHEET_URL = "https://script.google.com/macros/s/AKfycbyHGCWVdAEtXEKsSsaA4DxduFye0cFXOpHKgS_vLMDymT6Pq2lzKyiYRsSqA2BE8pPxiA/exec"

def load_db_from_gsheet():
    if not GSHEET_URL:
        return pd.DataFrame()
    try:
        res = requests.get(GSHEET_URL, params={'action': 'read'}, timeout=10)
        data = res.json()
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
        elif len(data) == 1:
            return pd.DataFrame(columns=data[0])
    except Exception as e:
        st.error(f"Дата уншихад алдаа гарлаа: {e}")
    return pd.DataFrame()

def save_to_gsheet(data_dict):
    if not GSHEET_URL:
        return False
    try:
        res = requests.get(GSHEET_URL, params={'action': 'write', 'data': json.dumps(data_dict)}, timeout=10)
        return res.status_code == 200
    except Exception as e:
        st.error(f"Хадгалахад алдаа гарлаа: {e}")
        return False


# ==========================================
# 4. ВЭБИЙН ЦЭС БОЛОН ХАЖУУГИЙН СЕКЦ (SIDEBAR)
# ==========================================
# Хажуугийн цэсэнд Лого харуулах
if os.path.exists("logo.jpg"):
    st.sidebar.image("logo.jpg", use_container_width=True)

st.sidebar.markdown("""
    <div style='text-align: center; padding: 5px 0;'>
        <h3 style='color: #005088; margin: 0;'>Аутизм Монгол-АНД</h3>
        <p style='color: #64748b; font-size: 12px; margin-top: 2px;'>Үнэлгээний Систем</p>
    </div>
    <hr style='margin: 10px 0;'>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "Үндсэн цэс:",
    ["📝 Шинэ үнэлгээ хийх", "📈 Ахиц дэвшлийн харьцуулалт", "📅 Үнэлгээний түүх & Дата", "🔒 Гарах"]
)

if menu == "🔒 Гарах":
    st.session_state["authenticated"] = False
    st.rerun()

# ------------------------------------------
# ХЭСЭГ 1: ШИНЭ ҮНЭЛГЭЭ ХИЙХ
# ------------------------------------------
if menu == "📝 Шинэ үнэлгээ хийх":
    banner_col1, banner_col2 = st.columns([1, 5])
    with banner_col1:
        if os.path.exists("logo.jpg"):
            st.image("logo.jpg", width=100)
    with banner_col2:
        st.markdown("""
            <div class="header-banner">
                <h1>📝 "Аутизм Монгол-АНД" ТББ - Шинэ Үнэлгээ</h1>
                <p>Хүүхдийн мэдээлэл болон сургалтын үзүүлэлтүүдийг бөглөнө үү</p>
            </div>
        """, unsafe_allow_html=True)

    with st.form("assessment_form"):
        st.subheader("1. Үндсэн мэдээлэл")
        col1, col2, col3 = st.columns(3)
        with col1:
            child_name = st.text_input("Хүүхдийн нэр:")
        with col2:
            child_age = st.number_input("Нас:", min_value=1, max_value=18, value=5)
        with col3:
            eval_date = st.date_input("Үнэлгээ хийсэн огноо:", datetime.date.today())
            
        psychologist_name = st.selectbox("Үнэлгээ хийсэн сэтгэл зүйч:", ["Г.Хонгорзул", "Г.Чимэдлхам", "Ц.Хулан"])
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("2. Чадваруудын үнэлгээ (1-10 оноо)")
        
        col_a, col_b = st.columns(2)
        with col_a:
            score_cog = st.slider("🧠 Танин мэдэхүй", 1, 10, 5)
            score_comm = st.slider("🗣️ Хэл яриа ба харилцаа", 1, 10, 5)
            score_soc = st.slider("🤝 Нийгэмшихүй & Эмоци", 1, 10, 5)
        with col_b:
            score_motor = st.slider("🏃‍♂️ Хөдөлгөөний хөгжил", 1, 10, 5)
            score_self = st.slider("🥣 Биеэ даах чадвар", 1, 10, 5)
            score_attn = st.slider("🎯 Анхаарал төвлөрөлт", 1, 10, 5)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("3. 📝 Сэтгэл зүйчийн тэмдэглэл & Зөвлөмж")
        notes = st.text_area(
            "Хүүхдийн онцлог, ажиглагдсан зан төлөв, цаашид анхаарах зөвлөмжүүд:",
            placeholder="Жишээ нь: Харааны хавьтал сайн, даалгавар гүйцэтгэхдээ анхааралтай байсан..."
        )

        submit_btn = st.form_submit_button("💾 Үнэлгээг хадгалах & Тайлан гаргах", use_container_width=True)

    if submit_btn:
        if not child_name:
            st.warning("⚠️ Хүүхдийн нэрийг заавал бичнэ үү!")
        else:
            data = {
                "Огноо": str(eval_date),
                "Хүүхдийн нэр": child_name.strip(),
                "Нас": child_age,
                "Сэтгэл зүйч": psychologist_name,
                "Танин мэдэхүй": score_cog,
                "Хэл яриа": score_comm,
                "Нийгэмшихүй": score_soc,
                "Хөдөлгөөн": score_motor,
                "Биеэ даах": score_self,
                "Анхаарал": score_attn,
                "Тэмдэглэл": notes
            }
            
            with st.spinner("Google Sheet рүү хадгалж байна..."):
                success = save_to_gsheet(data)
                
            if success:
                st.success("✅ Үнэлгээ Google Sheets рүү амжилттай хадгалагдлаа!")
                
                st.markdown("<hr>", unsafe_allow_html=True)
                st.subheader(f"📊 {child_name} - Үнэлгээний Нэгдсэн Тайлан")
                
                categories = ['Танин мэдэхүй', 'Хэл яриа', 'Нийгэмшихүй', 'Хөдөлгөөн', 'Биеэ даах', 'Анхаарал']
                values = [score_cog, score_comm, score_soc, score_motor, score_self, score_attn]
                
                angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
                values_plot = values + [values[0]]
                angles_plot = angles + [angles[0]]

                fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
                ax.fill(angles_plot, values_plot, color='#005088', alpha=0.3)
                ax.plot(angles_plot, values_plot, color='#005088', linewidth=2)
                ax.set_xticks(angles)
                ax.set_xticklabels(categories, fontsize=10, fontweight='bold')
                ax.set_ylim(0, 10)
                plt.title(f"Хөгжлийн профиль - {child_name}", size=13, color='#005088', pad=20, weight='bold')
                
                col_chart, col_info = st.columns([1, 1])
                with col_chart:
                    st.pyplot(fig)
                with col_info:
                    st.markdown(f"**Хүүхдийн нэр:** {child_name}")
                    st.markdown(f"**Нас:** {child_age}")
                    st.markdown(f"**Огноо:** {eval_date}")
                    st.markdown(f"**Сэтгэл зүйч:** {psychologist_name}")
                    st.info(f"**Сэтгэл зүйчийн тэмдэглэл:**\n\n{notes if notes else 'Тэмдэглэл бичигдээгүй.'}")

                pdf_buffer = io.BytesIO()
                with PdfPages(pdf_buffer) as pdf:
                    pdf.savefig(fig, bbox_inches='tight')
                pdf_buffer.seek(0)
                
                st.download_button(
                    label="📄 Үнэлгээний графикийг PDF-ээр татах",
                    data=pdf_buffer,
                    file_name=f"{child_name}_үнэлгээ_{eval_date}.pdf",
                    mime="application/pdf"
                )

# ------------------------------------------
# ХЭСЭГ 2: АХИЦ ДЭВШЛИЙН ХАРЬЦУУЛАЛТ
# ------------------------------------------
elif menu == "📈 Ахиц дэвшлийн харьцуулалт":
    st.markdown("""
        <div class="header-banner">
            <h1>📈 Ахиц Дэвшлийн Харьцуулалт</h1>
            <p>Хүүхдийн гарааны болон давтан үнэлгээний өөрчлөлтийг шинжлэх</p>
        </div>
    """, unsafe_allow_html=True)
    
    df = load_db_from_gsheet()
    if df.empty or "Хүүхдийн нэр" not in df.columns:
        st.info("Одоогоор мэдээллийн санд үнэлгээ хадгалагдаагүй байна.")
    else:
        children = df["Хүүхдийн нэр"].unique().tolist()
        selected_child = st.selectbox("Харьцуулах хүүхдийг сонгоно уу:", children)
        
        child_df = df[df["Хүүхдийн нэр"] == selected_child].sort_values(by="Огноо")
        
        if len(child_df) < 2:
            st.warning(f"⚠️ {selected_child} хүүхдийн үнэлгээ одоогоор 1 удаа хийгдсэн байна. Давтан үнэлгээ хийсний дараа ахиц харьцуулах боломжтой.")
            st.dataframe(child_df)
        else:
            st.success(f"Нийт {len(child_df)} удаагийн үнэлгээ олдлоо.")
            
            baseline = child_df.iloc[0]
            latest = child_df.iloc[-1]
            
            categories = ['Танин мэдэхүй', 'Хэл яриа', 'Нийгэмшихүй', 'Хөдөлгөөн', 'Биеэ даах', 'Анхаарал']
            
            base_scores = [float(baseline.get(c, 0)) for c in categories]
            latest_scores = [float(latest.get(c, 0)) for c in categories]
            
            x = np.arange(len(categories))
            width = 0.35
            
            fig, ax = plt.subplots(figsize=(10, 5))
            rects1 = ax.bar(x - width/2, base_scores, width, label=f'Эхний ({baseline["Огноо"]})', color='#94a3b8')
            rects2 = ax.bar(x + width/2, latest_scores, width, label=f'Сүүлийн ({latest["Огноо"]})', color='#005088')
            
            ax.set_ylabel('Оноо (1-10)')
            ax.set_title(f'{selected_child} - Ахиц дэвшлийн харьцуулалт', fontsize=14, fontweight='bold', pad=15)
            ax.set_xticks(x)
            ax.set_xticklabels(categories, fontweight='bold')
            ax.legend()
            ax.set_ylim(0, 12)
            
            ax.bar_label(rects1, padding=3)
            ax.bar_label(rects2, padding=3)
            
            st.pyplot(fig)
            
            st.subheader("📊 Чадваруудын өсөлтийн хувь")
            cols = st.columns(len(categories))
            for i, cat in enumerate(categories):
                diff = latest_scores[i] - base_scores[i]
                cols[i].metric(label=cat, value=f"{latest_scores[i]} оноо", delta=f"{diff:+} оноо")

# ------------------------------------------
# ХЭСЭГ 3: ҮНЭЛГЭЭНИЙ ТҮҮХ & ДАТА
# ------------------------------------------
elif menu == "📅 Үнэлгээний түүх & Дата":
    st.markdown("""
        <div class="header-banner">
            <h1>📅 Үнэлгээний Нэгдсэн Түүх</h1>
            <p>Google Sheet дээр хадгалагдсан бүх үнэлгээний санг харах болон шүүх</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("Мэдээллийн сангаас датаг ачаалж байна..."):
        df = load_db_from_gsheet()
        
    if not df.empty:
        search_term = st.text_input("🔍 Хүүхдийн нэрээр хайх:")
        if search_term:
            df = df[df["Хүүхдийн нэр"].astype(str).str.contains(search_term, case=False, na=False)]
            
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Бүх датаг Excel (CSV) файлаар татах",
            data=csv,
            file_name=f"Аутизм_Монгол_АНД_Үнэлгээнүүд_{datetime.date.today()}.csv",
            mime="text/csv"
        )
    else:
        st.info("Одоогоор хадгалагдсан дата олдсонгүй.")
