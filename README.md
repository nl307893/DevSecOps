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
- `app/models/` - modele SQLAlchemy ORM
- `app/auth/` - JWT, hashowanie haseł i autoryzacja ról
- `db/migrations/` - wersjonowane migracje bazy danych Alembic
- `tests/` - testy aplikacji
- `.env` - lokalna konfiguracja i dane poufne (plik ignorowany przez Git)
- `requirements.txt` - przypięte wersje zależności Pythona

### Uruchomienie backendu:
Baza PostgreSQL uruchamia się w Dockerze. Skopiuj `.env.example` do `.env` i ustaw własne `POSTGRES_PASSWORD`. `DATABASE_URL` powinien wskazywać ten sam port, użytkownika, hasło i bazę.

```bash
python -m venv .venv
```

Windows:
```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
docker compose up -d --wait db
python run.py
```

`docker compose up -d --wait db` uruchamia bazę PostgreSQL, czeka na jej gotowość i zapisuje dane w trwałym wolumenie `postgres_data`.
`python run.py` instaluje zależności, uruchamia migracje Alembic do wersji `head` i uruchamia backend pod adresem `http://127.0.0.1:5000`.

### Dane demonstracyjne

Dane demonstracyjne są tworzone osobnym skryptem, a nie podczas migracji.
Ustaw w lokalnym `.env` dane `SEED_CLIENT_*` i `SEED_TECHNICIAN_*`, a następnie
jawnie włącz seedowanie:

```powershell
$env:SEED_DEMO_DATA="1"
.venv\Scripts\python.exe -m db.seed
```

Skrypt jest idempotentny i nie nadpisuje istniejących użytkowników.

### Uwierzytelnianie

API używa krótkotrwałego JWT access tokena oraz refresh tokena zapisywanego
w bazie jako hash. Dostępne endpointy:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/refresh`
- `POST /api/auth/logout`

Chronione endpointy mogą używać `@login_required` albo
`@roles_required("technician")` z `app.auth.decorators`.
### Migracje bazy danych

Migracje są przechowywane w `db/migrations/versions/`. Po dodaniu nowej migracji uruchom:
```powershell
.venv\Scripts\python.exe -m db.migrate
```

W aplikacji migracje są wykonywane automatycznie przy starcie, więc standardowy `python run.py` nadal wystarcza.

Zatrzymanie bazy:
```powershell
docker compose down
```

Usunięcie bazy wraz z danymi:
```powershell
docker compose down -v
```

Testy PostgreSQL wymagają ustawienia `TEST_DATABASE_URL` i uruchamiają się poleceniem:
```powershell
$env:TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/devsecops_test"
python -m unittest discover -s tests -p "test_*.py"
```

### Endpoint API:
- `GET /api/health` - publiczny endpoint sprawdzający stan aplikacji; zwraca `{"status": "ok"}` i kod HTTP 200.
### Opis aplikacji:
Aplikacja ma umożliwiać pracownikom i klientom zgłaszania awarii oraz problemów serwisowych, wszystko w jednej aplikacji, upraszczając komunikacje, która wcześniej była przez telefony/e-mail itp. Po zalogowaniu użytkownik ma możliwość tworzenia zgłoszenia i śledzenia jego statusu, a technik/serwisant nimi zarządza. System ma umożliwić sprawniejsze działanie techników oraz zgłaszanie awarii/usterek itd.