## Opdracht 5: Key & secrets management

### vault installatie
https://developer.hashicorp.com/vault/install

Activeer vault:
```bash
./vault.exe server -dev -dev-root-token-id="root" 

./init.sh
```

### Voeg secret toe 
1. Login met de dev-root-token-id: http://127.0.0.1:8200
2. ga naar secrets engines
3. selecter "secrets" en dan "weather-app"
4. voeg secret toe