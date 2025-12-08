import os
import hvac
from flask import Flask, jsonify
import requests

app = Flask(__name__)

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

@app.route('/')
def index():
    html = '''
    <html>
    <head>
        <style>
            body { display:grid; place-items:center}
            button { padding: 10px;}
            #result { margin-top: 20px; padding: 20px;}
        </style>
    </head>
    <body>
        <h1>Weather forecast</h1>
        <button onclick="getInfo()">Get Weather</button>
        <div id="result"></div>

        <script>
            async function getInfo() {
                try {
                    const response = await fetch('/api/get-information');
                    const data = await response.json();
                    document.getElementById('result').innerHTML = JSON.stringify(data, null, 2);
                } catch (e) {
                    document.getElementById('result').innerHTML = 'Error: ' + e;
                }
            }
        </script>
    </body>
    </html>
    '''
    return html

@app.route('/api/get-information')
def get_information():
    try:
        api_key = getApiKey()
        if not api_key:
            return jsonify({'error': 'Failed to retrieve API key from Vault'}), 500
        
        url = f'https://api.openweathermap.org/data/2.5/weather?q=Antwerp&appid={api_key}&units=metric'
        response = requests.get(url)
        data = response.json()
        
        return jsonify({
            'city': data.get('name'),
            'temp': data.get('main', {}).get('temp'),
            'weather': data.get('weather', [{}])[0].get('main')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)