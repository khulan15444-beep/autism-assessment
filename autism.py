import pandas as pd
import streamlit as st


# CSV файлаас 220 асуултаа унших функц
@st.cache_data
def load_assessment_questions():
  try:
    return pd.read_csv("Гарааны_үнэлгээ_БҮРЭН.csv", encoding="utf-8")
  except Exception as e:
    st.error("CSV файл олдсонгүй! Файлын нэр, байршлыг шалгана уу.")
    return pd.DataFrame()


# Шинэ үнэлгээ хийх цэсний хэсэг
if menu == "📝 Шинэ үнэлгээ хийх (220 асуулт)":
  st.markdown("""
        <div class="header-banner">
            <h1>📝 Шинэ үнэлгээ хийх</h1>
            <p>220 даалгавраар хүүхдийн хөгжлийн үнэлгээг авах</p>
        </div>
    """, unsafe_allow_html=True)

  df_questions = load_assessment_questions()

  if not df_questions.empty:
    child_name = st.text_input(
        "👶 Хүүхдийн нэр:", placeholder="Жишээ: Б.Анар"
    )

    if child_name:
      st.info(f"Судалгаа хийж буй хүүхэд: **{child_name}**")
      scores = {}

      # 1. Үндсэн аймаг тус бүрээр ангилах
      main_domains = df_questions["Үндсэн аймаг"].unique()

      for domain in main_domains:
        with st.expander(f"📁 {domain}", expanded=False):
          domain_df = df_questions[df_questions["Үндсэн аймаг"] == domain]

          # 2. Дэд аймгаар бүлэглэх
          sub_domains = domain_df["Дэд аймаг"].unique()

          for sub in sub_domains:
            st.markdown(
                f"<h4 style='color: #1E88E5;'>🔹 {sub}</h4>",
                unsafe_allow_html=True,
            )
            sub_df = domain_df[domain_df["Дэд аймаг"] == sub]

            # 3. Асуулт бүрийг харуулах
            for idx, row in sub_df.iterrows():
              code = row["Код"]
              task = row["Даалгавар"]

              score = st.radio(
                  label=f"**[{code}]** {task}",
                  options=[
                      "0 - Хийж чадахгүй",
                      "1 - Дэмжлэгтэй хийнэ",
                      "2 - Бие даан хийнэ",
                  ],
                  key=f"{child_name}_{code}",
                  horizontal=True,
              )
              scores[code] = int(score.split(" - ")[0])

      if st.button("💾 Үнэлгээг хадгалах", type="primary"):
        st.balloons()
        st.success(
            f"**{child_name}** хүүхдийн үнэлгээ амжилттай хадгалагдлаа!"
        )