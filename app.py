import sqlite3

import streamlit as st
from pydantic import BaseModel
import streamlit_pydantic as sp
from typing import Literal

con = sqlite3.connect("todoapp.sqlite", isolation_level=None)
cur = con.cursor()
# drop table 
# con.execute("DROP TABLE tasks") 


# Create the table
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        task TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by TEXT DEFAULT "XR",
        category TEXT,
        is_done BOOLEAN DEFAULT FALSE
    )
    """
)


# Define our Form
class Task(BaseModel):
    task: str
    description: str
    created_by: str = "XIRAN LIN"
    category: Literal ['school', 'work', 'personal']
    is_done: bool



# This function will be called when the check mark is toggled, this is called a callback function
def toggle_is_done(is_done, row):
    cur.execute(
        """
        UPDATE tasks SET is_done = ? WHERE id = ?
        """,
        (is_done, row[0]),
    )

# This function will be called when the delete button is clicked
def delete_task(row):
    cur.execute(
        """
        DELETE FROM tasks WHERE id = ?
        """,
        (row[0],),
    )

def main():

    st.title("Todo App")

    # Create a Form using the streamlit-pydantic package, just pass it the Task Class
    data = sp.pydantic_form(key="task_form", model=Task)


    if data:
        cur.execute(
            """
            INSERT INTO tasks (task, description, created_by, category, is_done) 
            VALUES (?, ?, ?, ?, ?)
            """,
            (data.task, data.description, data.created_by, data.category, data.is_done),
        )

    data = cur.execute(
        """
        SELECT * FROM tasks
        """
    ).fetchall()

    # HINT: how to implement a Edit button?
    # if st.query_params.get('id') == "123":
    #     st.write("Hello 123")
    #     st.markdown(
    #         f'<a target="_self" href="/" style="display: inline-block; padding: 6px 10px; background-color: #4CAF50; color: white; text-align: center; text-decoration: none; font-size: 12px; border-radius: 4px;">Back</a>',
    #         unsafe_allow_html=True,
    #     )
    #     return

    cols = st.columns(8)
    # cols[0].write("Done?")
    cols[0].write("Status")
    cols[1].write("Task")
    cols[2].write("Description")
    cols[3].write("Created At")
    cols[4].write("Created By")
    cols[5].write("Category")

    for row in data:
        cols = st.columns(8)

        # Checkbox for marking task as done
        cols[0].checkbox('is_done', row[6], label_visibility='hidden', key=row[0], on_change=toggle_is_done, args=(not row[6], row))

        # Task details
        cols[1].write(row[1])
        cols[2].write(row[2])
        cols[3].write(row[3])
        cols[4].write(row[4])
        cols[5].write(row[5])

        # Edit button
        edit_key = f"edit-{row[0]}"
        if cols[6].button("Edit", key=edit_key):
            # Set the edit mode or redirect to another page for editing
            st.session_state.edit_mode = not st.session_state.get('edit_mode', False)
            st.session_state.edit_id = row[0]

        # Delete button
        delete_key = f"delete-{row[0]}"  # Use row ID as a suffix for the key
        if cols[7].button("Delete", key=delete_key, on_click=delete_task, args=(row,)):
            # Handle delete logic if the button is clicked
            pass

        # Check if edit mode is active for the current row
        if hasattr(st.session_state, 'edit_mode') and st.session_state.edit_mode and st.session_state.edit_id == row[0]:
            # Display the form for editing with default values from the original data
            edited_data = {}
            
            # Task details
            edited_data['task'] = st.text_input("Task", value=row[1])
            edited_data['description'] = st.text_input("Description", value=row[2])
            edited_data['created_by'] = st.text_input("Created By", value=row[4])
            edited_data['category'] = st.selectbox("Category", options=['school', 'work', 'personal'], index=['school', 'work', 'personal'].index(row[5]))

            

            # Update the task details in the database if data is provided
            if st.button("Update"):
                cur.execute(
                    """
                    UPDATE tasks 
                    SET task=?, description=?, created_by=?, category=?
                    WHERE id=?
                    """,
                    (edited_data['task'], edited_data['description'], edited_data['created_by'], edited_data['category'], row[0]),
                )
                # Reset edit mode
                st.session_state.edit_mode = False
                st.session_state.edit_id = None

main()

