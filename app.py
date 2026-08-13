import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import os
import textwrap
import io
import requests
import json
from matplotlib.backends.backend_pdf import PdfPages

# ==========================================
# 1. ВЭБИЙН ТОХИРГОО БОЛОН CSS СТАЙЛ
# ==========================================
st.set_page_config(
    page_title="Аутизм Монгол-АНД - Үнэлгээний Систем",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        font-size: 24px !important;
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
                    st.error("🔒 Нууц үг буруу байна!")
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
# 4. EXCEL-ЭЭС 220 АСУУЛТ УНШИХ ФУНКЦ
# ==========================================
@st.cache_data
def parse_excel_questions(file_source):
    try:
        df = pd.read_excel(file_source, sheet_name='Эх хувь', header=None)
        assessment_data = {}
        current_sub_category = "Ерөнхий"
        
        for index, row in df.iterrows():
            col0 = str(row[0]).strip() if pd.notna(row[0]) else ""
            col1 = str(row[1]).strip() if pd.notna(row[1]) else ""
            
            if col0 != "" and col1 == "" and col0 not in ["Нэр:", "Код", "nan"]:
                if len(col0) < 50:
                    current_sub_category = col0
                    if current_sub_category not in assessment_data:
                        assessment_data[current_sub_category] = []
                        
            elif col0 != "" and col1 != "" and col0 != "Код":
                if current_sub_category not in assessment_data:
                    assessment_data[current_sub_category] = []
                assessment_data[current_sub_category].append({"code": col0, "question": col1})
        return assessment_data
    except Exception as e:
        st.error(f"Файл уншихад алдаа гарлаа: {e}")
        return None


# ==========================================
# 5. ХАЖУУГИЙН ЦЭС (SIDEBAR)
# ==========================================
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
    ["📝 Шинэ үнэлгээ хийх (220 асуулт)", "📈 Ахиц дэвшлийн харьцуулалт", "📅 Үнэлгээний түүх & Дата", "🔒 Гарах"]
)

if menu == "🔒 Гарах":
    st.session_state["authenticated"] = False
    st.rerun()

