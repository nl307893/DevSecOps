# DevSecOps
## System zgłoszeń serwisowych
### Członkowie zespołu:
- Michał Barcik
- Adam Grelewicz
- Norbert Luchowski
#### Tablica Trello:
- https://trello.com/b/r7wdp3wR
### Wybrana technologia:
- Backend: Python Flask
- Fronted: JavaScript React
### Struktura projektu:
- `app/` - kod aplikacji Flask
- `app/api/` - endpointy API
- `tests/` - testy aplikacji
- `.env` - lokalna konfiguracja i dane poufne (plik ignorowany przez Git)
- `requirements.txt` - przypięte wersje zależności Pythona

### Uruchomienie backendu:
```bash
python -m venv .venv
```

Windows:
```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask run
```

Backend będzie dostępny pod adresem `http://127.0.0.1:5000`.

### Baza danych
Backend automatycznie tworzy bazę SQLite w `instance/app.sqlite3` przy uruchomieniu
aplikacji. Schemat zawiera:
- `users` - konta użytkowników z hashem hasła w kolumnie `password_hash`,
- `tickets` - zgłoszenia powiązane z użytkownikiem przez `user_id`.

Nie trzeba ręcznie tworzyć tabel. Przy lokalnej konfiguracji skopiuj `.env.example`
do `.env` i ustaw własny `SECRET_KEY`.

### Endpoint API:
- `GET /api/health` - publiczny endpoint sprawdzający stan aplikacji; zwraca `{"status": "ok"}` i kod HTTP 200.
### Opis aplikacji:
Aplikacja ma umożliwiać pracownikom i klientom zgłaszania awarii oraz problemów serwisowych, wszystko w jednej aplikacji, upraszczając komunikacje, która wcześniej była przez telefony/e-mail itp. Po zalogowaniu użytkownik ma możliwość tworzenia zgłoszenia i śledzenia jego statusu, a technik/serwisant nimi zarządza. System ma umożliwić sprawniejsze działanie techników oraz zgłaszanie awarii/usterek itd.