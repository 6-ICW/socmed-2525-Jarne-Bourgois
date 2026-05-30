Opstarten discord clone

Backend server

open terminal
cd backend
python -m venv venv
venv\Scripts\activate
python -m daphne -b 0.0.0.0 -p 8000 discord_backend.asgi:application
```
IP configureren

zoek eerst je Ip4V-adres
dit kan door in een terminal "ipconfig" te doen en zoeken naar Ip4V
Klik in de explorer links
ga naar : frontend/src/utils/api.js

verander volgende code.

oude code : 
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
const WS_BASE = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

nieuwe code : 
const API_BASE = 'http://jouw-ip:8000/api';   bv 'http://192.168.0.154:8000/api';
const WS_BASE =  'ws://jouw-ip:8000';         bv ws://192.168.0.154:8000';

niet vergeten het bestand op te slaan : ctrl+s

Wanneer de code is aangepast : 
Nieuwe terminal aanmaken

cd frontend

Typ in de terminal
npm install
npm start


