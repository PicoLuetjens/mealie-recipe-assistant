# Mealie Recipe Assistant

Lokales, Docker-basiertes Tool zum Entwerfen und Anlegen von Rezepten in Mealie. Es bietet eine Nuxt-/Vue-3-Oberfläche mit TypeScript und ein FastAPI-Backend. Nutzer können einen Rezeptwunsch per Texteingabe oder Sprache formulieren, Mengen für Personen skalieren und das bestätigte Ergebnis im Namen eines dedizierten Mealie-Service-Benutzers speichern.

> Dieses Repository enthält absichtlich **keine echten Zugangsdaten**. Alle Werte in `.env.example` sind Dummies und müssen vor einem Start ersetzt werden.

## Funktionen

- Anmeldung und rollenbasierte Nutzerverwaltung
  - Beim ersten Start wird ein Administrator aus `FIRST_ADMIN_EMAIL` und `FIRST_ADMIN_PASSWORD` angelegt.
  - Administratoren können zusätzliche Benutzer und weitere Administratoren anlegen und Konten aktivieren/deaktivieren.
  - Passwörter werden mit Argon2 gehasht; das Frontend erhält nur ein zeitlich begrenztes JWT.
- Rezeptentwurf per Chat-Eingabe über die OpenAI Responses API
- Spracheingabe im Browser mit `MediaRecorder`, serverseitige Transkription über die OpenAI-Audio-API
- Strukturiertes Rezeptmodell mit Zutaten, Schritten, Basisportionen, Tags und Bildprompt
- Dynamische Skalierung der numerischen Zutatenmengen im Frontend
- Mealie-Export mit dem API-Token eines separaten Mealie-Nutzers
- Optionale Bildgenerierung und Upload zum erzeugten Mealie-Rezept
- Demo-Rezept im Backend, falls kein gültiger OpenAI-Key hinterlegt ist

## Architektur

```text
Browser
  └─ Nuxt 3 / Vue 3 / TypeScript (Port 3000)
       └─ FastAPI (Port 8000)
            ├─ SQLite: Nutzer, Rollen und Passwort-Hashes
            ├─ OpenAI: Rezept, Transkription, Bild
            └─ Mealie REST API: Rezept und Bild
```

Das Backend ist die einzige Komponente, die OpenAI- und Mealie-Zugangsdaten kennt. Das Browser-Frontend kommuniziert ausschließlich mit der eigenen FastAPI.

## Projektstruktur

```text
.
├── frontend/                 # Nuxt 3 / Vue 3 / TypeScript
│   ├── components/            # Rezeptansicht, Nutzerverwaltung
│   ├── composables/useApi.ts  # vollständig typisierte API-Client-Funktionen
│   ├── types/api.ts           # gemeinsames TypeScript-API-Vertragsmodell
│   └── pages/index.vue        # Login, Chat, Spracheingabe und Rezeptprozess
├── backend/
│   └── app/
│       ├── api/               # Auth-, Nutzer- und Rezept-Routen
│       ├── core/              # Konfiguration, Datenbank, Sicherheit
│       ├── models/            # SQLAlchemy-Nutzermodell
│       └── services/          # OpenAI- und Mealie-Adapter
├── docker-compose.yml
└── .env.example
```

## Voraussetzungen

- Docker Engine mit Docker Compose v2
- Eine laufende Mealie-Instanz, erreichbar aus dem Assistant-Backend
- Ein OpenAI-API-Key für KI-Rezepte, Spracheingabe und Bilder
- Eine zufällig erzeugte JWT-Secret-Zeichenfolge

Für die lokale Entwicklung ohne OpenAI kann das Projekt mit den Dummywerten gestartet werden. In diesem Fall erzeugt der Rezeptendpunkt ein festes Demo-Rezept. Spracheingabe und Bildgenerierung benötigen einen gültigen OpenAI-Key.

## Mealie vorbereiten

1. In Mealie einen Nutzer `recipe-assistant` anlegen.
2. Diesem Nutzer **keine Administratorrechte** geben und ihn dem Haushalt bzw. der Gruppe zuordnen, in der Rezepte landen sollen.
3. Im Profil dieses Nutzers einen langlebigen API-Token erzeugen.
4. Diesen Wert nur in `MEALIE_API_TOKEN` eintragen.

Alle Schreibvorgänge nach Mealie nutzen genau diesen Token. Dadurch wird die Ersteller-Identität in Mealie dem Service-Benutzer zugeordnet. Das Rezept wird nie über ein Benutzer-Token aus dem Browser angelegt.

Die Mealie-API kann sich je nach verwendeter Version unterscheiden. Vor Produktivbetrieb die Payloads in `backend/app/services/mealie_service.py` mit der lokalen Mealie-Dokumentation unter `http://DEINE-MEALIE-INSTANZ/docs` abgleichen, besonders das Zutatenformat und den Bild-Upload.

## Konfiguration

Die Beispielkonfiguration kopieren:

```bash
cp .env.example .env
```

Dann diese Werte in `.env` ersetzen:

