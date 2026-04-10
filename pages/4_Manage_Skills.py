import streamlit as st
import psycopg2

st.title("Manage Skills")

conn = psycopg2.connect(st.secrets["DB_URL"])
cur = conn.cursor()

# Pull levels for dropdown
cur.execute("""
    SELECT id, level_name
    FROM student_levels
    ORDER BY id;
""")
levels = cur.fetchall()

level_options = {level_name: level_id for level_id, level_name in levels}

if not level_options:
    st.info("Please add at least one student level before adding skills.")
else:
    with st.form("add_skill"):
        st.subheader("Add New Skill")

        skill_name = st.text_input("Skill Name *")
        skill_category = st.text_input("Skill Category *")
        description = st.text_area("Description")
        selected_level = st.selectbox("Associated Level *", options=list(level_options.keys()))
        submitted = st.form_submit_button("Add Skill")

        if submitted:
            errors = []

            if not skill_name.strip():
                errors.append("Skill name is required.")
            if not skill_category.strip():
                errors.append("Skill category is required.")

            if errors:
                for err in errors:
                    st.error(err)
            else:
                try:
                    cur.execute("""
                        INSERT INTO skills (skill_name, skill_category, description, level_id)
                        VALUES (%s, %s, %s, %s);
                    """, (
                        skill_name.strip(),
                        skill_category.strip(),
                        description.strip(),
                        level_options[selected_level]
                    ))
                    conn.commit()
                    st.success("Skill added successfully!")
                    st.rerun()
                except Exception:
                    conn.rollback()
                    st.error("There was an error adding the skill.")

st.subheader("Existing Skills")

cur.execute("""
    SELECT
        sk.id,
        sk.skill_name,
        sk.skill_category,
        sk.description,
        sl.level_name
    FROM skills sk
    LEFT JOIN student_levels sl ON sk.level_id = sl.id
    ORDER BY sk.id;
""")
skills = cur.fetchall()

if not skills:
    st.info("No skills found yet.")
else:
    for skill in skills:
        skill_id, skill_name, skill_category, description, level_name = skill

        col1, col2 = st.columns([5, 1])

        with col1:
            st.write(f"**{skill_name}**")
            st.write(f"Category: {skill_category}")
            st.write(f"Level: {level_name if level_name else 'N/A'}")
            st.write(f"Description: {description if description else 'No description'}")

        with col2:
            if st.button("Delete", key=f"delete_skill_{skill_id}"):
                try:
                    cur.execute("DELETE FROM skills WHERE id = %s;", (skill_id,))
                    conn.commit()
                    st.success(f"{skill_name} deleted.")
                    st.rerun()
                except Exception:
                    conn.rollback()
                    st.error("Could not delete this skill. It may still be connected to other records.")

        st.markdown("---")

cur.close()
conn.close()
