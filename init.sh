#!/bin/bash
set -e

export VAULT_ADDR="http://127.0.0.1:8200"
export VAULT_TOKEN="${VAULT_TOKEN:-root}"
POLICY_FILE="weather-policy.hcl"

echo "Enabling file audit device..."
./vault audit enable file file_path=./vault_audit.log 2>/dev/null || echo "Audit already enabled"

echo "Enabling AppRole auth method..."
./vault auth enable approle 2>/dev/null || echo "AppRole already enabled"

echo "Enabling transit engine..."
./vault secrets enable -path=transit transit 2>/dev/null || echo "Transit already enabled"

echo "Creating (or ensuring) transit key..."
./vault write -f transit/keys/weather-key 2>/dev/null || echo "Transit key already exists"

echo "Applying policy from ${POLICY_FILE}..."
./vault policy write weather-policy "${POLICY_FILE}"

echo "Applying transit encrypt-only policy..."
./vault policy write weather-transit-policy - <<EOF
path "transit/encrypt/weather-key" {
  capabilities = ["update"]
}
EOF

echo "Creating AppRole..."
./vault write auth/approle/role/weather-role \
  token_policies="weather-policy,weather-transit-policy" \
  bind_secret_id=true \
  secret_id_ttl=24h \
  token_ttl=1h \
  token_max_ttl=4h
  
ROLE_ID=$(./vault read -field=role_id auth/approle/role/weather-role/role-id)
export ROLE_ID

SECRET_ID=$(./vault write -field=secret_id -f auth/approle/role/weather-role/secret-id)
export SECRET_ID

unset VAULT_TOKEN

python main.py
