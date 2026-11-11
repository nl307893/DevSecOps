# DevSecOps - system zgłoszeń serwisowych

## System zgłoszeń serwisowych
### Członkowie zespołu:
- Michał Barcik
- Adam Grelewicz
- Norbert Luchowski
#### Tablica Trello:
- https://trello.com/b/r7wdp3wR

## Technologie

- Python 3.11+
- Flask
- PostgreSQL 17
- SQLAlchemy
- Alembic
- JWT
- bcrypt
- Docker Compose

## Wymagania środowiskowe

Przed uruchomieniem zainstaluj:

- Python 3.11 lub nowszy,
- Docker Desktop z Docker Compose,
- Git.

Na Windows wymagany jest PowerShell, jeśli chcesz uruchomić aplikację jedną komendą. PostgreSQL nie musi być instalowany lokalnie, ponieważ uruchamia go Docker Compose. Inaczej należy odpowiednio skonfigurować plik .env do połączenia lokalnego

## Sposób Instalacji

Sklonuj repozytorium i przejdź do jego katalogu:

```powershell
git clone https://github.com/nl307893/DevSecOps.git
cd DevSecOps
```

Utwórz lokalną konfigurację:

```powershell
Copy-Item .env.example .env
```

W pliku `.env` ustaw własne wartości, szczególnie:

```env
POSTGRES_PASSWORD=haslo-bazy
SECRET_KEY=dlugi-losowy-sekret
```

Utwórz środowisko wirtualne i zainstaluj zależności:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Uruchomienie

Najprostszy sposób:

```powershell
.\start.ps1
```

Skrypt:

1. uruchamia PostgreSQL w Dockerze,
2. czeka na gotowość bazy,
3. instaluje zależności przez `run.py`,
4. wykonuje migracje Alembic,
5. uruchamia backend.

Alternatywnie:

```powershell
docker compose up -d --wait db
python run.py
```

## Adres aplikacji

Backend działa domyślnie pod adresem:

```text
http://127.0.0.1:5000
```

Publiczny endpoint kontrolny:

```http
GET /api/health
```

Odpowiedź:

```json
{"status": "ok"}
```

## Uwierzytelnianie

API używa krótkotrwałego JWT access tokena oraz refresh tokena zapisywanego
w bazie jako hash. Chronione endpointy wymagają nagłówka:

```http
Authorization: Bearer <access_token>
```

## Endpointy autoryzacji

| Metoda | Endpoint | Dostęp | Opis |
|---|---|---|---|
| `POST` | `/api/auth/register` | publiczny | Rejestracja klienta |
| `POST` | `/api/auth/login` | publiczny | Logowanie |
| `POST` | `/api/auth/refresh` | publiczny | Odświeżenie tokena |
| `POST` | `/api/auth/logout` | zalogowany token | Wylogowanie |

### Rejestracja

```powershell
$body = @{
    email = "client@example.com"
    password = "ClientPassword123!"
    first_name = "Jan"
    last_name = "Kowalski"
} | ConvertTo-Json -Compress

Invoke-RestMethod `
    -Uri "http://127.0.0.1:5000/api/auth/register" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

### Logowanie

```powershell
$body = @{
    email = "client@example.com"
    password = "ClientPassword123!"
} | ConvertTo-Json -Compress

$login = Invoke-RestMethod `
    -Uri "http://127.0.0.1:5000/api/auth/login" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$token = $login.access_token
```

## Endpointy klienta

Klient może przeglądać i modyfikować wyłącznie własne zgłoszenia.

| Metoda | Endpoint | Opis |
|---|---|---|
| `GET` | `/api/users/me` | Dane własnego profilu |
| `PATCH` | `/api/users/me/name` | Zmiana imienia i nazwiska |
| `PATCH` | `/api/users/me/email` | Zmiana emaila |
| `PATCH` | `/api/users/me/password` | Zmiana hasła |
| `DELETE` | `/api/users/me` | Usunięcie konta |
| `GET` | `/api/tickets` | Lista własnych zgłoszeń |
| `POST` | `/api/tickets` | Utworzenie zgłoszenia |
| `GET` | `/api/tickets/<uuid>` | Szczegóły własnego zgłoszenia |
| `PATCH` | `/api/tickets/<uuid>` | Edycja zgłoszenia w statusie `new` |
| `DELETE` | `/api/tickets/<uuid>` | Usunięcie zgłoszenia w statusie `new` |
| `GET` | `/api/tickets/<uuid>/comments` | Lista komentarzy |
| `POST` | `/api/tickets/<uuid>/comments` | Dodanie komentarza |

Priorytet zgłoszenia jest zwracany wyłącznie w endpointach technika.

### Utworzenie zgłoszenia

Tytuł, opis i kategoria są wymagane. Dozwolone kategorie to:
`hardware`, `software`, `network`, `access`, `other`.

```powershell
$body = @{
    title = "Awaria drukarki"
    description = "Drukarka nie drukuje"
    category = "hardware"
} | ConvertTo-Json -Compress

