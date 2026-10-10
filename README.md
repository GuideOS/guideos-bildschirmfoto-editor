
## Hier die korrigierte README für 3.1.3

```markdown
# GuideOS Bildschirmfoto-Editor

Der **GuideOS Bildschirmfoto-Editor** ist ein eigenständiges Python-Programm
auf Basis von **GTK 4** und **libadwaita**. Es kombiniert eine flexible
Aufnahmefunktion (Bereich, Vollbild, aktives Fenster) mit einem vollwertigen
Bildeditor zum Markieren, Kommentieren und Bearbeiten von Screenshots – ganz
ohne externe Bildbearbeitungssoftware.

- **Version:** 3.1.2
- **Entwickler:** evilware666 & Helga
- **Lizenz:** GPLv.3 

---

## Funktionen

### Aufnahme
- **Bereichsauswahl** – freies Aufziehen mit der Maus, live Anzeige der
  Abmessungen, Auswahl wird beim Loslassen automatisch übernommen
- **Ganzer Bildschirm** – alle Monitore in einem Bild
- **Aktives Fenster** – das gerade fokussierte Fenster (via `xdotool`)
- **Timer** – Sofort / 3 s / 5 s / 10 s Verzögerung mit grafischem
  Countdown-Overlay
- **HiDPI-fähig** – automatische Umrechnung logischer → physischer Pixel
- **Transparentes Overlay** – Desktop scheint durch, nur Abdunklung und
  Rahmen werden gezeichnet

### Editor
- **Zehn Zeichenwerkzeuge:** Auswahl, Linie, Rechteck, Kreis, Pfeil, Text,
  Marker, Freihand, Verpixeln, Lupe
- **Auswahl & Verschieben** – Elemente anklicken, verschieben, löschen
- **Undo / Redo** – mehrstufige Rückgängig-Funktion
- **Auto-Zoom** – kleine Auswahlen (< 300 px) starten bei 100 %
- **Zoom** – feines Zoomen per `Strg + Mausrad` (multiplikativ, 8 %/Klick)

### Ausgabe
- **Speichern** als PNG mit wählbarem Speicherordner (Standard `~/Bilder`)
- **Zwischenablage** – Bild direkt in die Zwischenablage kopieren
- **Öffnen mit…** – direkte Weitergabe an installierte Bildprogramme
  (GIMP, Krita, Pinta, Inkscape, …) mit automatischer Icon-Erkennung
- **Letztes Programm merken** – bevorzugtes Zielprogramm wird gespeichert

### Bedienung
- **Adwaita-Design** – moderne GNOME-typische Optik
- **Menü** in beiden Fenstern für Ordner und Info
- **Beenden-Button** in Start- und Editorfenster
- **Werkzeugeinstellungen persistent** – Farbe, Größen, Zoom bleiben erhalten

---

## Systemanforderungen

| Komponente | Anforderung |
|---|---|
| Betriebssystem | Linux mit **X11-Session** (Cinnamon, MATE, XFCE, GNOME-X11, …) |
| Python | 3.6 oder neuer |
| GTK | **4.0** (`python3-gi`, `gir1.2-gtk-4.0`) |
| libadwaita | (`gir1.2-adw-1`) |
| Cairo | `python3-cairo` |
| Bildverarbeitung | `gir1.2-gdkpixbuf-2.0` |
| Optional | `xdotool`, `imagemagick` |

> **Wichtig:** Das Programm benötigt zwingend eine **X11-Sitzung**. Unter
> Wayland ist die Aufnahme technisch nicht möglich (ImageMagick `import`
> und `xdotool` setzen X11 voraus). Bitte beim Login eine X11-Session
> wählen („Cinnamon (X11)", „GNOME unter Xorg", …).

---

## Installation

### 1. Systempakete installieren

```bash
sudo apt update
sudo apt install python3-gi python3-gi-cairo python3-cairo \
                 gir1.2-gtk-4.0 gir1.2-adw-1 gir1.2-gdkpixbuf-2.0 \
                 xdotool imagemagick
