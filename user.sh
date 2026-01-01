#!/bin/bash

# Usage:
# ./user.sh add username password "Full Name"
# ./user.sh del username

ACTION="$1"
USERNAME="$2"
PASSWORD="$3"
FULLNAME="$4"

if [[ "$ACTION" == "add" ]]; then
    if [[ -z "$USERNAME" || -z "$PASSWORD" || -z "$FULLNAME" ]]; then
        echo "Usage: $0 add username password \"Full Name\""
        exit 1
    fi

    echo "➡️  Creating Kerberos principal for $USERNAME..."
    sudo kadmin.local -q "addprinc -pw $PASSWORD $USERNAME@TEST.LAN"
    if [[ $? -ne 0 ]]; then
        echo "❌ Error creating Kerberos principal."
        exit 1
    fi

    echo "➡️  Creating LDAP entry for $USERNAME..."
    LDAP_ENTRY=$(cat <<EOF
dn: uid=$USERNAME,ou=users,dc=test,dc=lan
objectClass: inetOrgPerson
uid: $USERNAME
cn: $FULLNAME
sn: ${FULLNAME##* }
userPassword: $PASSWORD
EOF
)
    echo "$LDAP_ENTRY" | ldapadd -x -D cn=admin,dc=test,dc=lan -W
    if [[ $? -ne 0 ]]; then
        echo "❌ Error adding user to LDAP."
        exit 1
    fi

    echo "✅ User $USERNAME created in both Kerberos and LDAP."

elif [[ "$ACTION" == "del" ]]; then
    if [[ -z "$USERNAME" ]]; then
        echo "Usage: $0 del username"
        exit 1
    fi

    echo "➡️  Deleting Kerberos principal $USERNAME..."
    sudo kadmin.local -q "delprinc -force $USERNAME@TEST.LAN"
    if [[ $? -ne 0 ]]; then
        echo "❌ Error deleting Kerberos principal."
        exit 1
    fi

    echo "➡️  Deleting LDAP entry $USERNAME..."
    ldapdelete -x -D cn=admin,dc=test,dc=lan -W "uid=$USERNAME,ou=users,dc=test,dc=lan"
    if [[ $? -ne 0 ]]; then
        echo "❌ Error deleting LDAP entry."
        exit 1
    fi

    echo "✅ User $USERNAME deleted from both Kerberos and LDAP."

else
    echo "Usage:"
    echo "  $0 add username password \"Full Name\""
    echo "  $0 del username"
    exit 1
fi
