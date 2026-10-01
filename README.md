# Secure File Sharing System
A secure file sharing web application built with Python and Streamlit. The system provides user authentication, encrypted file storage, controlled file sharing, expiring access, access revocation, and activity logging. Link : https://securefilesharing-sfwskxuhxtc6hlyszvdqdb.streamlit.app/

## Features
* User registration and login
* Password hashing using bcrypt
* Encrypted file storage using Fernet encryption
* Secure file upload and download
* User-to-user file sharing
* Configurable sharing duration
* Automatic access expiration
* File access revocation
* Activity logging
* SQLite database for users, files, sharing permissions, and logs
* Streamlit-based web interface

## Technologies Used
* Python
* Streamlit
* SQLite
* Cryptography
* Fernet Encryption
* bcrypt

## Project Structure
```text
secure_file_sharing/
│
├── app.py
├── auth.py
├── database.py
├── file_manager.py
├── requirements.txt
├── .gitignore
│
├── storage/
├── files.db
└── secret.key
```

## How It Works
### 1. Authentication

Users can create an account and log in using their email and password.

Passwords are hashed using bcrypt before being stored in the database.

### 2. File Encryption

When a user uploads a file:

```text
User Upload
     ↓
Read File
     ↓
Fernet Encryption
     ↓
Encrypted File
     ↓
Local Storage
```

The original file is not stored directly in the storage folder.

### 3. File Sharing
The owner can share a file with another registered user using their email address.

Available access options:

* No expiration
* 1 hour
* 24 hours
* 7 days

### 4. Access Control
Before a shared file can be downloaded, the application checks whether the user still has valid access.

Access can become invalid when:

* The share expires
* The owner revokes access

### 5. Activity Logging
Important user activities such as successful login and file-related actions can be recorded in the SQLite database.

## Database
The application uses SQLite with the following main tables:

* `users`
* `files`
* `shared_files`
* `activity_logs`

The database stores file metadata and access permissions rather than the actual unencrypted file contents.

## Security Considerations
The project demonstrates several practical security concepts:

* Password hashing with bcrypt
* Symmetric encryption using Fernet
* Access control
* Expiring permissions
* Access revocation
* Separation of encrypted file storage and metadata
* Activity logging

The encryption key is stored separately from the SQLite database.

For a production system, secure key management, persistent cloud storage, database security, HTTPS, stronger authorization controls, and secure deployment practices would be required.


## Future Improvements
Possible production-oriented improvements include:

* Cloud object storage
* Managed database
* Secure secret/key management
* HTTPS deployment
* Email-based sharing invitations
* Multi-factor authentication
* File integrity verification
* More granular permissions
* Improved audit logging


GitHub: Add your GitHub profile link here
LinkedIn: Add your LinkedIn profile link here
