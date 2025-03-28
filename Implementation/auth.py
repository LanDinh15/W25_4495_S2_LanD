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
            "movie_checklist": {}
        }}, f)

def load_credentials():
    with open(CREDENTIALS_FILE, "r") as f:
        creds = json.load(f)
    for username in creds:
        if "dob" not in creds[username]:
            creds[username]["dob"] = None
        if "movie_checklist" not in creds[username]:
            creds[username]["movie_checklist"] = {}
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
        "movie_checklist": {}
    }
    save_credentials(creds)
    return True

def update_user_profile(username, full_name=None, dob=None, email=None, password=None, avatar_path=None, movie_checklist=None):
    creds = load_credentials()
    if username not in creds:
        return False
    if full_name:
        creds[username]["full_name"] = full_name
    if dob is not None:
        creds[username]["dob"] = dob
    if email:
        creds[username]["email"] = email
    if password:
        creds[username]["password"] = password
    if avatar_path:
        creds[username]["avatar_path"] = avatar_path
    if movie_checklist is not None:
        creds[username]["movie_checklist"] = movie_checklist
    save_credentials(creds)
    
    return True