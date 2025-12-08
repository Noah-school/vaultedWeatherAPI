import os
import hvac

VAULT_ADDR = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
ROLE_ID = os.getenv("ROLE_ID")
SECRET_ID = os.getenv("SECRET_ID")

def conn():
    client = hvac.Client(url=VAULT_ADDR)
    try:
        client.auth.approle.login(role_id=ROLE_ID, secret_id=SECRET_ID)
        return client
    except Exception as e:
        print("Error:", e)
        return False

def getApiKey():
    client = conn()
    if not client:
        return None
    
    try:
        response = client.secrets.kv.v2.read_secret_version(
            mount_point='secret',
            path='weather-app',
            raise_on_deleted_version=True
        )
        return response['data']['data']['secret'] 
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print(getApiKey())