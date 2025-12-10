#!/bin/bash
set -e

export VAULT_ADDR="http://127.0.0.1:8200"
export VAULT_TOKEN="root"

echo "Enabling AppRole auth method..."
./vault auth enable approle 2>/dev/null || echo "AppRole already enabled"

echo "Creating read policy..."
./vault policy write weather-read-policy - <<EOF
path "secret/data/weather-app" {
  capabilities = ["read"]
}
EOF

echo "Creating AppRole..."
./vault write auth/approle/role/my-role \
  token_policies="default,weather-read-policy" \
  bind_secret_id=true \
  secret_id_ttl=0 \
  token_ttl=1h \
  token_max_ttl=4h
  
ROLE_ID=$(./vault read -field=role_id auth/approle/role/my-role/role-id)
export ROLE_ID

SECRET_ID=$(./vault write -field=secret_id -f auth/approle/role/my-role/secret-id)
export SECRET_ID

python main.py
