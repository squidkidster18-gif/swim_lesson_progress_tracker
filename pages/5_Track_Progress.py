import streamlit as st
import psycopg2

st.title("Track Progress")

conn = psycopg2.connect(st.secrets["DB_URL"])
cur = conn.cursor()

# Pull students for dropdown
cur.execute("""
    SELECT id, first_name || ' ' || last_name AS full_name
    FROM students
    ORDER BY last_name, first_name;
""")
students = cur.fetchall()
student_options = {name: student_id for student_id, name in students}

# Pull skills for dropdown
cur.execute("""
    SELECT id, skill_name
    FROM skills
    ORDER BY skill_name;
""")
skills = cur.fetchall()
skill_options = {skill_name: skill_id for skill_id, skill_name in skills}

# Pull lesson sessions for dropdown
cur.execute("""
    SELECT
        ls.id,
        s.first_name || ' ' || s.last_name || ' - ' || ls.lesson_date::text AS lesson_label
    FROM lesson_sessions ls
    JOIN students s ON ls.student_id = s.id
    ORDER BY ls.lesson_date DESC, s.last_name, s.first_name;
""")
lesson_sessions = cur.fetchall()
lesson_options = {lesson_label: lesson_id for lesson_id, lesson_label in lesson_sessions}

status_options = ["Not Started", "In Progress", "Needs Improvement", "Mastered"]

if not student_options:
    st.info("Please add at least one student before tracking progress.")
elif not skill_options:
    st.info("Please add at least one skill before tracking progress.")
elif not lesson_options:
    st.info("Please add at least one lesson session before tracking progress.")
else:
    with st.form("add_progress"):
        st.subheader("Add Progress Record")

        selected_student = st.selectbox("Student *", options=list(student_options.keys()))
        selected_skill = st.selectbox("Skill *", options=list(skill_options.keys()))
        selected_lesson = st.selectbox("Lesson Session *", options=list(lesson_options.keys()))
        selected_status = st.selectbox("Status *", options=status_options)
        instructor_notes = st.text_area("Instructor Notes")

        submitted = st.form_submit_button("Add Progress Record")

        if submitted:
            errors = []

            if not selected_student:
                errors.append("Student must be selected.")
            if not selected_skill:
                errors.append("Skill must be selected.")
            if not selected_lesson:
                errors.append("Lesson session must be selected.")
            if not selected_status:
                errors.append("Status is required.")

            if errors:
                for err in errors:
                    st.error(err)
            else:
                try:
                    cur.execute("""
                        INSERT INTO student_skill_progress
                        (student_id, skill_id, lesson_session_id, status, instructor_notes)
                        VALUES (%s, %s, %s, %s, %s);
                    """, (
                        student_options[selected_student],
                        skill_options[selected_skill],
                        lesson_options[selected_lesson],
                        selected_status,
                        instructor_notes.strip()
                    ))
                    conn.commit()
                    st.success("Progress record added successfully!")
                    st.rerun()
                except Exception:
                    conn.rollback()
                    st.error("There was an error adding the progress record.")

st.subheader("Filter Progress Records")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    student_filter = st.selectbox(
        "Filter by Student",
        options=["All Students"] + list(student_options.keys()) if student_options else ["All Students"]
    )

with filter_col2:
    skill_filter = st.selectbox(
        "Filter by Skill",
        options=["All Skills"] + list(skill_options.keys()) if skill_options else ["All Skills"]
    )

with filter_col3:
    status_filter = st.selectbox(
        "Filter by Status",
        options=["All Statuses"] + status_options
    )

query = """
    SELECT
        ssp.id,
        s.first_name || ' ' || s.last_name AS student_name,
        sk.skill_name,
        ls.lesson_date,
        ssp.status,
        ssp.instructor_notes
    FROM student_skill_progress ssp
    JOIN students s ON ssp.student_id = s.id
    JOIN skills sk ON ssp.skill_id = sk.id
    JOIN lesson_sessions ls ON ssp.lesson_session_id = ls.id
    WHERE 1=1
"""

params = []

if student_filter != "All Students":
    query += " AND s.first_name || ' ' || s.last_name = %s"
    params.append(student_filter)

if skill_filter != "All Skills":
    query += " AND sk.skill_name = %s"
    params.append(skill_filter)

if status_filter != "All Statuses":
    query += " AND ssp.status = %s"
    params.append(status_filter)

query += " ORDER BY ls.lesson_date DESC, student_name;"

cur.execute(query, tuple(params))
progress_records = cur.fetchall()

st.subheader("Existing Progress Records")

if not progress_records:
    st.info("No progress records found.")
else:
    for record in progress_records:
        record_id, student_name, skill_name, lesson_date, status, instructor_notes = record

        col1, col2 = st.columns([5, 1])

        with col1:
            st.write(f"**{student_name}**")
            st.write(f"Skill: {skill_name}")
            st.write(f"Lesson Date: {lesson_date}")
            st.write(f"Status: {status}")
            st.write(f"Instructor Notes: {instructor_notes if instructor_notes else 'No notes'}")

        with col2:
            if st.button("Delete", key=f"delete_progress_{record_id}"):
                try:
                    cur.execute("DELETE FROM student_skill_progress WHERE id = %s;", (record_id,))
                    conn.commit()
                    st.success("Progress record deleted.")
                    st.rerun()
                except Exception:
                    conn.rollback()
                    st.error("Could not delete this progress record.")

        st.markdown("---")

cur.close()
conn.close()
