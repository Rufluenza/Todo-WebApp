import hashlib
import mysql.connector
from twilio.rest import Client

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="ruben_admin",
        password="for admin in range",
        database="TodoWeb"
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- User management ---
def register_user(username, password, phone_number):
    connection = connect_db()
    cursor = connection.cursor()
    hashed_password = hash_password(password)
    query = "INSERT INTO `users` (`username`, `password`, `phone_number`) VALUES (%s, %s, %s)"
    cursor.execute(query, (username, hashed_password, phone_number))
    connection.commit()
    user_id = cursor.lastrowid
    cursor.close()
    connection.close()
    return user_id

def login_user(username, password):
    connection = connect_db()
    cursor = connection.cursor()
    query = "SELECT * FROM `users` WHERE `username` = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    cursor.fetchall()
    cursor.close()
    connection.close()
    if user and user[2] == hash_password(password):
        return user
    return None

def get_user_by_id(user_id):
    connection = connect_db()
    cursor = connection.cursor()
    query = "SELECT * FROM `users` WHERE `id` = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user

def update_user(user_id, new_username, new_password, new_phone_number):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE `users`
        SET `username` = ?, `password` = ?, `phone_number` = ?
        WHERE `id` = ?
    """, (new_username, new_password, new_phone_number, user_id))
    cursor.close()
    connection.commit()
    connection.close()


# --- Task management ---
def add_task(user_id, task, group_id=None):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO `tasks` (`user_id`, `task`, `status`, `group_id`) VALUES (%s, %s, %s, %s)", (user_id, task, 0, group_id))
    connection.commit()
    connection.close()

def get_tasks(user_id, group_id):
    connection = connect_db()
    cursor = connection.cursor()
    if group_id is None:
        cursor.execute("SELECT * FROM `tasks` WHERE `user_id`=%s AND `group_id` IS NULL", (user_id,))
    else:
        cursor.execute("SELECT * FROM tasks WHERE user_id=%s AND group_id=%s", (user_id, group_id))
    tasks = cursor.fetchall()
    cursor.close()
    return tasks

def update_task_status(task_id, status):
    connection = connect_db()
    cursor = connection.cursor()
    query = "UPDATE `tasks` SET `status` = %s WHERE `id` = %s"
    cursor.execute(query, (status, task_id))
    connection.commit()
    cursor.close()
    connection.close()

def update_task_name(task_id, new_task_name):
    connection = connect_db()
    cursor = connection.cursor()
    query = "UPDATE `tasks` SET `task` = %s WHERE `id` = %s"
    cursor.execute(query, (new_task_name, task_id))
    connection.commit()


def delete_task(task_id):
    connection = connect_db()
    cursor = connection.cursor()
    query = "DELETE FROM `tasks` WHERE `id` = %s"
    cursor.execute(query, (task_id,))
    connection.commit()

# --- Group management ---
def create_group(user_id, group_name):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO `groups` (`user_id`, `group_name`) VALUES (%s, %s)", (user_id, group_name))
    connection.commit()
    new_group_id = cursor.lastrowid
    cursor.close()
    connection.close()
    return new_group_id

def update_group(group_id, new_group_name):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("UPDATE `groups` SET `group_name`=%s WHERE `id`=%s", (new_group_name, group_id))
    connection.commit()
    cursor.close()
    connection.close()

def delete_group(group_id):
    connection = connect_db()
    cursor = connection.cursor()

    # Delete all tasks within the group
    query = "DELETE FROM `tasks` WHERE `group_id` = %s"
    cursor.execute(query, (group_id,))

    # Delete the group
    query = "DELETE FROM `groups` WHERE `id` = %s"
    cursor.execute(query, (group_id,))

    connection.commit()
    cursor.close()
    connection.close()


def get_groups(user_id):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM `groups` WHERE `user_id`=%s", (user_id,))
    groups = cursor.fetchall()
    cursor.close()
    connection.close()
    return groups

def create_default_group(user_id):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO `groups` (`user_id`, `group_name`) VALUES (%s, %s)", (user_id, "Default"))
    connection.commit()
    cursor.close()
    connection.close()

# --- User management ---
def get_all_users():
    connection = connect_db()
    cursor = connection.cursor()
    query = "SELECT * FROM `users`"
    #query = "SELECT id, username, password FROM users"
    cursor.execute(query)
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    return users



def delete_user(user_id):
    connection = connect_db()
    cursor = connection.cursor()

    # Delete tasks related to the user's groups
    query_tasks_group = """
    DELETE FROM `tasks`
    WHERE `group_id` IN (
        SELECT `id` FROM `groups` WHERE `user_id` = %s
    );
    """
    cursor.execute(query_tasks_group, (user_id,))

    # Delete tasks directly related to the user
    query_tasks_user = """
    DELETE FROM `tasks`
    WHERE `user_id` = %s;
    """
    cursor.execute(query_tasks_user, (user_id,))

    # Delete groups
    query_groups = """
    DELETE FROM `groups`
    WHERE `user_id` = %s;
    """
    cursor.execute(query_groups, (user_id,))

    # Delete user
    query_user = """
    DELETE FROM `users`
    WHERE `id` = %s;
    """
    cursor.execute(query_user, (user_id,))

    # Commit the transaction
    connection.commit()
    cursor.close()
    connection.close()



def delete_all_tasks_of_user(user_id):
    connection = connect_db()
    cursor = connection.cursor()
    query = "DELETE FROM `tasks` WHERE `user_id` = %s"
    cursor.execute(query, (user_id,))
    connection.commit()

def delete_all_tasks_of_group(group_id):
    connection = connect_db()
    cursor = connection.cursor()
    query = "DELETE FROM `tasks` WHERE `group_id` = %s"
    cursor.execute(query, (group_id,))
    connection.commit()

def delete_all_groups_of_user(user_id):
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM `groups` WHERE `user_id` = %s", (user_id,))
    groups = cursor.fetchall()

    for group in groups:
        group_id = group[0]
        delete_all_tasks_of_group(group_id)

    query = "DELETE FROM `groups` WHERE `user_id` = %s AND `group_name` != 'Default'"
    cursor.execute(query, (user_id,))
    connection.commit()
    cursor.close()


# --- Notification management ---
def send_sms(message, phone_number):
    # Send an sms to a phone number
    account_sid = "AC7961821818ff83df1fe55450c268e044"
    auth_token = "abca6272e34949358064ae32c33cff12"
    client = Client(account_sid, auth_token)
    message = client.messages.create(
    body=str(message),
    from_="+16076056475",
    to="+45"+str(phone_number)
    )



def send_sms_on_delete(user_id):
    # send a sms if a user is deleted
    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM `users` WHERE `id` = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()
