

# GuideOS Bildschirmfoto‑Editor

Ein erweiterter Screenshot‑Editor für Linux mit Multi‑Monitor‑Support, präziser Bereichsauswahl, umfangreichen Zeichen‑ und Markierungswerkzeugen sowie Export‑ und JSON‑Request‑Modus. Entwickelt von **evilware666 & Helga**.

# Entwickler: 
evilware666 & Helga

# Version:
2.0
---

## ✨ Funktionen

- **Multi‑Monitor‑Screenshot** (X11) mit exakter Bereichsauswahl  
- **Wayland‑Fallback** (falls Root‑Window nicht verfügbar)  
- **Lupenwerkzeug** mit variabler Vergrößerung  
- **Annotationen:**  
  - Linien, Rechtecke, Kreise  
  - Pfeile  
  - Text (variable Schriftgrößen)  
  - Marker  
  - Freihand  
  - **Pixelierung** (Blockgröße einstellbar)  
- **Undo/Redo‑System**  
- **Farbwahl & Liniendicken**  
- **Zoom (CTRL + Mausrad)**  
- **PNG‑Export & Zwischenablage‑Kopie**  
- **JSON‑Request‑Modus** für automatisierte Workflows  
- Automatische **Theme‑Erkennung** (Hell/Dunkel)

---

## 📦 Abhängigkeiten

- Python 3  
- GTK 3 (`python3-gi`, `gir1.2-gtk-3.0`)  
- Cairo  
- GdkPixbuf  
- GLib  
- Pango  

---

## 🚀 Starten

### Bereich auswählen & Editor öffnen
```bash
guideos-bildschirmfoto-editor.py
```

### Direkt mit JSON‑Request‑Modus
```bash
guideos-bildschirmfoto-editor --json
```

---

## 💾 Export

- Speichern als **PNG**
- Kopieren in die **Zwischenablage**
- Ausgabe im JSON‑Modus:
```json
{ "status": "ok", "file": "/pfad/zum/export.png" }
```

---

## 🖼️ Bedienung

- **Linksklick & Ziehen:** Bereich auswählen / Formen zeichnen  
- **Rechtsklick:** Abbrechen  
- **CTRL + Mausrad:** Zoom  
- **Werkzeugleiste:** Auswahl aller Tools & Einstellungen  

---

## 📚 Lizenz

**MIT License**

