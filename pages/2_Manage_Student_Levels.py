import streamlit as st
import psycopg2

st.title("Manage Student Levels")

# Connect to database
conn = psycopg2.connect(st.secrets["DB_URL"])
cur = conn.cursor()

# Add new level
with st.form("add_level"):
    st.subheader("Add New Level")

    level_name = st.text_input("Level Name *")
    description = st.text_area("Description")

    submitted = st.form_submit_button("Add Level")

    if submitted:
        if not level_name.strip():
            st.error("Level name is required.")
        else:
            cur.execute("""
                INSERT INTO student_levels (level_name, description)
                VALUES (%s, %s);
            """, (level_name, description))

            conn.commit()
            st.success("Level added successfully!")

# Show existing levels
st.subheader("Existing Levels")

cur.execute("SELECT id, level_name, description FROM student_levels ORDER BY id;")
levels = cur.fetchall()

for lvl in levels:
    st.write(f"**{lvl[1]}** - {lvl[2] if lvl[2] else 'No description'}")

cur.close()
conn.close()
