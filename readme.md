## Opdracht 5: Key & secrets management

### vault installatie

1. Installeer de vault: https://developer.hashicorp.com/vault/install

2. Activeer vault:
    ```bash
    ./vault server -dev -dev-root-token-id="root" 

    ./init.sh
    ```

### Voeg secret toe 
1. Login met de dev-root-token-id: http://127.0.0.1:8200
2. ga naar secrets engines
3. selecter "secrets" en dan "weather-app"
4. voeg secret api toe met de naam secret

### encryptie
Het script init.sh zet nu ook de transit engine op en maakt een encryptiesleutel (weather-key) aan. Deze sleutel wordt gebruikt door de webapplicatie om tekst te versleutelen via Vaults encryption-as-a-service api.

<<<<<<< HEAD

| Dreigingen                 | Threat                                                                       | hoe opgelost?                                                                                                                                                                                                                                                                                   |
| -------------------------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spoofing                   | Secret is stolen from plaintext files or environment variables               | Ik heb VAULT_TOKEN uitgeschakeld en het root-token verwijderd. Ik gebruik nu AppRole, wat de industriestandaard is voor machine-authenticatie.                                                                                                                                                  |
| Spoofing                   | Secret is guessed after a long time                                          | Door de secret tijdens runtime op te halen uit de KV-store maak ik gecentraliseerde rotatie mogelijk. admins kunnen de secret nu in Vault roteren zonder de code te wijzigen of opnieuw uit te rollen.                                                                                          |
| Tampering                  | Secret is changed by unauthorized people                                     | Ik heb weather-policy.hcl toegevoegd die expliciet schrijf en verwijderrechten weigert. De applicatie kan de secret nu alleen lezen, wat onbedoelde of kwaadwillige manipulatie door de app zelf voorkomt.                                                                                      |
| Repudiation                | Secret is accessed without an audit trail                                    | Ik heb expliciet vault audit enable file uitgevoerd. Elke keer dat de applicatie de secret opvraagt, wordt er een regel weggeschreven naar vault_audit.log wat zorgt voor onweerlegbaarheid.                                                                                                    |
| Denial of service          | Secret expires                                                               | De applicatie haalt het actuele, geldige secret  'on demand' op. Deze centrale controle voorkomt uitval doordat hardcoded secrets onopgemerkt verlopen in configuratiebestanden.                                                                                                                |
| Elevation of privilege     | Secret has overly broad permissions attached to it                           | Ik heb het "Root Token" achterwege gelaten. De applicatie werkt nu volgens het 'Least Privilege' principe en heeft alleen de rechten die zijn gedefinieerd in weather-policy.hcl, en niets anders.                                                                                              |
| Information disclosure     | Secret is exposed via logs on the database server                            | Omdat we nu een centraal beheerd secret gebruiken, minimaliseren we de kans dat statische wachtwoorden in logs verschijnen. Bovendien logt Vault zelf de secret niet in platte tekst.                                                                                                           |
| **Information disclosure** | **Secret is exposed via a memory dump on the fully compromised API server.** | **Dit is de enige dreiging die overblijft in Architectuur. De applicatie moet de secret ontsleutelen in het werkgeheugen om het te kunnen gebruiken. Als de server volledig gehackt is, kan de aanvaller het geheugen uitlezen. Dit kan alleen worden opgelost met Hardware Security Modules.** |
| Spoofing                   | The bootstrap secret is stolen from plaintext files or environment variables | We gebruiken geen hardcoded token meer in de code. We gebruiken AppRole. Deze worden idealiter geïnjecteerd via omgevingsvariabelen en staan niet in de broncode.                                                                                                                               |
| Spoofing                   | The bootstrap secret is guessed after a long time                            | De SECRET_ID in AppRole is cryptografisch sterk en kan door Vault automatisch worden geroteerd of 'wrapped' worden gemaakt, waardoor raden onmogelijk is.                                                                                                                                       |
| Spoofing                   | Weak or missing access control on secrets manager                            | Door de weather-policy.hcl toe te passen, hebben we strikte "Least Privilege" toegang afgedwongen. De app kan alleen lezen wat hij nodig heeft, in plaats van root-rechten te hebben.                                                                                                           |
| Tampering                  | The bootstrap secret is changed by unauthorized people                       | De policy verbiedt de applicatie om configuraties of policies aan te passen. De app kan zijn eigen ROLE_ID of rechten niet wijzigen.                                                                                                                                                            |
| Repudiation                | The bootstrap secret is accessed without an audit trail                      | Door vault audit enable file te activeren, wordt elke login-poging met de AppRole geregistreerd in de audit logs.                                                                                                                                                                               |
| Information disclosure     | Secret is retrieved using stolen bootstrap secret                            | Hoewel een gestolen SECRET_ID gebruikt kan worden, beperkt de policy de schade. Bovendien maakt de audit log detectie mogelijk en kan de SECRET_ID direct worden ingetrokken zonder de hele app opnieuw te deployen.                                                                            |
| Denial of service          | The bootstrap secret expires                                                 | AppRole auth is ontworpen voor machines. De applicatie kan programmatisch opnieuw inloggen voordat het token verloopt, waardoor uitval door verlopen certificaten/tokens wordt voorkomen.                                                                                                       |
| Denial of service          | Secret store becomes unavailable                                             | Hoewel je in je lokale script maar 1 instance draait, maakt het gebruik van Vault het mogelijk om in productie een High Availability cluster te draaien, waardoor er geen Single Point of Failure meer is.                                                                                      |
=======
| Dreigingen         | Threat                                                                   | Hoe opgelost?                                                                                                       |
| ---------------------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Spoofing               | Secret is stolen from plaintext files or environment variables               | AppRole geïmplementeerd (industriestandaard), Root-token verwijderd.                                                    |
| Spoofing               | Secret is guessed after a long time                                          | Runtime ophalen uit KV-store maakt centrale rotatie mogelijk zonder redeploy.                                           |
| Tampering              | Secret is changed by unauthorized people                                     | weather-policy.hcl dwingt Read-Only toegang af, wijzigen is geblokkeerd.                                                |
| Repudiation            | Secret is accessed without an audit trail                                    | vault audit enable file geactiveerd, alle toegang wordt gelogd voor onweerlegbaarheid.                                  |
| Denial of service      | Secret expires                                                               | On-demand ophalen voorkomt uitval door onopgemerkte, verlopen hardcoded secrets.                                        |
| Elevation of privilege | Secret has overly broad permissions attached to it                           | Least Privilege toegepast via weather-policy.hcl, applicatie heeft geen root-rechten.                                   |
| Information disclosure | Secret is exposed via logs on the database server                            | Centraal beheer voorkomt statische wachtwoorden in logs, Vault maskeert secrets in audit logs.                          |
| Information disclosure | Secret is exposed via a memory dump on the fully compromised API server.     | Restrisico: Decryptie in RAM is noodzakelijk voor gebruik. Volledige mitigatie vereist Hardware Security Modules (HSM). |
| Spoofing               | The bootstrap secret is stolen from plaintext files or environment variables | Geen hardcoded tokens, AppRole credentials geïnjecteerd via environment variables.                                      |
| Spoofing               | The bootstrap secret is guessed after a long time                            | Cryptografisch sterke SECRET_ID met optie tot automatische rotatie of response wrapping.                                |
| Spoofing               | Weak or missing access control on secrets manager                            | Strikte Least Privilege toegang afgedwongen via weather-policy.hcl.                                                     |
| Tampering              | The bootstrap secret is changed by unauthorized people                       | Policy verbiedt de applicatie om configuraties, policies of eigen rechten te wijzigen.                                  |
| Repudiation            | The bootstrap secret is accessed without an audit trail                      | vault audit enable file logt elke AppRole login-poging.                                                                 |
| Information disclosure | Secret is retrieved using stolen bootstrap secret                            | Policy beperkt impact, audit logs en directe intrekking (revocation) maken snelle respons mogelijk.                     |
| Denial of service      | The bootstrap secret expires                                                 | Programmatische re-login (AppRole) voorkomt uitval door verlopen tokens.                                                |
| Denial of service      | Secret store becomes unavailable                                             | Vault ondersteunt High Availability (HA) clusters in productie, elimineert Single Point of Failure.                     |
>>>>>>> c16f904 (added threat table)
