from fastapi import FastAPI, HTTPException
import ldap
import subprocess
from pydantic import BaseModel

app = FastAPI()

# LDAP config
LDAP_SERVER = "ldap://127.0.0.1"
BASE_DN = "dc=domain,dc=tld" # add your domain and tld
ADMIN_DN = "cn=admin,dc=test,dc=lan"
ADMIN_PASSWORD = "ldap-admin-password"  # change to your admin password

# Request model
class LoginRequest(BaseModel):
    username: str
    password: str
    agent_id: str = None

# Check user exists in LDAP
def ldap_user_exists(username: str) -> bool:
    conn = ldap.initialize(LDAP_SERVER)
    conn.simple_bind_s(ADMIN_DN, ADMIN_PASSWORD)
    result = conn.search_s(BASE_DN, ldap.SCOPE_SUBTREE, f"(uid={username})")
    conn.unbind_s()
    return len(result) > 0

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
    if not ldap_user_exists(request.username):
        raise HTTPException(status_code=404, detail="User not found")
    if not kerberos_auth(request.username, request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"status": "ok"}
