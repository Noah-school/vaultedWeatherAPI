import os
import hvac

VAULT_ADDR = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
ROLE_ID = os.getenv("ROLE_ID")
SECRET_ID = os.getenv("SECRET_ID")


def conn():
    client = hvac.Client(url=VAULT_ADDR)
    try:
        client.auth.approle.login(role_id=ROLE_ID, secret_id=SECRET_ID)
        print("Success")
        return True
    except Exception as e:
        print("Error:", e)
        return False


if __name__ == "__main__":
    conn()
