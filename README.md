# guideos-bildschirmfoto-editor[README.md](https://github.com/user-attachments/files/24281242/README.md)


## Übersicht
Der **GuideOS Bildschirmfoto-Editor** ist ein vollständiges Screenshot- und Annotierungswerkzeug für GuideOS und Cinnamon-basierte Systeme.  
Er kombiniert eine präzise Bereichsauswahl mit einem leistungsfähigen Editor, der Linien, Rechtecke, Ellipsen, Pfeile und Text unterstützt.  
Das Tool ist vollständig GTK-basiert und bietet Undo/Redo, Farbauswahl, Liniendicke, Zwischenablage,Textgröße sowie einen modernen Cinnamon-Look.

- **Autor:** evilware666 & Helga  
- **Version:** 1.6  
- **Letzte Änderung:** 29.01.2026  
- **Lizenz:** Frei nutzbar im Rahmen von GuideOS  

---

## Funktionen

### Bereichsauswahl
- Halbtransparente Overlay-Auswahl  
- Live-Anzeige der Auswahlgröße  
- ESC zum Abbrechen  
- Enter/Space zum Bestätigen  

### Screenshot-Engine
- Aufnahme eines beliebigen Bildschirmbereichs  
- Fallback für Wayland (Vollbild → Subpixbuf)  

### Editor
- Werkzeuge:
  - Linie  
  - Rechteck  
  - Ellipse  
  - Pfeil  
  - Text  
- Undo/Redo  
- Farbauswahl  
- Liniendicke einstellbar  
- Textgröße einstellbar  
- Cinnamon-kompatible Icons und CSS  
- Scrollbarer Arbeitsbereich  
- Speichern als PNG mit Zeitstempel  

### Startfenster
- Minimalistische GUI  
- Button „Bereich auswählen“  
- Info-Hinweis  

### Request-Modus
- Startbar mit `--request`  
- Gibt JSON zurück (für Integrationen in andere Tools)

### Zwischenablage
- Jetzt können Bilder auch in die Zwischenablage kopiert werden

---

## Abhängigkeiten
- `python3-gi`  
- `gir1.2-gtk-3.0`  
- `gir1.2-gdk-3.0`  
- `gir1.2-pangocairo-1.0`  
- `python3-cairo`  

Installation (Debian/Ubuntu):
```bash
sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-gdk-3.0 gir1.2-pangocairo-1.0 python3-cairo

