# Raport z wyników testów


**Środowisko:** Windows, Python `3.11.7`, `pytest 8.3.5`, Docker `29.8.2` (`testcontainers` z obrazem `postgres:17-alpine`)  
**Polecenie uruchomienia:** `.venv\Scripts\python.exe -m pytest -v`  


---

## Podsumowanie według kategorii

| Kategoria | Plik | Liczba testów (przypadków) | Status |
|---|---|---:|---|
| Test endpointu (`smoke`) | `tests/test_health.py` | 1 (1) | PASSED |
| Testy jednostkowe (`unit`) | `tests/test_unit.py` | 8 (13) | PASSED |
| Testy integracyjne (`integration`) | `tests/test_auth.py`, `tests/test_tickets.py`, `tests/test_seed.py`, `tests/test_database.py` | 6 (6) | PASSED |
| Testy bezpieczeństwa (`security`) | `tests/test_security.py` | 2 (2) | PASSED |
| **Łącznie** | **`tests/`** | **17 (22)** | **PASSED** |

---

## Szczegółowy opis wykonanych testów

### 1. Test endpointu (`tests/test_health.py`)
1. `test_health_returns_ok_without_login` — wywołuje `GET /api/health` bez logowania i weryfikuje status `200`, nagłówek `Content-Type: application/json` oraz ciało odpowiedzi `{"status": "ok"}`.

### 2. Testy jednostkowe (`tests/test_unit.py`)
1. `test_hash_password_can_be_verified` — sprawdza, że `hash_password` generuje hash różny od hasła jawnego i przechodzi weryfikację przez `verify_password`.
2. `test_verify_password_rejects_wrong_password` — sprawdza, że `verify_password` zwraca `False` dla błędnego hasła.
3. `test_ticket_data_normalizes_valid_values` — weryfikuje przycinanie białych znaków oraz normalizację wielkości liter dla pól `category` i `priority` w `_ticket_data`.
4. `test_ticket_data_rejects_invalid_input` (3 przypadki parametryzowane) — sprawdza odrzucenie niekompletnego zgłoszenia, nieprawidłowego priorytetu (`"urgent"`) oraz nieprawidłowej kategorii (`"unknown"`).
5. `test_validate_comment_content_strips_surrounding_whitespace` — weryfikuje przycięcie białych znaków w treści komentarza przez `validate_comment_content`.
6. `test_validate_comment_content_rejects_invalid_values` (3 przypadki parametryzowane) — sprawdza odrzucenie wartości `None`, samego białego znaku (`"   "`) oraz komentarza przekraczającego 5000 znaków.
7. `test_create_refresh_token_uses_session_and_persists_token` — z zamockowaną sesją SQLAlchemy i generatorem tokenów weryfikuje zapis obiektu `RefreshToken`, powiązanie z `user_id`, ustawienie `expires_at` oraz wywołanie `session.commit()`.
8. `test_login_required_rejects_expired_or_invalid_signature_token` (2 przypadki parametryzowane) — weryfikuje odrzucenie wygasłego tokena JWT oraz tokena podpisanego błędnym kluczem kodem `401`.

### 3. Testy integracyjne (`testcontainers` + PostgreSQL 17)
1. `tests/test_auth.py::test_register_user_with_valid_email_persists_hashed_password` — rejestruje użytkownika przez `POST /api/auth/register`, sprawdza status `201`, zwrot tokenów JWT oraz faktyczny zapis użytkownika w tabeli `users` z hasłem zahashowanym przez `bcrypt`.
2. `tests/test_auth.py::test_register_user_with_invalid_email_is_rejected_and_not_saved` — wysyła nieprawidłowy adres e-mail (`"invalid-email"`), weryfikuje status `400`, komunikat `{"error": "invalid email"}` oraz brak rekordu w tabeli `users`.
3. `tests/test_auth.py::test_login_refresh_and_logout_session_lifecycle` — sprawdza logowanie, rotację refresh tokena, odrzucenie powtórnie użytego starego refresh tokena (`401`), wylogowanie (`204`) i odrzucenie tokena po wylogowaniu (`401`).
4. `tests/test_tickets.py::test_client_ticket_and_comment_lifecycle` — sprawdza utworzenie zgłoszenia (`201`), odczyt (`200`), aktualizację tytułu (`200`), dodanie komentarza (`201`), stan rekordów `Ticket` i `Comment` w bazie danych oraz usunięcie zgłoszenia (`204`) wraz z potwierdzeniem usunięcia w bazie.
5. `tests/test_seed.py::test_seed_creates_all_entities_idempotently` — dwukrotnie uruchamia `db.seed.seed_test_data()` na czystej bazie i weryfikuje utworzenie bez duplikatów 4 użytkowników (2 klientów, 2 techników), 3 zgłoszeń, 3 komentarzy i 2 wpisów historii `TicketHistory`.
6. `tests/test_database.py::test_database_is_created_with_related_tables` — sprawdza w `information_schema` po migracjach Alembic obecność tabel `users` i `tickets` oraz istnienie klucza obcego `tickets.client_id -> users`.

### 4. Testy bezpieczeństwa (`tests/test_security.py`)
1. `test_user_cannot_modify_delete_or_access_other_users_or_technician_resources` — sprawdza, że próba edycji (`PATCH`) i usunięcia (`DELETE`) zgłoszenia innego użytkownika oraz próba odczytu `/api/technician/tickets` przez klienta zwracają `404`, a zgłoszenie właściciela pozostaje nienaruszone w bazie.
2. `test_password_length_policy_enforced_on_register_and_password_change` — sprawdza odrzucenie zbyt krótkiego hasła przy rejestracji (< 12 znaków, `400`) oraz przy zmianie hasła przez `PATCH /api/users/me/password` (< 8 znaków, `400`), potwierdzając że dotychczasowe hasło nadal umożliwia logowanie (`200`).


### 5. Zdjęcie z przeprowadzonych testów
![Tu powinno być zdjęcie, path: "./resources/Screenshot%202026-11-25%20160924.png"](./resources/Screenshot%202026-11-25%20160924.png)
