# README.md  
# Titel       : GuideOS Bildschirmfoto-Editor
# Beschreibung: Erweiterte Version des GuideOS Screenshot-Tools mit vollständiger
#               Multi-Monitor-Unterstützung, präziser Bereichsauswahl, Wayland-
#               Fallback, Monitor-Erkennung, Lupenwerkzeug, Annotationen (Linien,
#               Rechtecke, Kreise, Pfeile, Text), Undo/Redo, Farbwahl, variablen
#               Liniendicken, Textgrößen und PNG-Export. Unterstützt sowohl den
#               normalen Modus als auch einen JSON-basierten Request-Modus für
#               automatisierte Abläufe.
#
# Autor       : evilware666 & Helga
# Version     : 1.2
# Datum       : 22.12.2025
# Lizenz      : MIT

---

## ✨ Hauptfunktionen

### 🖼️ Screenshot‑Engine
- Multi‑Monitor‑Erkennung mit korrekter Geometrie  
- Bereichsauswahl mit Live‑Größenanzeige  
- Monitor‑Info bei Multi‑Monitor‑Screenshots  
- Wayland‑Fallback (falls `Gdk.pixbuf_get_from_window` fehlschlägt)  
- Monitor‑Offsets werden korrekt berücksichtigt  
- Auswahlfenster mit halbtransparentem Overlay

### 🖊️ Editor‑Funktionen
- Werkzeuge:
  - Linie  
  - Rechteck  
  - Ellipse  
  - Pfeil  
  - Text  
  - Marker  
  - Lupe (Magnifier)  
- Undo/Redo  
- Farbwahl  
- Variable Liniendicken  
- Variable Textgrößen  
- Vergrößerungsfaktor für Lupe einstellbar  
- Zoomfunktion (Strg + Mausrad)  
- Zentrierte Werkzeugleiste  
- Cinnamon‑kompatibles CSS‑Styling (#2573bf)

### 💾 Export & Automatisierung
- PNG‑Export mit Zeitstempel  
- Dateidialog für benutzerdefinierten Speicherort  
- JSON‑Request‑Modus:
  - Startbar mit JSON‑Input  
  - Gibt nach Bearbeitung JSON‑Output zurück  
  - Ideal für Dokumentation, Support‑Tools, Automatisierung

---

## 📦 Installation

### Voraussetzungen
- Python 3  
- GTK3 + GObject Introspection  
- Cairo  
- Pango  

### Benötigte Pakete (Debian/Ubuntu)
```bash
sudo apt install python3-gi python3-cairo gir1.2-gtk-3.0 gir1.2-pango-1.0
```

### Starten
```bash
python3 screenshot_editor.py
```

---

## ▶️ Bedienung

### Bereichsauswahl
1. Programm starten  
2. Auswahlfenster erscheint im Vollbild  
3. Mit der Maus einen Bereich ziehen  
4. Größe wird live angezeigt  
5. Enter → Auswahl bestätigen  
6. Escape → Abbrechen  

### Editor
- Werkzeugleiste ist zentriert unter dem Screenshot  
- Werkzeuge per Klick aktivieren  
- Zeichnen durch Klicken & Ziehen  
- Text durch Klick setzen  
- Lupe durch Ziehen bewegen  
- Zoom mit **Strg + Mausrad**  
- Speichern über den Header‑Button  

---

## 🧩 Code‑Struktur

| Komponente | Beschreibung |
|-----------|--------------|
| `ScreenshotEngine` | Screenshot‑Erfassung, Monitor‑Infos |
| `AreaSelectorWindow` | Vollbild‑Auswahlfenster |
| `Tool` | Werkzeug‑Konstanten |
| `EditorWindow` | Haupteditor mit Werkzeugleiste |
| Cairo‑Zeichenlogik | Rendering von Formen, Text, Lupe |
| JSON‑Modus | Automatisierte Screenshot‑Workflows |

---

## 🛠️ Technologien
- **GTK3** (UI)  
- **GdkPixbuf** (Screenshots)  
- **Cairo** (Zeichnen)  
- **Pango** (Text)  
- **JSON** (Request‑Modus)  

---

## 📄 Lizenz
Dieses Projekt steht unter der **MIT‑Lizenz**.
