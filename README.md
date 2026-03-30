# Architecture Intelligence

> Voraussetzung für die Ausführung ist eine, vorzugsweise globale, Installation von **Python 3.13** und **Node 20.19.0** sowie das Starten von Docker!
>
> **Python:** https://www.python.org/downloads/  
> **Node:** https://nodejs.org/en/download



## Anleitung zur Ausführung der Anwendung

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