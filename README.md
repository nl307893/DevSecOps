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
```
`.venv\Scripts\python.exe -m pytest -v`  
```
### Wykorzystane narzędzia

- `pytest` (`pyproject.toml`) — główny framework testowy i runner z obsługą markerów (`unit`, `integration`, `security`, `smoke`),
- `testcontainers[postgres]` — automatyczne uruchamianie izolowanego kontenera PostgreSQL (`postgres:17-alpine`) dla testów integracyjnych i bezpieczeństwa wraz z migracjami Alembic oraz czyszczeniem tabel między testami,
- `unittest.mock` — izolacja zależności (np. sesji bazy danych) w testach jednostkowych.

### Zakres testów

#### 1. Test endpointu (`tests/test_health.py` — 1 test)
- `test_health_returns_ok_without_login` — wywołuje `GET /api/health` bez logowania i sprawdza kod `200`, `Content-Type: application/json` oraz odpowiedź `{"status": "ok"}`.

#### 2. Testy jednostkowe (`tests/test_unit.py` — 8 testów / 13 przypadków)
1. `test_hash_password_can_be_verified` — sprawdza, że `hash_password` tworzy hash różny od hasła jawnego i przechodzi weryfikację przez `verify_password`.
2. `test_verify_password_rejects_wrong_password` — sprawdza, że `verify_password` zwraca `False` dla błędnego hasła.
3. `test_ticket_data_normalizes_valid_values` — weryfikuje przycinanie białych znaków oraz normalizację wielkości liter dla `category` i `priority` w `_ticket_data`.
4. `test_ticket_data_rejects_invalid_input` (3 przypadki) — sprawdza odrzucenie brakujących pól wymaganych, nieprawidłowego priorytetu (`"urgent"`) oraz nieprawidłowej kategorii (`"unknown"`).
5. `test_validate_comment_content_strips_surrounding_whitespace` — weryfikuje usunięcie skrajnych spacji z treści komentarza przez `validate_comment_content`.
6. `test_validate_comment_content_rejects_invalid_values` (3 przypadki) — sprawdza odrzucenie wartości `None`, pustego tekstu (`"   "`) oraz komentarza dłuższego niż 5000 znaków.
7. `test_create_refresh_token_uses_session_and_persists_token` — z zamockowaną sesją i generatorem tokenów sprawdza zapis `RefreshToken`, powiązanie z `user_id`, ustawienie `expires_at` i wywołanie `session.commit()`.
8. `test_login_required_rejects_expired_or_invalid_signature_token` (2 przypadki) — sprawdza, że dekorator `@login_required` odrzuca wygasły token JWT oraz token z nieprawidłowym podpisem kodem `401`.

#### 3. Testy integracyjne (`testcontainers` + PostgreSQL — 6 testów)
1. `tests/test_auth.py::test_register_user_with_valid_email_persists_hashed_password` — rejestruje użytkownika (`POST /api/auth/register`), sprawdza status `201`, zwrócenie tokenów JWT oraz faktyczny zapis użytkownika w tabeli `users` z hashem `bcrypt`.
2. `tests/test_auth.py::test_register_user_with_invalid_email_is_rejected_and_not_saved` — wysyła niepoprawny e-mail, sprawdza status `400`, błąd `"invalid email"` oraz brak rekordu w tabeli `users`.
3. `tests/test_auth.py::test_login_refresh_and_logout_session_lifecycle` — sprawdza logowanie, rotację refresh tokena, odrzucenie powtórnie użytego starego tokena (`401`), wylogowanie (`204`) i odrzucenie odświeżania po wylogowaniu (`401`).
4. `tests/test_tickets.py::test_client_ticket_and_comment_lifecycle` — sprawdza utworzenie zgłoszenia (`201`), odczyt (`200`), aktualizację tytułu (`200`), dodanie komentarza (`201`), obecność zmian w bazie danych oraz usunięcie zgłoszenia (`204`) z potwierdzeniem usunięcia w bazie.
5. `tests/test_seed.py::test_seed_creates_all_entities_idempotently` — uruchamia dwukrotnie `db.seed.seed_test_data()` i sprawdza utworzenie bez duplikatów 4 użytkowników (2 klientów, 2 techników), 3 zgłoszeń, 3 komentarzy i 2 wpisów historii `TicketHistory`.
6. `tests/test_database.py::test_database_is_created_with_related_tables` — po migracjach Alembic sprawdza w `information_schema` utworzenie tabel `users` i `tickets` oraz relację klucza obcego `tickets.client_id -> users`.

#### 4. Testy bezpieczeństwa (`tests/test_security.py` — 2 scenariusze)
1. `test_user_cannot_modify_delete_or_access_other_users_or_technician_resources` — sprawdza ochronę przed IDOR i eskalacją uprawnień: próba edycji (`PATCH`) lub usunięcia (`DELETE`) zgłoszenia innego użytkownika oraz dostęp klienta do `/api/technician/tickets` zwracają `404`, a rekord właściciela pozostaje nienaruszony w bazie.
2. `test_password_length_policy_enforced_on_register_and_password_change` — sprawdza odrzucenie zbyt krótkiego hasła przy rejestracji (< 12 znaków, `400`) oraz przy zmianie hasła przez `PATCH /api/users/me/password` (< 8 znaków, `400`), potwierdzając że dotychczasowe hasło nadal pozwala się zalogować (`200`).

### Uruchomienie testów

Zainstaluj zależności testowe (jednorazowo):

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Uruchomienie **wszystkich testów jednym poleceniem** (wymaga działającego Dockera dla kontenera PostgreSQL):

```powershell
.venv\Scripts\python.exe -m pytest -v
```

Uruchomienie wyłącznie testów niewymagających Dockera (jednostkowych i smoke):

```powershell
.venv\Scripts\python.exe -m pytest -v -m "unit or smoke"
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
