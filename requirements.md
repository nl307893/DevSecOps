## Cel aplikacji:
Celem aplikacji jest dodanie szybkiej i sprawnej możliwości kontaktu między klientem zgłaszającym awarię/usterkę, a pracownikiem/serwistanem.
## Na co pozwala aplikacja:
Aplikacja umożliwia dodawanie zgłoszeń po stronie użytkownika, natomiast pracownik ma możliwość odpowiadania na nie/
## Wymagania funkcjonalne:
- Rejestracja nowego użytkownika z zapisem konta w bazie danych.
- Logowanie i wylogowanie. Funkcje zgłoszeń są dostępne tylko po zalogowaniu.
- Dodawanie zgłoszenia (tytuł, opis, kategoria, priorytet) z zapisem w bazie.
- Lista własnych zgłoszeń z filtrowaniem po statusie (Nowe, W trakcie, Zamknięte).
- Podgląd szczegółów zgłoszenia wraz z historią zmian statusu.
- Dodawanie komentarzy do zgłoszenia przez użytkownika i technika.
- Panel technika: lista wszystkich zgłoszeń, zmiana statusu i przypisanie zgłoszenia.
- Edycja lub anulowanie własnego zgłoszenia, dopóki ma status „Nowe".
## Wymaganie bezpieczeństwa:
- Nieprzechowywanie haseł jawnym tekstem albo hasło hashować z solą, albo logowanie bez użycia hasła (inne metody)
- Walidacja, sanityzacja danych wejściowych podawanych przez użytkownika i serwisanta
- Kontrola dostępu: czy dostęp do danego zasobu ma tylko osoba uprawniona, np. klient może widzieć tylko swoje złoszenia, nikt inny
- Ochrona przed XSS, CSRF, SQL injection i pokrewne
- Nieujawnianie błędów i sekretów kodu użytkownik (np. dać błąd 404, zamiast nie masz uprawnień do zasobu)
- Bezpieczne sesje użytkownika, wyhasanie sesji, unieważnianie przy logowaniu itd. 
## Model Zagrożeń:
| Zagrożenie | Czego dotyczy | Możliwe konsekwencje | Planowana kontrola |
|---|---|---|---|
| SQL Injection | Formularze logowania, zgłoszeń i pokrewne baza danych | Wyciek lub modyfikacja danych, obejście logowania | Zapytania parametryzowane lub ORM, walidacja danych|
| Zgadywanie haseł (brute force, credential stuffing) | Formularz logowania | Przejęcie kont użytkowników lub technika | Limit prób i czasowa blokada, polityka haseł, neutralny komunikat błędu |
| Broken access control (IDOR), np. zmiana ID zgłoszenia w adresie URL | Dostęp do zgłoszeń i funkcji technika | Odczyt cudzych zgłoszeń, nieuprawniona zmiana statusu | Sprawdzanie roli i właściciela zasobu po stronie serwera |
| XSS (wstrzyknięcie skryptu) | Pola tytułu, opisu i komentarzy | Kradzież sesji, wykonanie złośliwego kodu w przeglądarce technika | Escapowanie danych na wyjściu, nagłówek CSP, ciasteczka HttpOnly |
| Przechwycenie sesji lub ruchu | Transmisja danych, ciasteczka sesyjne | Podszycie się pod użytkownika, podsłuch haseł | Ciasteczka Secure i SameSite, krótki czas życia sesji |
| Wyciek bazy danych | Tabela users | Ujawnienie haseł użytkowników | Hash z solą, brak sekretów w repozytorium |