
# README.md  
## GuideOS Bildschirmfoto‑Editor  
### Version 1.8 – 18.02.2026  
**Autoren:** evilware666 & Helga  
**Lizenz:** MIT  
**Datei:** `guideos-screenshot-editor.py`

Der **GuideOS Bildschirmfoto‑Editor** ist ein leistungsstarkes, erweitertes Screenshot‑ und Markup‑Tool für Linux.  
Es kombiniert präzise Bildschirmaufnahme‑Funktionen mit einem vollwertigen Editor für Annotationen, Formen, Text, Freihand‑Zeichnung, Undo/Redo und PNG‑Export.  
Das Tool unterstützt Multi‑Monitor‑Setups, Wayland‑Fallbacks und bietet zusätzlich einen JSON‑basierten Request‑Modus für automatisierte Abläufe.

Ideal für Dokumentation, Support, Tutorials, Software‑Erklärungen und professionelle Markups.

---

## ✨ Hauptfunktionen

### 🖥️ Multi‑Monitor‑Unterstützung
- Erkennung aller angeschlossenen Monitore  
- Korrekte Geometrie‑Berechnung (Offsets, Auflösungen, Positionen)  
- Bereichsauswahl zeigt Monitor‑Nummer und Live‑Größe an  
- Vollbild‑Overlay über alle Monitore  

### 🔍 Präzise Bereichsauswahl
- Halbtransparentes Overlay  
- Live‑Anzeige von Breite × Höhe  
- Escape = Abbrechen  
- Enter/Space = Auswahl bestätigen  
- Funktioniert auch bei Multi‑Monitor‑Setups  

### 📸 Screenshot‑Engine
- Bereichsaufnahme mit Monitor‑Offset‑Korrektur  
- Fallback‑Mechanismus, falls `Gdk.pixbuf_get_from_window` fehlschlägt  
- Wayland‑Fallback (sofern möglich)  
- Rückgabe als Pixbuf für den Editor  

---

## 🖌️ Editor‑Funktionen

### Zeichen‑Werkzeuge
- **Linien**  
- **Rechtecke**  
- **Kreise/Ellipsen**  
- **Pfeile**  
- **Text** (mit frei wählbarer Schriftgröße)  
- **Marker**  
- **Freihand‑Malen** (NEU)  
- **Lupe** (Magnifier) mit variabler Vergrößerung  

### Bearbeitungs‑Funktionen
- **Undo / Redo**  
- Farbwahl über ColorButton  
- Variable Liniendicken  
- Zoom (STRG + Mausrad)  
- Zentrierte Darstellung im Editor  
- Export als PNG mit Zeitstempel  
- Kopieren in die Zwischenablage  

---

## 🧰 JSON‑Request‑Modus (Automatisierung)
Der Editor kann im **Request‑Modus** laufen, um automatisiert Screenshots zu erstellen und als JSON zurückzugeben.

Beispiel‑Workflow:
- Tool wird mit Parametern gestartet  
- Screenshot wird automatisch erstellt  
- Editor läuft im Hintergrund  
- JSON‑Antwort enthält Pfad oder Status  

Ideal für:
- Automatisierte Dokumentation  
- CI‑Pipelines  
- Remote‑Support‑Tools  

---

## 📦 Installation

### Voraussetzungen
- Python 3  
- GTK 3 (`python3-gi`)  
- Cairo (`python3-cairo`)  
- GdkPixbuf  
- Optional: Wayland‑Kompatibilität  

### Installation (Debian/Ubuntu/GuideOS)
```bash
sudo apt install python3-gi python3-cairo gir1.2-gtk-3.0
```

### Starten
```bash
python3 guideos-screenshot-editor.py
```

oder ausführbar machen:

```bash
chmod +x guideos-screenshot-editor.py
./guideos-screenshot-editor.py
```

---

## ▶️ Bedienung

### 1. Bereich auswählen  
- Maus ziehen → Auswahl  
- Escape → Abbrechen  
- Enter → Bestätigen  

### 2. Screenshot erscheint im Editor  
- Werkzeuge auswählen  
- Markierungen setzen  
- Undo/Redo nutzen  
- Zoom verwenden  

### 3. Export  
- PNG speichern  
- In Zwischenablage kopieren  
- Im Request‑Modus: JSON‑Antwort  

---

## 🧩 Code‑Struktur

| Komponente | Beschreibung |
|-----------|--------------|
| `ScreenshotEngine` | Bereichsaufnahme, Multi‑Monitor‑Geometrie |
| `AreaSelectorWindow` | Vollbild‑Overlay für Auswahl |
| `EditorWindow` | Haupteditor mit Werkzeugen |
| `Tool` | Werkzeug‑Konstanten |
| Zeichenfunktionen | Linien, Rechtecke, Kreise, Pfeile, Text, Marker, Freihand |
| Undo/Redo | Stapelverwaltung |
| Export | PNG‑Speicherung, Clipboard |

---

## 📄 Lizenz (MIT)

```
MIT License

