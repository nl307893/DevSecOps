# DevSecOps
## System zgłoszeń serwisowych
### Członkowie zespołu:
- Rodo 1
- Rodo 2
- Rodo 3
#### Tablica Trello:
- https://trello.com/b/r7wdp3wR
### Wybrana technologia:
- Backend: Python Flask
- Fronted: JavaScript React
### Struktura projektu:
- `app/` - kod aplikacji Flask
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
### Opis aplikacji:
Aplikacja ma umożliwiać pracownikom i klientom zgłaszania awarii oraz problemów serwisowych, wszystko w jednej aplikacji, upraszczając komunikacje, która wcześniej była przez telefony/e-mail itp. Po zalogowaniu użytkownik ma możliwość tworzenia zgłoszenia i śledzenia jego statusu, a technik/serwisant nimi zarządza. System ma umożliwić sprawniejsze działanie techników oraz zgłaszanie awarii/usterek itd.