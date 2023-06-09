# Todo-WebApp

This is a simple Todo List WebApp built with Python, Streamlit, and MySQL. It allows users to manage their tasks, group them, and manage their account. Administrators can also manage user accounts.

## Example

![Tasks](images/tasks.png)

## Setup

Follow these steps to set up the Todo-WebApp:

### 1. Install required Python packages

To install the required Python packages, run the following command:

```bash
    pip install -r requirements.txt
```
### 2. Set up XAMPP

Download and install XAMPP for your operating system.
Open the XAMPP Control Panel and start the Apache and MySQL services.
Open a web browser and navigate to http://localhost/phpmyadmin/ to access the phpMyAdmin interface.

### 3. Set up the database and tables
Run the following SQL queries in phpMyAdmin to set up the database and tables:
    
```sql
CREATE DATABASE todo_db;

USE todo_db;

CREATE TABLE `users` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone_number VARCHAR(8)
);

CREATE TABLE `groups` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    group_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE `tasks` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    task_name VARCHAR(255) NOT NULL,
    status TINYINT(1) DEFAULT 0,
    group_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (group_id) REFERENCES `groups`(id)
);
```
Bare in mind that the phone number is only 8 characters long because it's by default set to Danish phone numbers.

## Screenshots

![Login](images/login.png)
![Tasks Edit](images/tasks_edit.png)
![Admin View](images/admin_view.png)
![Admin Edit](images/admin_edit.png)
