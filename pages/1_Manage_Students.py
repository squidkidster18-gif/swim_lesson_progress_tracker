import streamlit as st
import psycopg2

st.title("Manage Students")

# Connect to database
conn = psycopg2.connect(st.secrets["DB_URL"])
cur = conn.cursor()

# Get levels for dropdown
cur.execute("SELECT id, level_name FROM student_levels ORDER BY level_name;")
levels = cur.fetchall()

level_options = {level[1]: level[0] for level in levels}

# Form to add student
with st.form("add_student"):
    st.subheader("Add New Student")

    first_name = st.text_input("First Name *")
    last_name = st.text_input("Last Name *")
    age = st.number_input("Age *", min_value=1, step=1)
    parent_name = st.text_input("Parent Name *")
    parent_email = st.text_input("Parent Email *")

    selected_level = st.selectbox("Student Level", options=level_options.keys())
    level_id = level_options[selected_level]

    notes = st.text_area("Notes")

    submitted = st.form_submit_button("Add Student")

    if submitted:
        errors = []

        if not first_name.strip():
            errors.append("First name is required.")
        if not last_name.strip():
            errors.append("Last name is required.")
        if not parent_name.strip():
            errors.append("Parent name is required.")
        if not parent_email.strip():
            errors.append("Parent email is required.")

        if errors:
            for err in errors:
                st.error(err)
        else:
            cur.execute("""
                INSERT INTO students 
                (first_name, last_name, age, parent_name, parent_email, student_level_id, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (first_name, last_name, age, parent_name, parent_email, level_id, notes))

            conn.commit()
            st.success("Student added successfully!")

cur.close()
conn.close()