```

### 2. Programm herunterladen

Speichere das Skript als `guideos-screenshot-editor.py` in einem Verzeichnis
deiner Wahl.

### 3. Ausführbar machen

```bash
chmod +x guideos-screenshot-editor.py
```

### 4. Starten

```bash
./guideos-screenshot-editor.py
```

Optional: Ein Desktop-Eintrag unter
`~/.local/share/applications/guideos-screenshot-editor.desktop` mit
passendem Icon, damit das Programm im Startmenü erscheint.

---

## Verwendung

Beim Start öffnet sich das **Modi-Fenster** mit drei Aufnahmeoptionen:

| Option | Beschreibung |
|---|---|
| **Bereich auswählen** | Maus aufziehen, um einen Bereich zu erfassen – Auswahl wird beim Loslassen übernommen |
| **Ganzer Bildschirm** | Alle Monitore zusammen aufnehmen |
| **Aktives Fenster** | Das gerade fokussierte Fenster erfassen |

Zusätzlich kann ein **Timer** (Sofort / 3 s / 5 s / 10 s) voreingestellt
werden. Nach jeder Aufnahme springt der Timer automatisch auf „Sofort" zurück.

Nach der Aufnahme öffnet sich der **Editor**. Dort kannst du das Bild
bearbeiten, speichern, in die Zwischenablage kopieren oder direkt an ein
externes Programm übergeben.

---

## Tastenkürzel & Maussteuerung

### Aufnahme
| Aktion | Taste / Maus |
|---|---|
| Bereich aufziehen | Linke Maustaste gedrückt halten |
| Auswahl übernehmen | **automatisch beim Loslassen** |
| Auswahl abbrechen | `ESC` |

### Editor
| Aktion | Taste / Maus |
|---|---|
| Zoomen | `Strg` + Mausrad |
| Element auswählen | Klick mit Auswahl-Werkzeug |
| Element verschieben | Linke Maustaste gedrückt halten |
| Element löschen | `Entf` / `Backspace` |
| Auswahl aufheben | `ESC` |

---

## Werkzeuge im Detail

| Werkzeug | Symbol | Beschreibung |
|---|---|---|
| **Auswahl** | ✛ | Elemente anklicken, verschieben, löschen |
| **Linie** | ╱ | Gerade Linie in wählbarer Strichstärke |
| **Rechteck** | ▢ | Rahmen-Rechteck, Strichstärke einstellbar |
| **Kreis** | ◯ | Ellipse / Kreis als Rahmen |
| **Pfeil** | ➤ | Pfeil mit Spitze in Zugrichtung |
| **Text** | Aa | Text mit einstellbarer Schriftgröße |
| **Lupe** | 🔍 | Vergrößerter Ausschnitt als Overlay (1,5×–5,0×) |
| **Marker** | ▬ | Halbtransparenter Textmarker-Effekt (40 % Alpha) |
| **Freihand** | ✎ | Freies Malen mit Glättung |
| **Verpixeln** | ▦ | Bereich unkenntlich machen (Pixelgröße wählbar) |

**Verfügbare Farben:** frei wählbar per Adwaita-Farbwähler.

---

## Konfiguration

Alle Einstellungen werden in folgender Datei gespeichert:

```
~/.config/guideos-screenshot-editor.json
```

Enthaltene Werte:

| Schlüssel | Bedeutung |
|---|---|
| `tool_color` | Zuletzt gewählte Farbe (RGBA) |
| `tool_line_width` | Strichstärke in px |
| `tool_text_size` | Schriftgröße in pt |
| `tool_magnifier_scale` | Lupenvergrößerung |
| `tool_pixel_size` | Pixelgröße für Verpixeln |
| `tool_zoom_level` | Zoomstufe im Editor |
| `save_folder` | Standard-Speicherordner für Screenshots |
| `timer_delay` | Zuletzt gewählter Timer (0, 3, 5, 10) |
| `default_app` / `default_app_name` | Zuletzt verwendetes externes Programm |

Die Datei kann gelöscht werden, um alle Einstellungen zurückzusetzen.
Beim ersten Start wird automatisch `~/Bilder` (oder `~/Pictures`) als
Speicherordner verwendet.

---

## Kompatibilität

| Umgebung | Status |
|---|---|
| Cinnamon (X11) | ✅ Vollständig getestet |
| MATE, XFCE | ✅ Erwartungsgemäß funktionsfähig |
| GNOME (X11) | ✅ Funktioniert |
| Multi-Monitor-Setups | ✅ Unterstützt |
| HiDPI-Displays | ✅ Automatische Skalierung |

> Wayland wird **nicht** unterstützt. Das Programm benötigt eine
> X11-Session.

---

## Bekannte Einschränkungen

- **X11 erforderlich:** Unter Wayland funktioniert die Aufnahme nicht,
  weil ImageMagick `import` und `xdotool` X11 voraussetzen.
- **Timer + Bereichsauswahl:** Der Timer startet nach der Auswahl, nicht
  davor.
- **Verzögerung nach Aufnahmeklick:** 450–650 ms, damit das Start-Fenster
  vollständig ausgeblendet ist. Das ist Absicht, um saubere Aufnahmen zu
  garantieren.
- **Sehr große Screenshots** (4K-Vollbild) können bei schwacher Hardware
  kurze Verzögerungen beim Öffnen verursachen.


