
# Multithreaded Chat Application Setup Guide

## 📦 Installation

### Step 1: Get the Code

Clone the repository and navigate into the project directory:

```bash
git clone https://github.com/3bdul1ah/multithreaded_chat_app.git
cd multithreaded_chat_app
```

### Step 2: Create a Virtual Environment

Create a virtual environment to manage dependencies:

```bash
python3 -m venv venv
```

Activate the virtual environment:

- For Windows:

```bash
venv\Scripts\activate
```

- For Mac/Linux:

```bash
source venv/bin/activate
```

### Step 3: Install Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

---

## 🖥 Running the Chat Application

### Step 1: Configure the Database

Before starting the application, ensure that the MySQL database is set up properly.

1. **Login to MySQL**:

```bash
sudo mysql -u root -p
```

2. **Create the Database and Tables**:

Run the following SQL commands in the MySQL terminal:

```sql
CREATE DATABASE IF NOT EXISTS chat_db;
USE chat_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(256) NOT NULL
);

CREATE TABLE rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    content TEXT NOT NULL,
    room_id INT,
    receiver_id INT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (room_id) REFERENCES rooms(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id)
);
```

### Step 2: Update `db_config` in Python

In the project, update the `db_config` dictionary located in `server.py` to match your MySQL setup. Specifically, change the password to your MySQL root password:

```python
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'azaz',  # Change this to your MySQL root password
    'database': 'chat_db'
}
```

This `'azaz'` is the password used in our case, so replace it with your actual MySQL root password in the above configuration.

### Step 3: Start the Server

Run the server in one terminal:

```bash
python3 server.py
```

### Step 4: Start the Client

Run the client in a separate terminal:

```bash
python3 client.py
```

---

## Features

- Real-time messaging
- Group chat functionality
- Direct messaging
- Multithreading support

---

## Notes

- Make sure MySQL is running and you have created the `chat_db` database before starting the server.
- Ensure that the database credentials in the `db_config` are correct and match your MySQL setup.