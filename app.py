import sqlite3
import streamlit as st
from pydantic import BaseModel
import streamlit_pydantic as sp
from typing import Literal

# Connect to our database
con = sqlite3.connect("todoapp.sqlite", isolation_level=None)
cur = con.cursor()

# Create the table
cur.execute(
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        task TEXT,
        description TEXT,
        category TEXT,
        is_done BOOLEAN
    )
    """
)

# Define our Form
class Task(BaseModel):
    task: str
    description: str
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
            INSERT INTO tasks (task, description, category, is_done) VALUES (?, ?, ?, ?)
            """,
             (data.task, data.description, data.category, data.is_done),
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

    cols = st.columns(4)
    cols[0].write("Status")
    cols[1].write("Task")
    cols[2].write("Description")
    cols[3].write("Category")


    for row in data:
        cols = st.columns(4)


        cols[0].checkbox('is_done', row[3], label_visibility='hidden', key=row[0], on_change=toggle_is_done, args=(not row[3], row))
        cols[1].write(row[1])
        cols[2].write(row[2])
        cols[3].write(row[3])
        # cols[2].markdown(
        #     f'<a target="_self" href="/?id=123" style="display: inline-block; padding: 6px 10px; background-color: #4CAF50; color: white; text-align: center; text-decoration: none; font-size: 12px; border-radius: 4px;">Action Text on Button</a>',
        #     unsafe_allow_html=True,
        # )

main()

