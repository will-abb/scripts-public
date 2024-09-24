#!/bin/bash

echo "#+title: Audit UNIX.09"

# Section 1: File Permissions
echo "Section 1: File Permissions"

# Associative array to maintain the order of file permissions checks
declare -A file_permissions_ordered=(
    ["A"]="/etc/exports:-rw-r--r--"
    ["B"]="/etc/inetd.conf:-rw-------"
    ["C"]="/etc/passwd:-rw-r--r--"
    ["D"]="/etc/services:-rw-r--r--"
    ["E"]="/etc/shadow:-r--------"
    ["F"]="/etc/securetty:-rw-------"
    ["G"]="/etc/group:-rw-r--r--"
    ["H"]="/etc/ftpusers:-rw-rw-r--"
    ["I"]="<directories where compiled application code resides>"
    ["J"]="<directories where database and other financial relevant data resides>"
)

# Function to print file permissions and check against expected
print_and_check_permissions() {
    local label="$1"
    local file="${2%:*}"
    local expected="${2#*:}"

    echo "Checking $label: $file"
    if [ -e "$file" ]; then
        local actual=$(ls -l "$file" | awk '{print $1}')
        ls -la "$file"
        if [ "$actual" == "$expected" ]; then
            echo "PASS: $file permissions are correct: $actual"
        else
            echo "FAIL: $file permissions are incorrect: Expected $expected, Found $actual"
        fi
    else
        echo "DNE: $file does not exist."
    fi
}

# Loop over the ordered list for file permission checks
for key in {A..J}; do
    print_and_check_permissions "$key" "${file_permissions_ordered[$key]}"
done

echo "Section 1B: Inspect File Permissions for Write Access"
echo "Script to check for WRITE access in critical directories needs to be implemented."

# Section 2: /etc/securetty and /etc/pam.d/login
echo "Section 2: Inspect Securetty and pam.d/login"

# /etc/securetty inspection
echo "Inspect /etc/securetty"
if [ -e "/etc/securetty" ]; then
    ls -la /etc/securetty
    if grep -q "^console$" /etc/securetty; then
        echo "PASS: /etc/securetty limits root access to CONSOLE only."
    else
        echo "FAIL: /etc/securetty does not limit root access to CONSOLE."
    fi
    echo "Contents of /etc/securetty:"
    cat /etc/securetty
else
    echo "DNE: /etc/securetty does not exist."
fi

# /etc/pam.d/login inspection
echo "Check /etc/pam.d/login for pam_securetty module"
if [ -e "/etc/pam.d/login" ]; then
    ls -la /etc/pam.d/login
    if grep -q "auth.*required.*pam_securetty.so" /etc/pam.d/login; then
        echo "PASS: pam_securetty module is configured in /etc/pam.d/login."
    else
        echo "FAIL: pam_securetty module is not configured in /etc/pam.d/login."
    fi
    echo "Contents of /etc/pam.d/login:"
    cat /etc/pam.d/login
else
    echo "ERROR: /etc/pam.d/login does not exist."
fi

# Section 3: SSH Configuration Inspection
echo "Section 3: SSH Configuration Inspection"
echo "Inspect sshd_config for PermitRootLogin"
if [ -e "/etc/ssh/sshd_config" ]; then
    ls -la /etc/ssh/sshd_config
    if grep -q "^PermitRootLogin no$" /etc/ssh/sshd_config; then
        echo "PASS: PermitRootLogin is set to 'No'."
    else
        echo "ALERT: PermitRootLogin is not set to 'No'. Further investigation needed."
    fi
    echo "Contents of /etc/ssh/sshd_config:"
    cat /etc/ssh/sshd_config
else
    echo "ERROR: /etc/ssh/sshd_config does not exist."
fi
