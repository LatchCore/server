from fastapi import FastAPI, HTTPException
import ldap
import subprocess
from pydantic import BaseModel

app = FastAPI()

# LDAP config
LDAP_SERVER = "ldap://127.0.0.1"
BASE_DN = "dc=test,dc=lan"
ADMIN_DN = "cn=admin,dc=test,dc=lan"
ADMIN_PASSWORD = "HiHi123H"  # change to your admin password

# Request model
class LoginRequest(BaseModel):
    username: str
    password: str
    agent_id: str = None

# Check user exists and return full name
def ldap_get_user_fullname(username: str) -> str:
    conn = ldap.initialize(LDAP_SERVER)
    conn.simple_bind_s(ADMIN_DN, ADMIN_PASSWORD)
    
    # Search for user
    result = conn.search_s(BASE_DN, ldap.SCOPE_SUBTREE, f"(uid={username})", ['cn'])
    conn.unbind_s()
    
    if len(result) == 0:
        return None
    # result[0][1] contains the attributes dictionary, 'cn' is a list
    full_name = result[0][1].get('cn', [b""])[0].decode("utf-8")
    return full_name

# Authenticate with Kerberos
def kerberos_auth(username: str, password: str) -> bool:
    result = subprocess.run(
        ["kinit", f"{username}@TEST.LAN"],
        input=f"{password}\n",
        text=True,
        capture_output=True
    )
    return result.returncode == 0

# Login endpoint
@app.post("/auth/login")
def login(request: LoginRequest):
    full_name = ldap_get_user_fullname(request.username)
    if not full_name:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not kerberos_auth(request.username, request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "status": "ok",
        "full_name": full_name,
        "agent_id": request.agent_id
    }
