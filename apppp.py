import datetime
import pandas as pd
import streamlit as st


# 1. CSV файлаас 220 асуултаа унших функц
@st.cache_data
def load_assessment_questions():
  try:
    df = pd.read_csv("Гарааны_үнэлгээ_БҮРЭН.csv", encoding="utf-8")
    # Хэрэв "Оноо" багана байхгүй бол 0 оноотойгоор шинээр нэмнэ
    if "Оноо" not in df.columns:
      df["Оноо"] = 0
    return df
  except Exception as e:
    st.error("CSV файл олдсонгүй! Файлын нэр, байршлыг шалгана уу.")
    return pd.DataFrame()


# 2. Шинэ үнэлгээ хийх цэс
if menu == "📝 Шинэ үнэлгээ хийх (220 асуулт)":

  st.markdown("""
        <div class="header-banner">
            <h1>📝 Шинэ үнэлгээ хийх</h1>
            <p>220 даалгаврыг 0-5 хүртэлх оноогоор хүснэгтээс шууд үнэлэх</p>
        </div>
    """, unsafe_allow_html=True)

  df_questions = load_assessment_questions()

  if not df_questions.empty:
    col1, col2 = st.columns(2)
    with col1:
      child_name = st.text_input(
          "👶 Хүүхдийн нэр:", placeholder="Жишээ: Б.Анар"
      )
    with col2:
      eval_date = st.date_input("📅 Үнэлгээний огноо:", datetime.date.today())

    if child_name:
      st.info(
          f"Үнэлгээ хийж буй хүүхэд: **{child_name}** | Огноо: **{eval_date}**"
      )
      st.write(
          "💡 **Заавар:** Доорх хүснэгтийн **'Оноо'** баганад **0-ээс 5** хүртэлх"
          " оноог оруулна уу."
      )

      # Excel/CSV загвартай шууд засах боломжтой хүснэгт
      edited_df = st.data_editor(
          df_questions,
          column_config={
              "Оноо": st.column_config.NumberColumn(
                  "Оноо (0-5)",
                  help="0, 1, 2, 3, 4, 5 онооны аль нэгийг оруулна уу",
                  min_value=0,
                  max_value=5,
                  step=1,
                  default=0,
              )
          },
          # "Оноо"-ноос бусад баганыг өөрчлөхөөс хамгаална
          disabled=[col for col in df_questions.columns if col != "Оноо"],
          use_container_width=True,
          num_rows="fixed",
          height=600,  # 220 асуултыг гүйлгэж харах цонхны өндөр
      )

      # Нийт онооны нийлбэр
      total_score = edited_df["Оноо"].sum()
      st.metric(label="📊 Нийт авсан оноо:", value=f"{total_score} / 1100")

      # Хадгалах товчлуур
      if st.button("💾 Үнэлгээг хадгалах", type="primary"):
        st.balloons()
        st.success(
            f"**{child_name}** хүүхдийн үнэлгээ (Нийт {total_score} оноо)"
            " амжилттай хадгалагдлаа!"
        )