| Variable | Bedeutung | Beispiel / Hinweis |
|---|---|---|
| `OPENAI_API_KEY` | OpenAI-Server-Key | Niemals ins Frontend eintragen oder committen. |
| `MEALIE_BASE_URL` | Mealie-Adresse aus Sicht des Backend-Containers | Bei gleichem Docker-Netz z. B. `http://mealie:9000`. |
| `MEALIE_API_TOKEN` | Token des `recipe-assistant`-Mealie-Benutzers | Kein Admin-Token. |
| `JWT_SECRET` | Signierschlüssel der Anwendung | Langer zufälliger Wert, mindestens 32 Zeichen. |
| `FIRST_ADMIN_EMAIL` | erste lokale Admin-E-Mail | Nach erstem Start wird dieser Nutzer erzeugt. |
| `FIRST_ADMIN_PASSWORD` | erstes lokales Admin-Passwort | Vor dem ersten Start ändern; mindestens 12 Zeichen. |
| `NUXT_PUBLIC_API_BASE` | API-Adresse, die der Browser nutzt | Lokal `http://localhost:8000/api`. |

Die Platzhalter in `.env.example` sind absichtlich ungültig. Die Datei `.env` ist per `.gitignore` ausgeschlossen und darf nicht eingecheckt werden.

## Start mit Docker

In diesem Projektordner:

```bash
docker compose up --build
```

Danach:

- Weboberfläche: `http://localhost:3000`
- Backend-OpenAPI: `http://localhost:8000/docs`
- Backend-Gesundheitsstatus: `http://localhost:8000/api/health`

Zum Beenden:

```bash
docker compose down
```

Die lokale SQLite-Datenbank liegt in dem Docker-Volume `assistant-data`. Sie bleibt bei `docker compose down` bestehen. Für einen vollständigen lokalen Neustart inklusive Nutzerkonten kann das Volume bewusst entfernt werden:

```bash
docker compose down -v
```

## Rezeptprozess

1. Nutzer meldet sich an.
2. Nutzer tippt seinen Rezeptwunsch ein oder startet die Spracheingabe.
3. Das Backend transkribiert Audio und erzeugt einen strikt strukturierten Rezeptentwurf.
4. Das Frontend zeigt Zutaten und Schritte; die Portionenzahl kann für die Anzeige verändert werden.
5. Zutaten mit `scalable: true` werden mathematisch skaliert. Qualitative Mengen wie „Salz nach Geschmack“ bleiben unverändert.
6. „In Mealie speichern“ erzeugt das Rezept per Mealie-API im Namen des Service-Benutzers.
7. Wenn ein Bildprompt vorliegt und OpenAI konfiguriert ist, generiert das Backend ein Bild und lädt es nach Mealie hoch.

Das gespeicherte Rezept behält immer seine Basisportionen. Die im Frontend gewählte Anzeigeportion verändert nicht den gespeicherten Rezeptentwurf.

## Typisierte API-Verträge

Die TypeScript-Verträge liegen in `frontend/types/api.ts`; sie beschreiben Nutzer, Login-Antworten, Rezeptentwürfe, Zutaten, Status und Mealie-Antworten. Der Client in `frontend/composables/useApi.ts` gibt bei jedem API-Aufruf den passenden generischen Rückgabetyp an.

Wichtige Routen:

| Methode | Route | Berechtigung | Zweck |
|---|---|---|---|
| `POST` | `/api/auth/login` | öffentlich | JWT-Anmeldung |
| `GET` | `/api/auth/me` | angemeldet | aktueller Nutzer |
| `GET` | `/api/users` | Admin | Nutzer auflisten |
| `POST` | `/api/users` | Admin | Nutzer anlegen |
| `PATCH` | `/api/users/{id}` | Admin | Rolle oder Aktivstatus ändern |
| `POST` | `/api/recipes/generate` | angemeldet | KI- oder Demo-Rezept erzeugen |
| `POST` | `/api/recipes/transcribe` | angemeldet | Audio transkribieren |
| `POST` | `/api/recipes/publish` | angemeldet | Rezept inklusive optionalem Bild nach Mealie schreiben |

## Sicherheit und Betrieb

- Zugangsdaten ausschließlich über `.env` oder im Produktivbetrieb über Docker Secrets setzen.
- Das aktuelle Compose-Beispiel ist für lokalen Einsatz vorgesehen. Für produktive Nutzung HTTPS und einen Reverse Proxy vor Nuxt/FastAPI einsetzen.
- Das CORS-Setup erlaubt standardmäßig nur `http://localhost:3000`; für einen anderen Host in `backend/app/main.py` anpassen.
- Zugangsdaten werden nicht geloggt. Audio wird nur für den Transkriptionsaufruf im Speicher gehalten und nicht gespeichert.
- Eine echte Produktivumgebung sollte Bildgenerierung in eine Queue/Worker auslagern, Rate Limits ergänzen und eine Postgres-Datenbank statt SQLite verwenden.

## Nicht in diesem Auftrag ausgeführt

Es wurden keine Pakete installiert, keine Images gebaut, kein Container, Server, Test oder Linter gestartet und keine echten Tokens eingesetzt. Der Code wurde ausschließlich erzeugt.
