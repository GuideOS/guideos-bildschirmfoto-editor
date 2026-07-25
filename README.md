
# GuideOS Bildschirmfoto‑Editor  
**Version 2.2 – 26.07.2026**  
Erweiterter Screenshot‑Editor für Linux (GTK3), optimiert für Cinnamon, X11 und Multi‑Monitor‑Setups.

## ✨ Funktionen
Der Editor bietet eine umfangreiche Werkzeugpalette für professionelle und schnelle Bildschirmbearbeitung:

## Entwickler(in)
evilware666 & Helga

### 📸 Screenshot‑Erfassung
- **Ganzer Bildschirm** (alle Monitore)
- **Aktives Fenster**  
  - via `xdotool`  
  - Fallback über `wmctrl`  
  - letzter Fallback: Vollbild
- **Bereich auswählen**  
  - Multi‑Monitor‑fähig  
  - Live‑Overlay mit Größenanzeige  
  - Monitor‑Erkennung

### 🖊️ Zeichen‑ & Bearbeitungswerkzeuge
- Linien  
- Rechtecke  
- Ellipsen  
- Pfeile  
- Text  
- Marker  
- Freihand  
- Pixelierung (variable Blockgröße)  
- Lupenwerkzeug (variable Vergrößerung)

### 🎨 Editor‑Features
- Undo / Redo  
- Farbwahl  
- Variable Liniendicke  
- Variable Textgröße  
- Zoom (mit STRG + Mausrad)  
- PNG‑Export  
- Zwischenablage‑Export  
- **„Öffnen mit…“**  
  - erkennt installierte Bildprogramme  
  - speichert bevorzugte App  
  - lädt Icons automatisch

### 🖥️ Theme‑Erkennung
Automatische Anpassung an das System‑Theme:
- Cinnamon‑Theme  
- GTK‑Theme  
- Dark/Light‑Modus  
- Eigene Farbschemata für Buttons, Comboboxes, Headerbar

### 🧩 GTK4/Adwaita‑Style für GTK3
Version 2.2 bringt ein neues, modernes Styling:
- aktive Comboboxen in Akzentfarbe  
- ToggleButtons im Adwaita‑Stil  
- Hover‑Effekte  
- klare Akzentfarben  
- konsistente Farbpalette für Dark/Light

---

## 🆕 Neuerungen in Version 2.2
### 🔥 **Neue Screenshot‑Modi**
- **Ganzer Bildschirm**  
- **Aktives Fenster** (xdotool → wmctrl → Fallback)
- **Bereich auswählen** über Multi‑Monitor‑Overlay

### 🎨 **Modernisiertes UI**
- Vollständiges CSS‑Upgrade auf GTK4/Adwaita‑Look  
- Aktive Comboboxen farbig hinterlegt  
- ToggleButtons im modernen Stil  
- Verbesserte Hover‑ und Active‑Zustände  
- Einheitliche Akzentfarbe

### 🖼️ **Verbesserte „Öffnen mit…“-Funktion**
- erkennt mehr Programme  
- lädt Icons aus `.desktop`‑Dateien  
- speichert bevorzugte App dauerhaft

### 🧭 **Multi‑Monitor‑Verbesserungen**
- exakte Monitor‑Erkennung  
- Bereichsauswahl über alle Displays  
- Anzeige des Monitornamens im Overlay

### 🧰 **Stabilitäts‑Fixes**
- Cairo‑Bridge‑Fix (`python3-gi-cairo`)  
- robustere Fallbacks bei fehlenden Tools  
- Fehlerbehandlung für Screenshots ohne Root‑Window

---

## 📦 Abhängigkeiten
### Pflicht:
- `python3`
- `python3-gi`
- `python3-gi-cairo`
- `gir1.2-gtk-3.0`
- `gir1.2-gdkpixbuf-2.0`

### Optional (für aktive Fenster):
- `xdotool`
- `wmctrl`

---

## 🚀 Starten
```bash
python3 guideos-screenshot-editor.py
```

---

## 🖼️ Bedienung
### Screenshot erstellen
1. Editor starten  
2. Modus wählen:  
   - Vollbild  
   - Aktives Fenster  
   - Bereich auswählen  
3. Screenshot erscheint direkt im Editor

### Werkzeuge aktivieren
Einfach auf das jeweilige Icon klicken.

### Speichern
- PNG  
- Zwischenablage  
- „Öffnen mit…“ → direkt in GIMP, Krita, Pinta usw.

---

## 🛠️ Code‑Struktur
- `ScreenshotEngine`  
- `AreaSelectorWindow`  
- `EditorWindow`  
- Theme‑Erkennung  
- App‑Icon‑Erkennung  
- Werkzeug‑Rendering (Cairo)

---

## 📄 Lizenz
MIT License  
© 2026 evilware666 & Helga

