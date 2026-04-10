import streamlit as st
import psycopg2

st.title("Manage Student Levels")

conn = psycopg2.connect(st.secrets["DB_URL"])
cur = conn.cursor()

with st.form("add_level"):
    st.subheader("Add New Level")

    level_name = st.text_input("Level Name *")
    description = st.text_area("Description")
    submitted = st.form_submit_button("Add Level")

    if submitted:
        if not level_name.strip():
            st.error("Level name is required.")
        else:
            try:
                cur.execute("""
                    INSERT INTO student_levels (level_name, description)
                    VALUES (%s, %s);
                """, (level_name.strip(), description.strip()))
                conn.commit()
                st.success("Level added successfully!")
            except Exception:
                conn.rollback()
                st.error("That level may already exist.")

st.subheader("Existing Levels")

cur.execute("""
    SELECT id, level_name, description
    FROM student_levels
    ORDER BY id;
""")
levels = cur.fetchall()

if not levels:
    st.info("No levels found yet.")
else:
    for level in levels:
        level_id, level_name, description = level

        col1, col2 = st.columns([5, 1])

        with col1:
            st.write(f"**{level_name}**")
            st.write(description if description else "No description")

        with col2:
            if st.button("Delete", key=f"delete_level_{level_id}"):
                try:
                    cur.execute("DELETE FROM student_levels WHERE id = %s;", (level_id,))
                    conn.commit()
                    st.success(f"{level_name} deleted.")
                    st.rerun()
                except Exception:
                    conn.rollback()
                    st.error("Could not delete this level. It may still be connected to other records.")

        st.markdown("---")

cur.close()
conn.close()