$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod `
    -Uri "http://127.0.0.1:5000/api/tickets" `
    -Method Post `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $body
```

### Dodanie komentarza

```powershell
$body = @{
    content = "Problem nadal występuje"
} | ConvertTo-Json -Compress

Invoke-RestMethod `
    -Uri "http://127.0.0.1:5000/api/tickets/<ticket_uuid>/comments" `
    -Method Post `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $body
```

Komentarze są zablokowane dla statusów `resolved`, `cancelled` i `archived`.

## Endpointy technika

Endpointy technika wymagają roli `technician`. Priorytet jest dostępny tylko
w tych odpowiedziach.

| Metoda | Endpoint | Opis |
|---|---|---|
| `GET` | `/api/technician/tickets` | Wszystkie zgłoszenia |
| `GET` | `/api/technician/tickets/assigned` | Zgłoszenia przypisane do siebie |
| `GET` | `/api/technician/tickets/<uuid>` | Szczegóły zgłoszenia |
| `GET` | `/api/technician/tickets/<uuid>/history` | Historia statusów |
| `POST` | `/api/technician/tickets/<uuid>/comments` | Dodanie komentarza |
| `GET` | `/api/technician/tickets/<uuid>/comments` | Lista komentarzy |
| `PATCH` | `/api/technician/tickets/<uuid>/assign` | Przypisanie technika |
| `PATCH` | `/api/technician/tickets/<uuid>/priority` | Zmiana priorytetu |
| `PATCH` | `/api/technician/tickets/<uuid>/category` | Zmiana kategorii |
| `PATCH` | `/api/technician/tickets/<uuid>/status` | Zmiana statusu |
| `PATCH` | `/api/technician/tickets/<uuid>/archive` | Archiwizacja |

Przypisanie zgłoszenia samemu sobie automatycznie ustawia status `instatus`.
Operacje przypisania, edycji i usuwania używają blokady wiersza w bazie, aby
uniknąć konfliktu równoczesnych żądań.

### Zmiana statusu przez technika

```powershell
$body = @{
    status = "resolved"
} | ConvertTo-Json -Compress

$technicianHeaders = @{
    Authorization = "Bearer <technician_access_token>"
}

Invoke-RestMethod `
    -Uri "http://127.0.0.1:5000/api/technician/tickets/<ticket_uuid>/status" `
    -Method Patch `
    -Headers $technicianHeaders `
    -ContentType "application/json" `
    -Body $body
```

Dozwolone statusy to: `new`, `instatus`, `resolved`, `cancelled`, `archived`.

### Przypisanie zgłoszenia

```powershell
curl.exe -X PATCH http://127.0.0.1:5000/api/technician/tickets/<ticket_uuid>/assign `
  -H "Authorization: Bearer <technician_access_token>" `
  -H "Content-Type: application/json" `
  -d '{}'
```

Puste body przypisuje zgłoszenie zalogowanemu technikowi.

## Dane demonstracyjne
Ustaw lokalnie dane użytkowników i jawnie włącz seed:

```powershell
$env:SEED_DEMO_DATA="1"
$env:SEED_CLIENT_EMAIL="client@example.com"
$env:SEED_CLIENT_PASSWORD="ClientPassword123!"
$env:SEED_TECHNICIAN_EMAIL="technician@example.com"
$env:SEED_TECHNICIAN_PASSWORD="TechnicianPassword123!"
.venv\Scripts\python.exe -m db.seed
```

## Migracje

Migracje są przechowywane w `db/migrations/versions/` i wykonywane
automatycznie przy starcie aplikacji. Ręczne wykonanie:

```powershell
.venv\Scripts\python.exe -m db.migrate
```

## Testy

Testy wymagają osobnej bazy PostgreSQL. Ustaw `TEST_DATABASE_URL`, a następnie:

```powershell
$env:TEST_DATABASE_URL="postgresql://devsecops:haslo-bazy@localhost:5435/devsecops_test"
.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Pojedynczy moduł:

```powershell
.venv\Scripts\python.exe -m unittest tests.test_tickets
```

## Zatrzymanie

Zatrzymanie kontenera:

```powershell
docker compose down
```

Usunięcie kontenera wraz z danymi PostgreSQL:

```powershell
docker compose down -v
```

## Struktura projektu

- `app/` - aplikacja Flask,
- `app/api/Client/` - endpointy klienta,
- `app/api/Technician/` - endpointy technika,
- `app/auth/` - JWT, bcrypt i autoryzacja ról,
- `app/models/` - modele SQLAlchemy,
- `db/migrations/` - migracje Alembic,
- `db/seed.py` - dane demonstracyjne,
- `tests/` - testy API i bazy danych.