# ------------------------------------------
# ХЭСЭГ 1: ШИНЭ ҮНЭЛГЭЭ ХИЙХ
# ------------------------------------------
if menu == "📝 Шинэ үнэлгээ хийх (220 асуулт)":
    banner_col1, banner_col2 = st.columns([1, 5])
    with banner_col1:
        if os.path.exists("logo.jpg"):
            st.image("logo.jpg", width=100)
    with banner_col2:
        st.markdown("""
            <div class="header-banner">
                <h1>📝 "Аутизм Монгол-АНД" ТББ - Ганцаарчилсан Сургалтын Үнэлгээ</h1>
                <p>Хүүхдийн мэдээллийг бөглөн 220 асуултад оноо өгнө үү</p>
            </div>
        """, unsafe_allow_html=True)

    # 1. Excel файл унших (Репозитор дахь эсвэл Upload хийсэн)
    parsed_data = None
    if os.path.exists("Гарааны-үнэлгээ.xlsx"):
        parsed_data = parse_excel_questions("Гарааны-үнэлгээ.xlsx")
    else:
        uploaded_file = st.file_uploader("Үнэлгээний хуудас (Гарааны-үнэлгээ.xlsx) файлаа оруулна уу", type=['xlsx'])
        if uploaded_file is not None:
            parsed_data = parse_excel_questions(uploaded_file)

    if parsed_data:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            child_name = st.text_input("Хүүхдийн нэр:", placeholder="Жишээ: Б.Амартайван")
        with col2:
            child_age = st.number_input("Нас:", min_value=1, max_value=18, value=5)
        with col3:
            eval_date = st.date_input("Үнэлгээ хийсэн огноо:", datetime.date.today())
        with col4:
            psychologist_name = st.selectbox("Үнэлгээ хийсэн сэтгэл зүйч:", ["Г.Хонгорзул", "Г.Чимэдлхам", "Ц.Хулан"])

        st.info("💡 Асуулт тус бүрт 0-5 хооронд оноо өгнө үү. (5 оноо = 100%)")
        
        eval_scores = {}
        
        with st.form("evaluation_form"):
            for sub_cat, questions in parsed_data.items():
                if not questions: continue
                
                with st.expander(f"📁 {sub_cat} ({len(questions)} асуулт)", expanded=False):
                    for q in questions:
                        q_key = f"[{q['code']}] {q['question']}"
                        st.markdown(f"**{q_key}**")
                        eval_scores[q_key] = st.radio(
                            "Оноо:", 
                            options=[0, 1, 2, 3, 4, 5], 
                            horizontal=True, 
                            key=f"score_{q['code']}"
                        )
                        st.markdown("---")
            
            st.markdown("### 📝 Сэтгэл зүйчийн тэмдэглэл & Зөвлөмж")
            notes = st.text_area(
                "Хүүхдийн онцлог, ажиглагдсан зан төлөв, цаашид анхаарах зөвлөмжүүд:",
                placeholder="Жишээ нь: Харааны хавьтал сайн, даалгавар гүйцэтгэхдээ анхааралтай байсан..."
            )

            submit_btn = st.form_submit_button("💾 Үнэлгээг хадгалах & Тайлан харах", use_container_width=True)

        if submit_btn:
            if not child_name.strip():
                st.error("⚠️ Алдаа: Хүүхдийн нэрийг заавал оруулна уу!")
            else:
                sub_category_percentages = {}
                for sub_cat, questions in parsed_data.items():
                    if not questions: continue
                    total_score = sum([eval_scores[f"[{q['code']}] {q['question']}"] for q in questions])
                    max_possible_score = len(questions) * 5
                    percentage = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
                    sub_category_percentages[sub_cat] = percentage
                
                # Google Sheets рүү хадгалах дата бэлтгэх
                save_data = {
                    'Огноо': str(eval_date), 
                    'Хүүхдийн нэр': child_name.strip(),
                    'Нас': child_age,
                    'Сэтгэл зүйч': psychologist_name,
                    'Тэмдэглэл': notes
                }
                for cat, perc in sub_category_percentages.items():
                    save_data[f"{cat} (%)"] = round(perc, 1)

                with st.spinner("Google Sheets рүү хадгалж байна..."):
                    success = save_to_gsheet(save_data)

                if success:
                    st.success("✅ Үнэлгээ Google Sheets рүү амжилттай хадгалагдлаа!")

                # 📊 ТАЙЛАН БА ГРАФИК
                st.markdown("## 📊 Үр дүнгийн тайлан")
                fig, ax = plt.subplots(figsize=(8.27, 11.69)) 
                
                categories = list(sub_category_percentages.keys())
                percentages = list(sub_category_percentages.values())
                
                y_pos = range(len(categories))
                bars = ax.barh(y_pos, percentages, align='center', color='#005088', edgecolor='black')
                
                wrapped_labels = [textwrap.fill(cat, width=38) for cat in categories]
                ax.set_yticks(y_pos)
                ax.set_yticklabels(wrapped_labels, fontsize=10)
                ax.invert_yaxis() 
                
                ax.set_xlabel('Хөгжлийн түвшин (%)', fontsize=12)
                ax.set_xlim(0, 100) 
                
                for bar in bars:
                    width = bar.get_width()
                    ax.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width:.1f}%', 
                            ha='left', va='center', fontsize=10, fontweight='bold')
                
                title_text = (
                    f'"Аутизм Монгол-АНД" ТББ - Ганцаарчилсан сургалтын үнэлгээ\n\n'
                    f'Хүүхдийн нэр: {child_name} | Нас: {child_age} | Огноо: {eval_date.strftime("%Y-%m-%d")}\n'
                    f'Сэтгэл зүйч: {psychologist_name}'
                )
                plt.title(title_text, fontsize=12, fontweight='bold', pad=20)
                ax.grid(axis='x', linestyle='--', alpha=0.7)
                plt.tight_layout()
                
                col_chart, col_info = st.columns([3, 2])
                with col_chart:
                    st.pyplot(fig)
                with col_info:
                    st.markdown(f"### 📋 Хүүхдийн мэдээлэл")
                    st.write(f"**Нэр:** {child_name}")
                    st.write(f"**Нас:** {child_age}")
                    st.write(f"**Үнэлгээ хийсэн огноо:** {eval_date}")
                    st.write(f"**Сэтгэл зүйч:** {psychologist_name}")
                    st.info(f"**Сэтгэл зүйчийн тэмдэглэл:**\n\n{notes if notes else 'Тэмдэглэл бичигдээгүй.'}")

                # PDF Татах
                pdf_buffer = io.BytesIO()
                with PdfPages(pdf_buffer) as pdf:
                    pdf.savefig(fig, bbox_inches='tight')
                pdf_buffer.seek(0)
                
                st.download_button(
                    label="📄 Үнэлгээний тайланг PDF-ээр татах",
                    data=pdf_buffer,
                    file_name=f"{child_name}_үнэлгээ_{eval_date}.pdf",
                    mime="application/pdf"
                )
    else:
        st.warning("⚠️ 'Гарааны-үнэлгээ.xlsx' файл олдсонгүй. Файлаа оруулан үргэлжлүүлнэ үү.")

# ------------------------------------------
# ХЭСЭГ 2: АХИЦ ДЭВШЛИЙН ХАРЬЦУУЛАЛТ
# ------------------------------------------
elif menu == "📈 Ахиц дэвшлийн харьцуулалт":
    st.markdown("""
        <div class="header-banner">
            <h1>📈 Ахиц Дэвшлийн Харьцуулалт</h1>
            <p>Хүүхдийн анхны болон дараагийн үнэлгээнүүдийн өөрчлөлтийг харьцуулах</p>
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
            
            perc_cols = [c for c in child_df.columns if "(%)" in c]
            
            if perc_cols:
                categories = [c.replace(" (%)", "") for c in perc_cols]
                base_scores = [float(baseline.get(c, 0)) for c in perc_cols]
                latest_scores = [float(latest.get(c, 0)) for c in perc_cols]
                
                y = np.arange(len(categories))
                height = 0.35
                
                fig, ax = plt.subplots(figsize=(10, max(6, len(categories)*0.5)))
                rects1 = ax.barh(y - height/2, base_scores, height, label=f'Анхны ({baseline["Огноо"]})', color='#94a3b8')
                rects2 = ax.barh(y + height/2, latest_scores, height, label=f'Сүүлийн ({latest["Огноо"]})', color='#005088')
                
                ax.set_xlabel('Хөгжлийн түвшин (%)')
                ax.set_title(f'{selected_child} - Ахиц дэвшлийн харьцуулалт', fontsize=14, fontweight='bold', pad=15)
                ax.set_yticks(y)
                ax.set_yticklabels([textwrap.fill(c, width=30) for c in categories], fontweight='bold')
                ax.invert_yaxis()
                ax.legend()
                ax.set_xlim(0, 105)
                
                ax.bar_label(rects1, padding=3, fmt='%.1f%%')
                ax.bar_label(rects2, padding=3, fmt='%.1f%%')
                
                st.pyplot(fig)

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
