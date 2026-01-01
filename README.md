# Latch Backend Setup

This repository contains the backend for your agent system, providing authentication via LDAP and Kerberos.

>⚠️ Important: Use a VM or safe environment when testing. Misconfiguring Kerberos or LDAP on a production machine can break logins.

## 1️⃣ Install System Dependencies

- First, install the necessary system packages on Ubuntu Server:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y slapd ldap-utils krb5-kdc krb5-admin-server python3-pip python3-venv git
```

During installation, you may be prompted for initial configuration (Kerberos realm, LDAP domain). Make note of these values.

## 2️⃣ Configure Kerberos

Set your Kerberos realm (usually uppercase, e.g., TEST.LAN)

Start Kerberos realm setup:
```
sudo krb5_newrealm
```

Create an admin principal to manage users:
```
sudo kadmin.local
addprinc admin
```

Test obtaining a ticket:
```
kinit admin
klist
```

You should see a valid ticket listed.

## 3️⃣ Configure LDAP

Reconfigure slapd to match your domain:
```
sudo dpkg-reconfigure slapd
```

Set the domain name (e.g., test.lan)

Set the organization name (e.g., test)

Create an admin password for LDAP

Test LDAP connectivity:
```
ldapsearch -x -LLL -H ldap://localhost -b "dc=test,dc=lan"
```
4️⃣ Clone the Backend
git clone https://github.com/YOUR_GITHUB/fastapi-backend.git
cd fastapi-backend

5️⃣ Set Up Python Environment
python3 -m venv ~/fastapi_env
source ~/fastapi_env/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn python-ldap

6️⃣ Configure Backend

Edit the python file file:
```
nano main.py
```

Key settings:

LDAP_ADMIN_DN – LDAP admin DN you created during slapd setup

KERBEROS_REALM – Kerberos realm you set during krb5_newrealm

LDAP_BASE_DN – LDAP domain components, e.g., dc=test,dc=lan

## 7️⃣ Test Backend

Run FastAPI:

uvicorn main:app --host 0.0.0.0 --port 8000


Test with curl (replace values with your test user):
```
curl -X POST http://127.0.0.1:8000/auth/login \
-H "Content-Type: application/json" \
-d '{"username":"testuser","password":"password123","agent_id":"DESKTOP-1"}'
```

You should get a response like:
```
{
  "status": "ok"
}
```
## 8️⃣ User Management

Use user.sh to add or delete users:

Add a user:
```
./user.sh add username password "Full Name"
```

Delete a user:
```
./user.sh del username

```
Make sure the user exists in both LDAP and Kerberos if needed.

## 9️⃣ Notes

The backend can now be tested manually via curl or Postman.

Once confirmed working, the agent (being worked on) can be connected to this backend.

Always use a VM or test environment when configuring Kerberos/LDAP for the first time.
