import streamlit as st
import psycopg2

st.title("Manage Lesson Sessions")

conn = psycopg2.connect(st.secrets["DB_URL"])
cur = conn.cursor()

cur.execute("""
    SELECT id, first_name || ' ' || last_name AS full_name
    FROM students
    ORDER BY last_name, first_name;
""")
students = cur.fetchall()

student_options = {student[1]: student[0] for student in students}

if not student_options:
    st.info("Add a student first before creating lesson sessions.")
else:
    with st.form("add_lesson_session"):
        st.subheader("Add New Lesson Session")

        selected_student = st.selectbox("Student *", options=student_options.keys())
        student_id = student_options[selected_student]

        lesson_date = st.date_input("Lesson Date *")
        lesson_goal = st.text_input("Lesson Goal *")
        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Add Lesson Session")

        if submitted:
            errors = []

            if not lesson_goal.strip():
                errors.append("Lesson goal is required.")

            if errors:
                for err in errors:
                    st.error(err)
            else:
                cur.execute("""
                    INSERT INTO lesson_sessions (student_id, lesson_date, lesson_goal, notes)
                    VALUES (%s, %s, %s, %s);
                """, (student_id, lesson_date, lesson_goal.strip(), notes.strip()))
                conn.commit()
                st.success("Lesson session added successfully!")

st.subheader("Existing Lesson Sessions")

cur.execute("""
    SELECT
        ls.id,
        s.first_name || ' ' || s.last_name AS student_name,
        ls.lesson_date,
        ls.lesson_goal,
        ls.notes
    FROM lesson_sessions ls
    JOIN students s ON ls.student_id = s.id
    ORDER BY ls.lesson_date DESC, s.last_name;
""")
sessions = cur.fetchall()

if not sessions:
    st.info("No lesson sessions found yet.")
else:
    for session in sessions:
        session_id, student_name, lesson_date, lesson_goal, notes = session

        st.write(f"**{student_name}** — {lesson_date}")
        st.write(f"Goal: {lesson_goal}")
        st.write(f"Notes: {notes if notes else 'No notes'}")
        st.markdown("---")

cur.close()
conn.close()
