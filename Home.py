import streamlit as st
import psycopg2

st.set_page_config(page_title="Swim Lesson Tracker", layout="wide")

st.title("🏊 Swim Lesson Progress Tracker")

st.write("Welcome! This dashboard shows all students, their levels, and lesson information.")

# Connect to DB
conn = psycopg2.connect(st.secrets["DB_URL"])
cur = conn.cursor()

# Pull student data with level + latest lesson
cur.execute("""
SELECT 
    s.first_name,
    s.last_name,
    sl.level_name,
    ls.notes,
    ls.lesson_goal
FROM students s
LEFT JOIN student_levels sl ON s.student_level_id = sl.id
LEFT JOIN lesson_sessions ls ON s.id = ls.student_id
ORDER BY s.last_name;
""")

rows = cur.fetchall()

st.subheader("Your Students")

if not rows:
    st.info("No students found yet.")
else:
    for row in rows:
        first, last, level, notes, goal = row

        st.markdown(f"""
        **{first} {last}**  
        Level: {level if level else 'N/A'}  
        Last Lesson Notes: {notes if notes else 'N/A'}  
        Upcoming Goal: {goal if goal else 'N/A'}
        """)
        st.markdown("---")

cur.close()
conn.close()
