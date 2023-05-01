import streamlit as st
import pandas as pd
from backend import (
    register_user, login_user, add_task, get_tasks, update_task_status, delete_task, update_task_name, get_user_by_id,
    create_group, update_group, delete_group, get_groups, create_default_group, 
    get_all_users, delete_user, send_sms, update_user
)

st.set_page_config(
    page_title="Todo List App",
    #page_icon="💼",
)

send_text = False

def main():
    if st.button("Refresh (Debug)"):
        st.experimental_rerun()

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None

    if not st.session_state.logged_in:
        st.title("Todo List App \n Made by Ruben, Esther, Hannah & Theo")
        menu = ["Log in", "Sign Up"]
        #st.subheader("Welcome to the Todo List App!")
        st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        choice = st.radio("Log in or Sign Up ", menu)

        if choice == "Log in":
            st.subheader("Log in to your account")

            if 'password_entered' not in st.session_state:
                st.session_state.password_entered = False

            username = st.text_input("Username")
            password = st.text_input("Password", type="password", on_change=lambda: setattr(st.session_state, 'password_entered', True))

            if st.button("Log in") or st.session_state.password_entered:
                user = login_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    user_tasks(st.session_state.user)
                    st.session_state.password_entered = False
                    st.experimental_rerun()
                else:
                    st.warning("Incorrect username or password")
                    st.session_state.password_entered = False

        elif choice == "Sign Up":
            st.subheader("Create a new account")
            
            if 'new_password_entered' not in st.session_state:
                st.session_state.new_password_entered = False

            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password", on_change=lambda: setattr(st.session_state, 'new_password_entered', True))
            new_phone_number = st.text_input("Phone Number")

            if st.button("Sign Up") or st.session_state.new_password_entered:
                if new_phone_number:
                    new_user_id = register_user(new_username, new_password, new_phone_number)
                    create_default_group(new_user_id)
                    st.success("Account created successfully!")
                    st.info("Go to Login")
                #else:
                    #st.warning("Please enter a phone number")
    else:
        if st.session_state.user[1] == "admin":
            admin_panel()
        else:
            user_tasks(st.session_state.user)
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.experimental_rerun()

def user_groups(user):
    if 'group_interacted' not in st.session_state:
        st.session_state.group_interacted = False

    groups = get_groups(user[0])

    st.subheader("Welcome " + user[1] + "!")

    # Group management
    st.sidebar.subheader("Group Management")
    group_names = [group[2] for group in groups]
    group_ids = [group[0] for group in groups]

    group_mapping = dict(zip(group_names, group_ids))
    selected_group_name = st.sidebar.selectbox("Select group", group_names)

    if selected_group_name == "Default":
        selected_group_id = None
    else:
        selected_group_id = group_mapping[selected_group_name]
    
    if st.sidebar.button("Create Group"):
        new_group_name = st.sidebar.text_input("Add a new group", key="group_input", on_change=lambda: setattr(st.session_state, 'group_interacted', True))
        if st.session_state.group_interacted:
            if new_group_name.strip() == '':
                st.sidebar.warning("Group name cannot be empty.")
            elif new_group_name in group_names:
                st.sidebar.warning("Group name already exists.")
            else:
                create_group(user[0], new_group_name)
                st.session_state.group_interacted = False
                st.experimental_rerun()

    if st.sidebar.button("Rename Group"):
        new_group_name = st.sidebar.text_input("Enter new group name", key="group_input")
        if new_group_name.strip() == '':
            st.sidebar.warning("Group name cannot be empty.")
        elif new_group_name in group_names:
            st.sidebar.warning("Group name already exists.")
        else:
            update_group(selected_group_id, new_group_name)
            st.experimental_rerun()

    if st.sidebar.button("Delete Group"):
        if selected_group_name == "Default":
            st.sidebar.warning("Cannot delete default group")
        elif selected_group_id is not None:
            delete_group(selected_group_id)
            st.experimental_rerun()
        else:
            st.sidebar.warning("Invalid group selected")

    return selected_group_name, selected_group_id


