import os
import base64
import hvac
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

VAULT_ADDR = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
ROLE_ID = os.getenv("ROLE_ID")
SECRET_ID = os.getenv("SECRET_ID")

def conn():
    if not ROLE_ID or not SECRET_ID:
        print("Error: ROLE_ID or SECRET_ID is not set; cannot authenticate to Vault.")
        return None

    client = hvac.Client(url=VAULT_ADDR)
    try:
        client.auth.approle.login(role_id=ROLE_ID, secret_id=SECRET_ID)
        if not client.is_authenticated():
            print("Error: Vault AppRole authentication failed.")
            return None
        return client
    except Exception as e:
        print("Error:", e)
        return None

def getApiKey():
    client = conn()
    if not client:
        return None
    
    try:
        response = client.secrets.kv.v2.read_secret_version(
            mount_point='secret',
            path='weather-api',
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
            #result, #encryptResult { margin-top: 20px; padding: 20px;}
        </style>
    </head>
    <body>
        <h1>Weather forecast</h1>
        <div class="controls">
            <button onclick="getInfo()">Get Weather</button>
            <div id="result"></div>

            <input id="plaintext" type="text" placeholder="Text to encrypt" />
            <button onclick="encryptText()">Encrypt</button>
            <div id="encryptResult"></div>
        </div>

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

            async function encryptText() {
                const text = document.getElementById('plaintext').value;
                const target = document.getElementById('encryptResult');
                target.innerHTML = '';

                try {
                    const response = await fetch('/api/encrypt', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text })
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.error || 'Encryption failed');
                    }

                    target.innerHTML = data.ciphertext;
                } catch (e) {
                    target.innerHTML = 'Error: ' + e.message;
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

@app.route('/api/encrypt', methods=['POST'])
def encrypt_text():
    try:
        payload = request.get_json(silent=True) or {}
        plaintext = payload.get('text', '')

        if not plaintext:
            return jsonify({'error': 'Nothing provided to encrypt'}), 400

        client = conn()
        if not client:
            return jsonify({'error': 'Failed to auth with Vault'}), 500

        encoded = base64.b64encode(plaintext.encode('utf-8')).decode('ascii')
        response = client.secrets.transit.encrypt_data(
            name='weather-key',
            plaintext=encoded
        )

        ciphertext = response['data'].get('ciphertext')
        if not ciphertext:
            return jsonify({'error': 'No ciphertext returned from Vault'}), 500

        return jsonify({'ciphertext': ciphertext})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)