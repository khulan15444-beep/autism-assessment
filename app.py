import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import os
import textwrap
import io
import requests
import json

# --- 1. Вэбийн ерөнхий тохиргоо ---
st.set_page_config(page_title='"Аутизм Монгол-АНД" ТББ ганцаарчилсан сургалтын үнэлгээ', layout="wide")

# 🔗 Google Apps Script URL (Таны бэлтгэсэн линк)
GSHEET_URL = "https://script.google.com/macros/s/AKfycbyHGCWVdAEtXEKsSsaA4DxduFye0cFXOpHKgS_vLMDymT6Pq2lzKyiYRsSqA2BE8pPxiA/exec"

# Google Sheet-ээс дата унших функц
def load_db_from_gsheet():
    if not GSHEET_URL:
        return pd.DataFrame()
    try:
        res = requests.get(GSHEET_URL, params={'action': 'read'})
        data = res.json()
        if len(data) > 1:
            df = pd.DataFrame(data[1:], columns=data[0])
            return df
        elif len(data) == 1:
            return pd.DataFrame(columns=data[0])
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Дата харахад алдаа гарлаа: {e}")
        return pd.DataFrame()

# Excel файлаас асуулт ялгах ухаалаг функц
@st.cache_data
def parse_excel_questions(file):
    try:
        df = pd.read_excel(file, sheet_name='Эх хувь', header=None)
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

# --- 2. Вэбийн толгой хэсэг ---
st.title('🧩 "Аутизм Монгол-АНД" ТББ ганцаарчилсан сургалтын үнэлгээ')
st.markdown("---")

tab1, tab2 = st.tabs(["📝 Шинэ үнэлгээ хийх", "📅 Түүх харах (Календар)"])

# ==========================================
# TAB 1: ШИНЭ ҮНЭЛГЭЭ ХИЙХ
# ==========================================
with tab1:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        child_name = st.text_input("Хүүхдийн овог, нэр:", placeholder="Жишээ: Б.Амартайван")
    with col2:
        eval_date = st.date_input("Үнэлгээ хийсэн огноо:", datetime.date.today())
    with col3:
        psychologist = st.selectbox("Үнэлгээ хийсэн сэтгэл зүйч:", ["Г.Хонгорзул", "Г.Чимэдлхам", "Ц.Хулан"])

    st.markdown("---")
    
    uploaded_file = st.file_uploader("Үнэлгээний хуудас (Гарааны-үнэлгээ.xlsx) файлаа оруулна уу", type=['xlsx'])
    
    if uploaded_file is not None:
        parsed_data = parse_excel_questions(uploaded_file)
        
        if parsed_data:
            st.info("Асуулт тус бүрт 0-5 хооронд оноо өгнө үү. (5 оноо = 100%)")
            
            eval_scores = {}
            
            with st.form("evaluation_form"):
                for sub_cat, questions in parsed_data.items():
                    if not questions: continue
                    
                    with st.expander(f"📁 {sub_cat} ({len(questions)} асуулт)", expanded=False):
                        for q in questions:
                            q_key = f"[{q['code']}] {q['question']}"
                            st.markdown(f"**{q_key}**")
                            eval_scores[q_key] = st.radio("Оноо:", options=[0, 1, 2, 3, 4, 5], horizontal=True, key=f"score_{q['code']}")
                            st.markdown("---")
                
                submitted = st.form_submit_button("Үнэлгээг Хадгалах & Тайлан Харах", use_container_width=True)
            
            if submitted:
                if not child_name.strip():
                    st.error("Алдаа: Хүүхдийн нэрийг заавал оруулна уу!")
                else:
                    sub_category_percentages = {}
                    for sub_cat, questions in parsed_data.items():
                        if not questions: continue
                        total_score = sum([eval_scores[f"[{q['code']}] {q['question']}"] for q in questions])
                        max_possible_score = len(questions) * 5
                        percentage = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
                        sub_category_percentages[sub_cat] = percentage
                    
                    st.markdown("## 📊 Үр дүнгийн тайлан")
                    fig, ax = plt.subplots(figsize=(8.27, 11.69)) 
                    
                    categories = list(sub_category_percentages.keys())
                    percentages = list(sub_category_percentages.values())
                    
                    y_pos = range(len(categories))
                    bars = ax.barh(y_pos, percentages, align='center', color='#2ca02c', edgecolor='black')
                    
                    wrapped_labels = [textwrap.fill(cat, width=40) for cat in categories]
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
                        f'Хүүхдийн нэр: {child_name} | Огноо: {eval_date.strftime("%Y-%m-%d")}\n'
                        f'Үнэлгээ хийсэн сэтгэл зүйч: {psychologist}'
                    )
                    plt.title(title_text, fontsize=13, fontweight='bold', pad=20)
                    
                    ax.grid(axis='x', linestyle='--', alpha=0.7)
                    plt.tight_layout()
                    
                    st.pyplot(fig)
                    
                    buf = io.BytesIO()
                    fig.savefig(buf, format="png", bbox_inches='tight')
                    buf.seek(0)
                    st.download_button(
                        label="📥 Диаграммыг зураг (PNG) хэлбэрээр татах",
                        data=buf,
                        file_name=f"{child_name}_үнэлгээ_{eval_date}.png",
                        mime="image/png"
                    )
                    
                    # Google Sheets рүү хадгалах дата бэлдэх
                    save_data = {
                        'Огноо': str(eval_date), 
                        'Хүүхдийн нэр': child_name,
                        'Сэтгэл зүйч': psychologist
                    }
                    for cat, perc in sub_category_percentages.items():
                        save_data[f"{cat} (%)"] = round(perc, 1)
                        
                    # Google Sheets рүү ИЛГЭЭХ
                    try:
                        res = requests.get(GSHEET_URL, params={'action': 'write', 'data': json.dumps(save_data)})
                        if res.status_code == 200:
                            st.success("Үнэлгээ Google Sheets рүү насан туршдаа найдвартай хадгалагдлаа! 🟢")
                        else:
                            st.error("Google Sheets рүү хадгалахад алдаа гарлаа.")
                    except Exception as e:
                        st.error(f"Холболтын алдаа гарлаа: {e}")

# ==========================================
# TAB 2: ТҮҮХ ХАРАХ (КАЛЕНДАР)
# ==========================================
with tab2:
    st.subheader("📅 Үнэлгээний түүх хайх (Google Sheets-ээс)")
    search_date = st.date_input("Календариас өдөр сонгоно уу:")
    
    with st.spinner("Google Sheets-ээс дата уншиж байна..."):
        df_history = load_db_from_gsheet()
    
    if not df_history.empty and 'Огноо' in df_history.columns:
        df_history['Огноо_dt'] = pd.to_datetime(df_history['Огноо'], errors='coerce').dt.date
        filtered_df = df_history[df_history['Огноо_dt'] == search_date]
        
        if not filtered_df.empty:
            st.write(f"**{search_date}** өдөр нийт **{len(filtered_df)}** хүүхдэд үнэлгээ хийсэн байна:")
            display_df = filtered_df.drop(columns=['Огноо_dt'])
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info(f"{search_date} өдөр үнэлгээний бүртгэл байхгүй байна.")
    else:
        st.warning("Одоогоор Google Sheets дээр үнэлгээ хадгалагдаагүй байна.")