def user_tasks(user):
    if 'task_added' not in st.session_state:
        st.session_state.task_added = False
    selected_group_name, selected_group_id = user_groups(user)

    st.subheader("Your tasks in: " + selected_group_name)

    user_task = st.text_input("Enter a new task", key="task_input", on_change=lambda: setattr(st.session_state, 'task_entered', True))
    if 'task_entered' not in st.session_state:
        st.session_state.task_entered = False

    if st.button("Add Task", key="add_task") or (st.session_state.task_entered and not st.session_state.task_added):
        if user_task.strip() == '':
            st.warning("Task name cannot be empty.")
        else:
            add_task(user[0], user_task, selected_group_id)
            st.session_state.task_added = False
            st.session_state.task_entered = False
            st.experimental_rerun()

    tasks = get_tasks(user[0], selected_group_id)

    # Display tasks in a table-like format
    for task in tasks:
        with st.expander(task[2], expanded=False):
            #st.markdown(f'<div class="task-box">', unsafe_allow_html=True)
            task_col1, task_col2, task_col3, task_col4 = st.columns(4)

            with task_col1:
                if f'change_name_{task[0]}' in st.session_state and st.session_state[f'change_name_{task[0]}']:
                    new_task_name = st.text_input("New task name", value=task[2], key=f'new_name_{task[0]}')
                    if st.button("Save", key=f'save_{task[0]}'):
                        update_task_name(task[0], new_task_name)
                        st.experimental_rerun()
                else:
                    st.write("")

            with task_col2:
                st.write("Status: Completed" if task[3] == 1 else "Status: Not Completed")
                button_status = task[3] == 1

                if button_status == False:
                    button_task = "Set Complete"
                else:
                    button_task = "Set Not Complete"
                if st.button(button_task, key=f'status_{task[0]}'):
                    update_task_status(task[0], not button_status)
                    st.experimental_rerun()

            with task_col3:
                if st.button("Change Name", key=f'change_{task[0]}'):
                    st.session_state[f'change_name_{task[0]}'] = not st.session_state.get(f'change_name_{task[0]}', False)
                    st.experimental_rerun()

            with task_col4:
                if st.button("Delete", key=f'delete_{task[0]}'):
                    delete_task(task[0])
                    st.experimental_rerun()


def admin_panel():
    st.title("Admin Panel")

    # User management
    st.subheader("User Management")

    users = get_all_users()

    # Display users in a table
    st.write(len(users), " users found")

    for user in users:
        user_id, username, _, phone_number = user
        edit_col, delete_col, user_col = st.columns([1, 1, 8])

        with edit_col:
            if st.button("Edit", key=f'edit_{user_id}'):
                edit_user(user_id)

        with delete_col:
            if st.button("Delete", key=f'delete_{user_id}'):
                delete_user(user_id)
                st.experimental_rerun()

        with user_col:
            st.write(f"ID: {user_id}, Username: {username}, Phone Number: {phone_number}")

# Edit user function
def edit_user(user_id):
    user = get_user_by_id(user_id)
    if user:
        new_username = st.text_input("Username", value=user[1], key=f'username_{user_id}')
        new_password = st.text_input("Password", value=user[2], key=f'password_{user_id}')
        new_phone_number = st.text_input("Phone Number", value=user[3], key=f'phone_{user_id}')

        if st.button("Save", key=f'save_{user_id}'):
            # Save updated user details
            update_user(user_id, new_username, new_password, new_phone_number)
            st.experimental_rerun()
    else:
        st.warning("User not found")


if __name__ == "__main__":
    main()
    # remove the Made with Streamlit footer
    st.markdown("""<style> #MainMenu {visibility: hidden;} footer {visibility: hidden;} </style>""", unsafe_allow_html=True)