# Multithreaded Chat Application Setup Guide

## 📑 Table of Contents
1. [Installation](#-installation)
    - [Step 1: Get the Code](#step-1-get-the-code)
    - [Step 2: Create a Virtual Environment](#step-2-create-a-virtual-environment)
    - [Step 3: Install Dependencies](#step-3-install-dependencies)
    - [Step 4: Install MySQL and Create the Database](#step-4-install-mysql-and-create-the-database)

2. [Running the Chat Application](#-running-the-chat-application)
    - [Step 1: Update `db_config` in Python](#step-1-update-db_config-in-python)
    - [Step 2: Start the Server](#step-2-start-the-server)
    - [Step 3: Start the Client](#step-3-start-the-client)
3. [Usage Guide](#-usage-guide)
    - [Account Management](#account-management)
    - [Chat Room Interaction](#chat-room-interaction)
    - [Direct Messaging](#direct-messaging)
    - [Help and Navigation](#help-and-navigation)

---

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

### Step 4: Install MySQL and Create the Database

To install and access MySQL on Ubuntu 20.04, follow these steps:

1. **Install MySQL**:

```bash
sudo apt install mysql-client-core-8.0
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl status mysql
```

2. **Login to MySQL**:

```bash
sudo mysql -u root -p
```

3. **Create the Database and Tables**:

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

---

## 🖥 Running the Chat Application

### Step 1: Update `db_config` in Python

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

### Step 2: Start the Server

Run the server in one terminal:

```bash
python3 server.py
```

### Step 3: Start the Client

Run the client in a separate terminal:

```bash
python3 client.py
```

---

## 🌟 Usage Guide

Once the server and client are operational, you can start interacting with the system using the following commands:

#### **Account Management:**

- **Register a New Account**:  
  To create a new account, use the command:  
  `/register <username> <password>`  
  Example: `/register abdullah 123`

- **Log In**:  
  To log in to your account, use the command:  
  `/login <username> <password>`  
  Example: `/login ahmed 123`

#### **Chat Room Interaction:**

- **Join or Create a Room**:  
  To join or create a new chat room, use the command:  
  `/join <room_name>`  
  Example: `/join tech_chat`  
  You can chat freely with users in the same room.

#### **Direct Messaging:**

- **Send a Private Message**:  
  To start a private conversation with a user, use:  
  `/dm <username>`  
  Example: `/dm abdullah`  
  This allows for private messaging between users.

### **Help and Navigation:**

- **View Help**:  
  To get a list of available commands, use:  
  `/help`

- **Return to Main Menu**:  
  To return to the main menu, use:  
  `/back`

- **Logout**:  
  To log out from the chat, use:  
  `/exit`

---
