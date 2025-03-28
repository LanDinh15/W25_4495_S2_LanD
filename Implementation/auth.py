import json
import os

CREDENTIALS_FILE = "users.json"

if not os.path.exists(CREDENTIALS_FILE):
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump({"admin": {
            "password": "123",
            "full_name": "Admin User",
            "dob": None,
            "email": "admin@example.com",
            "avatar_path": None,
            "movie_checklist": {},
            "notifications": []
        }}, f)

def load_credentials():
    with open(CREDENTIALS_FILE, "r") as f:
        creds = json.load(f)
    for username in creds:
        if "dob" not in creds[username]:
            creds[username]["dob"] = None
        if "movie_checklist" not in creds[username]:  
            creds[username]["movie_checklist"] = {}
        if "notifications" not in creds[username]:
            creds[username]["notifications"] = []
    return creds

def save_credentials(creds):
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(creds, f)

def check_login(username, password):
    creds = load_credentials()
    return username in creds and creds[username]["password"] == password

def register_user(username, password, full_name, email):
    creds = load_credentials()
    if username in creds:
        return False
    creds[username] = {
        "password": password,
        "full_name": full_name,
        "dob": None,
        "email": email,
        "avatar_path": None,
        "movie_checklist": {},
        "notifications": []
    }
    save_credentials(creds)
    return True

def update_user_profile(username, full_name=None, dob=None, email=None, password=None, avatar_path=None, movie_checklist=None, notifications=None):
    creds = load_credentials()
    if username not in creds:
        return False
    if full_name is not None:  
        creds[username]["full_name"] = full_name
    if dob is not None:
        creds[username]["dob"] = dob
    if email is not None:
        creds[username]["email"] = email
    if password is not None:
        creds[username]["password"] = password
    if avatar_path is not None:
        creds[username]["avatar_path"] = avatar_path
    if movie_checklist is not None:
        creds[username]["movie_checklist"] = movie_checklist
    if notifications is not None:
        creds[username]["notifications"] = notifications
    save_credentials(creds)
    return True