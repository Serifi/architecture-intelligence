# Architecture Intelligence

Architecture Intelligence is a web-based, AI-powered platform that supports the capture, analysis, and documentation of software architecture decisions by integrating information from multiple sources and generating context-aware architecture suggestions.

> Voraussetzung für die Ausführung ist eine, vorzugsweise globale, Installation von **Python 3.13** und **Node 20.19.0** sowie das Starten von Docker!
>
> **Python:** https://www.python.org/downloads/  
> **Node:** https://nodejs.org/en/download

## Anwendung
<img width="2545" height="1249" alt="1" src="https://github.com/user-attachments/assets/e29c4a3b-4f4e-4f37-8ae4-da937df55215" />
<img width="2554" height="819" alt="5" src="https://github.com/user-attachments/assets/14a076b0-8289-4ba9-8c0c-75f2e799dced" />
<img width="2551" height="576" alt="15b" src="https://github.com/user-attachments/assets/c96a1da9-581a-42d7-9dd5-4d922a72052f" />
<img width="2406" height="1140" alt="20" src="https://github.com/user-attachments/assets/f40b6691-2c9e-4d77-90c2-500eb5b41b11" />

## Diagramme
<img width="981" height="996" alt="ER Diagramm" src="https://github.com/user-attachments/assets/323d4293-a954-472c-9abe-da0d36e83a9a" />
<img width="879" height="814" alt="Komponentendiagramm" src="https://github.com/user-attachments/assets/7570315b-f132-4258-9c82-3b88ea26f21e" />
<img width="1652" height="404" alt="Prozessmodell" src="https://github.com/user-attachments/assets/9664390f-f862-4ff1-bdeb-3fc62bab4206" />

## Anleitung

### 1. Setup
Vorbereitung des Projekts und Installation notwendiger Pakete.

##### macOS / Linux
```bash
./dev.sh setup
```

##### Windows
```bash
.\dev.ps1 -Command setup
```

### 2. Testdaten (optional)
Einspielen von Testdaten in die Datenbank; bei unveränderten Daten nur einmalig auszuführen. 

##### macOS / Linux
```bash
./dev.sh init-db
```

##### Windows
```bash
.\dev.ps1 -Command init-db
```

### 3. Backend & Frontend
Starten von Back- und Frontend.
Key muss vorher gesetzt werden!

##### macOS / Linux
```bash
./dev.sh dev
```

##### Windows
```bash
.\dev.ps1 -Command dev
```

##### **ODER**
Starten von separatem Back- und Frontend.
#### 3.1 Backend

##### macOS / Linux
```bash
./dev.sh backend
```

##### Windows
```bash
.\dev.ps1 -Command backend
```

#### 3.2 Frontend

##### macOS / Linux
```bash
./dev.sh frontend
```

##### Windows
```bash
.\dev.ps1 -Command frontend
```

## Anleitung zur Ausführung der Tests

##### macOS / Linux
```bash
./test.sh
```

##### Windows
```bash
./test.ps1
```

## Ports
- Server: 8000
- Client: 3000  
- Datenbank: 5432
