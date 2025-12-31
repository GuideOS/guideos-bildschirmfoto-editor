#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# Titel       : GuideOS Screenshot- & Editor-Tool
# Beschreibung: Umfangreiches GTK-basiertes Screenshot-Werkzeug für GuideOS.
#               Ermöglicht die Auswahl eines beliebigen Bildschirmbereichs,
#               erstellt präzise Screenshots (inkl. Wayland-Fallback) und bietet
#               anschließend einen vollwertigen Editor zum Annotieren. Unterstützt
#               Linien, Rechtecke, Ellipsen, Pfeile, Text, Farbwahl, Undo/Redo,
#               variable Liniendicken, Textgrößen und PNG-Export. Optionaler
#               Request-Modus für automatisierte Abläufe.
#
# Autor       : evilware666 & Helga
# Version     : 1.0
# Datum       : 21.12.2025
# Lizenz      : MIT
# ==============================================================================
#
# Hinweis     : - Bereichsauswahl mit Live-Overlay und Größenanzeige.
#               - Editor mit Werkzeugleiste, Cinnamon-kompatiblen Icons und
#                 zentrierter Toolbar.
#               - Unterstützt Undo/Redo, Farbauswahl, Text-Popup, Pfeilwerkzeug
#                 und skalierbare Formen.
#               - PNG-Export mit Zeitstempel und Dateidialog.
#               - Request-Modus gibt JSON zurück (für Automatisierung).
#               - Ideal für Dokumentation, Support, Tutorials und schnelle Markups.
#
# -------------------------------------------------------

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, Pango

import cairo
import math
import json
import sys
import os
from datetime import datetime


# ===================== Screenshot-Engine =====================

class ScreenshotEngine:
    @staticmethod
    def capture_area(x, y, width, height):
        """Nimmt einen Bereich des Bildschirms auf"""
        root = Gdk.get_default_root_window()
        if not root:
            print("Kein Root-Window gefunden")
            return None
        
        pb = Gdk.pixbuf_get_from_window(root, int(x), int(y), int(width), int(height))

        # Fallback für Wayland
        if pb is None:
            try:
                full_width = root.get_width()
                full_height = root.get_height()
                full_pb = Gdk.pixbuf_get_from_window(root, 0, 0, full_width, full_height)
                if full_pb:
                    pb = full_pb.new_subpixbuf(int(x), int(y), int(width), int(height))
            except:
                print("Fehler bei Screenshot")
        
        return pb


# ===================== Bereichsauswahl-Fenster =====================

class AreaSelectorWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Bereich auswählen")
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        self.fullscreen()

        self.start_x = 0
        self.start_y = 0
        self.cur_x = 0
        self.cur_y = 0
        self.selecting = False
        self.finished = False
        self.result_rect = None

        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.KEY_PRESS_MASK
        )

        self.connect("draw", self.on_draw)
        self.connect("button-press-event", self.on_button_press)
        self.connect("button-release-event", self.on_button_release)
        self.connect("motion-notify-event", self.on_mouse_move)
        self.connect("key-press-event", self.on_key_press)

    def on_draw(self, widget, cr):
        alloc = self.get_allocation()
        cr.set_source_rgba(0, 0, 0, 0.4)
        cr.rectangle(0, 0, alloc.width, alloc.height)
        cr.fill()

        if self.selecting or (self.finished and self.result_rect):
            if self.selecting:
                x1, y1 = self.start_x, self.start_y
                x2, y2 = self.cur_x, self.cur_y
            else:
                x1, y1, w, h = self.result_rect
                x2, y2 = x1 + w, y1 + h

            x = min(x1, x2)
            y = min(y1, y2)
            w = abs(x2 - x1)
            h = abs(y2 - y1)

            # Helles Rechteck für Auswahl
            cr.set_source_rgba(1, 1, 1, 0.1)
            cr.rectangle(x, y, w, h)
            cr.fill()

            # Rahmen
            cr.set_source_rgba(1, 1, 1, 0.8)
            cr.set_line_width(2)
            cr.rectangle(x, y, w, h)
            cr.stroke()

            # Größe anzeigen
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(14)
            text = f"{int(w)} × {int(h)}"
            extents = cr.text_extents(text)
            
            # Hintergrund für Text
            text_x = x + 10
            text_y = y + 25
            cr.set_source_rgba(0, 0, 0, 0.7)
            cr.rectangle(text_x - 5, text_y - extents.height - 5, 
                        extents.width + 10, extents.height + 10)
            cr.fill()
            
            # Text
            cr.set_source_rgba(1, 1, 1, 1)
            cr.move_to(text_x, text_y)
            cr.show_text(text)

    def on_button_press(self, widget, event):
        if event.button == 1:
            self.start_x = event.x
            self.start_y = event.y
            self.cur_x = event.x
            self.cur_y = event.y
            self.selecting = True
            self.queue_draw()

    def on_mouse_move(self, widget, event):
        if self.selecting:
            self.cur_x = event.x
            self.cur_y = event.y
            self.queue_draw()

    def on_button_release(self, widget, event):
        if event.button == 1 and self.selecting:
            self.selecting = False
            x1, y1 = self.start_x, self.start_y
            x2, y2 = event.x, event.y

            x = min(x1, x2)
            y = min(y1, y2)
            w = abs(x2 - x1)
            h = abs(y2 - y1)

            if w > 10 and h > 10:  # Minimale Größe
                self.result_rect = (x, y, w, h)
            self.finished = True

    def on_key_press(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == "Escape":
            self.result_rect = None
            self.finished = True
        elif keyname == "Return" or keyname == "space":
            self.finished = True

    def run(self):
        self.show_all()
        self.grab_add()
        self.grab_focus()
        
        while not self.finished:
            while Gtk.events_pending():
                Gtk.main_iteration_do(False)

        self.grab_remove()
        rect = self.result_rect
        self.destroy()
        return rect


# ===================== Tool-Konstanten =====================

class Tool:
    LINE = "line"
    RECT = "rect"
    ELLIPSE = "ellipse"
    ARROW = "arrow"
    TEXT = "text"


# ===================== Editor-Fenster =====================

class EditorWindow(Gtk.Window):
    def __init__(self, image_pixbuf, request_mode=False):
        super().__init__(title="GuideOS Bildschirmfoto-Editor")
        self.set_border_width(10)
        self.set_default_icon_name("applets-screenshooter")
        self.request_mode = request_mode

        # CSS für Cinnamon-Integration mit Farbe #2573bf
        css_provider = Gtk.CssProvider()
        css = """
        .tool-button {
            border-radius: 4px;
            padding: 6px 12px;
        }
        .tool-button:checked,
        .tool-button:active {
            background-color: #2573bf;
            color: white;
        }
        .tool-button:hover {
            background-color: alpha(#2573bf, 0.1);
        }
        .suggested-action {
            background-color: #2573bf;
            color: white;
        }
        .suggested-action:hover {
            background-color: #1a5a9c;
        }
        .combobox arrow {
            color: #2573bf;
        }
        .color-button {
            color: #2573bf;
        }
        """
        css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.current_tool = Tool.LINE
        self.shapes = []
        self.undo_stack = []
        self.redo_stack = []
        self.drawing = False
        self.start_x = 0
        self.start_y = 0
        self.current_x = 0
        self.current_y = 0
        # Farbe #2573bf in RGB (37/115/191)
        self.current_color = (0.1451, 0.4510, 0.7490, 1.0)
        self.current_line_width = 3.0
        self.current_text_size = 24.0
        
        # Neue Attribute für Werkzeugleiste
        self.font_sizes = [12, 14, 16, 18, 20, 24, 28, 32, 36, 48]
        self.line_widths = [1, 2, 3, 4, 5, 6, 8, 10]

        self.background_pixbuf = image_pixbuf
        self.background_surface = self.pixbuf_to_surface(image_pixbuf)

        width = self.background_surface.get_width()
        height = self.background_surface.get_height()
        self.set_default_size(min(width, 800), min(height + 150, 950))

        main_box = Gtk.VBox(spacing=0)
        self.add(main_box)

        # HeaderBar für Cinnamon-Integration
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.set_title("GuideOS Bildschirmfoto-Editor")
        self.set_titlebar(header_bar)

        # Zeichenbereich
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(width, height)
        self.drawing_area.connect("draw", self.on_draw)
        self.drawing_area.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
        )
        self.drawing_area.connect("button-press-event", self.on_button_press)
        self.drawing_area.connect("button-release-event", self.on_button_release)
        self.drawing_area.connect("motion-notify-event", self.on_mouse_move)
        
        # Scroll-Fenster für große Bilder
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_shadow_type(Gtk.ShadowType.IN)
        scrolled.add(self.drawing_area)
        main_box.pack_start(scrolled, True, True, 0)

        # Container für zentrierte Werkzeugleiste
        toolbar_container = Gtk.HBox()
        toolbar_container.set_border_width(5)
        main_box.pack_start(toolbar_container, False, False, 0)

        # Linker Platzhalter für Zentrierung
        left_spacer = Gtk.Label("")
        left_spacer.set_hexpand(True)
        toolbar_container.pack_start(left_spacer, True, True, 0)

        # Werkzeugleiste (horizontal)
        toolbar = Gtk.HBox(spacing=5)
        toolbar_container.pack_start(toolbar, False, False, 0)

        # Rechter Platzhalter für Zentrierung
        right_spacer = Gtk.Label("")
        right_spacer.set_hexpand(True)
        toolbar_container.pack_start(right_spacer, True, True, 0)

        # Werkzeug-Buttons
        tool_group = []
        
        def create_tool_button(icon_name, label, tool_id=None):
            if tool_id:
                btn = Gtk.ToggleButton()
                btn.set_tooltip_text(label)
                if tool_id == Tool.LINE:
                    btn.set_active(True)
                btn.connect("toggled", self.on_tool_toggled, tool_id)
                tool_group.append(btn)
            else:
                btn = Gtk.Button()
            
            # Icons für Cinnamon (Mint/Adwaita)
            try:
                icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
                btn.add(icon)
            except:
                # Fallback auf Text-Label
                btn = Gtk.Button(label=label[:3])
                if tool_id:
                    btn.connect("toggled", self.on_tool_toggled, tool_id)
                return btn
            
            btn.get_style_context().add_class("tool-button")
            return btn

        # Werkzeuge mit Cinnamon-kompatiblen Icons
        line_btn = create_tool_button("draw-line", "Linie", Tool.LINE)
        rect_btn = create_tool_button("gtk-justify-fill", "Rechteck", Tool.RECT)
        ellipse_btn = create_tool_button("radio-checked", "Ellipse", Tool.ELLIPSE)
        arrow_btn = create_tool_button("go-next", "Pfeil", Tool.ARROW)
        text_btn = create_tool_button("gtk-edit", "Text", Tool.TEXT)
        
        # Farbauswahl
        color_btn = Gtk.ColorButton()
        color_btn.set_rgba(Gdk.RGBA(*self.current_color))
        color_btn.set_tooltip_text("Farbe")
        color_btn.connect("color-set", self.on_color_set)
        color_btn.get_style_context().add_class("color-button")
        
        # Undo/Redo
        undo_btn = create_tool_button("edit-undo", "Rückgängig", None)
        undo_btn.connect("clicked", self.on_undo_clicked)
        
        redo_btn = create_tool_button("edit-redo", "Wiederholen", None)
        redo_btn.connect("clicked", self.on_redo_clicked)
        
        # Liniendicke
        linewidth_combo = Gtk.ComboBoxText()
        linewidth_combo.set_tooltip_text("Liniendicke")
        for w in self.line_widths:
            linewidth_combo.append_text(f"{w} px")
        linewidth_combo.set_active(2)  # 3px
        linewidth_combo.connect("changed", self.on_linewidth_changed)
        linewidth_combo.get_style_context().add_class("combobox")
        
        # Textgröße
        textsize_combo = Gtk.ComboBoxText()
        textsize_combo.set_tooltip_text("Textgröße")
        for s in self.font_sizes:
            textsize_combo.append_text(f"{s} pt")
        textsize_combo.set_active(5)  # 24pt
        textsize_combo.connect("changed", self.on_textsize_changed)
        textsize_combo.get_style_context().add_class("combobox")
        
        # Speichern-Button in HeaderBar
        save_btn = Gtk.Button.new_with_label("Speichern")
        save_btn.get_style_context().add_class("suggested-action")
        save_btn.connect("clicked", self.on_save_clicked)
        header_bar.pack_end(save_btn)
        
        # Abbrechen-Button in HeaderBar (nur im Request-Modus)
        if self.request_mode:
            cancel_btn = Gtk.Button.new_with_label("Abbrechen")
            cancel_btn.connect("clicked", lambda w: self.on_cancel_clicked())
            header_bar.pack_start(cancel_btn)
        else:
            # Im normalen Modus: Info-Button
            info_btn = Gtk.Button.new_with_label("Info")
            info_btn.connect("clicked", lambda w: self.show_info())
            header_bar.pack_start(info_btn)

        # Werkzeuge zur Toolbar hinzufügen
        for btn in [line_btn, rect_btn, ellipse_btn, arrow_btn, text_btn,
                   Gtk.SeparatorToolItem(), color_btn, 
                   Gtk.SeparatorToolItem(), undo_btn, redo_btn,
                   Gtk.SeparatorToolItem(), linewidth_combo,
                   Gtk.SeparatorToolItem(), textsize_combo]:
            if isinstance(btn, Gtk.Widget):
                if isinstance(btn, (Gtk.Button, Gtk.ComboBoxText, Gtk.ToggleButton, Gtk.ColorButton)):
                    container = Gtk.ToolItem()
                    container.add(btn)
                    toolbar.add(container)
                else:
                    toolbar.add(btn)

        # Tool-Button Gruppe setzen
        self.tool_group = tool_group

    def pixbuf_to_surface(self, pixbuf):
        width = pixbuf.get_width()
        height = pixbuf.get_height()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        cr = cairo.Context(surface)
        Gdk.cairo_set_source_pixbuf(cr, pixbuf, 0, 0)
        cr.paint()
        return surface

    # ------------------- Zeichnen -------------------

    def on_draw(self, widget, cr):
        cr.set_source_surface(self.background_surface, 0, 0)
        cr.paint()

        for s in self.shapes:
            self.draw_shape(cr, s)

        if self.drawing and self.current_tool != Tool.TEXT:
            temp = self.make_shape(
                self.current_tool,
                self.start_x,
                self.start_y,
                self.current_x,
                self.current_y,
            )
            self.draw_shape(cr, temp)

    def make_shape(self, tool, x1, y1, x2, y2, text=None):
        return {
            "type": tool,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "color": self.current_color,
            "width": self.current_line_width,
            "text": text,
            "text_size": self.current_text_size,
        }

    def draw_shape(self, cr, s):
        cr.set_source_rgba(*s["color"])
        cr.set_line_width(s["width"])

        if s["type"] == Tool.LINE:
            cr.move_to(s["x1"], s["y1"])
            cr.line_to(s["x2"], s["y2"])
            cr.stroke()

        elif s["type"] == Tool.RECT:
            x = min(s["x1"], s["x2"])
            y = min(s["y1"], s["y2"])
            w = abs(s["x2"] - s["x1"])
            h = abs(s["y2"] - s["y1"])
            cr.rectangle(x, y, w, h)
            cr.stroke()

        elif s["type"] == Tool.ELLIPSE:
            x = (s["x1"] + s["x2"]) / 2
            y = (s["y1"] + s["y2"]) / 2
            rx = abs(s["x2"] - s["x1"]) / 2
            ry = abs(s["y2"] - s["y1"]) / 2
            cr.save()
            cr.translate(x, y)
            cr.scale(rx, ry)
            cr.arc(0, 0, 1, 0, 2 * math.pi)
            cr.restore()
            cr.stroke()

        elif s["type"] == Tool.ARROW:
            self.draw_arrow(cr, s["x1"], s["y1"], s["x2"], s["y2"])

        elif s["type"] == Tool.TEXT and s["text"]:
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            cr.set_font_size(s["text_size"])
            cr.move_to(s["x1"], s["y1"])
            cr.show_text(s["text"])
            cr.stroke()

    def draw_arrow(self, cr, x1, y1, x2, y2):
        cr.move_to(x1, y1)
        cr.line_to(x2, y2)
        cr.stroke()

        angle = math.atan2(y2 - y1, x2 - x1)
        length = 12 + self.current_line_width
        a1 = angle + math.pi / 6
        a2 = angle - math.pi / 6

        cr.move_to(x2, y2)
        cr.line_to(x2 - length * math.cos(a1), y2 - length * math.sin(a1))
        cr.move_to(x2, y2)
        cr.line_to(x2 - length * math.cos(a2), y2 - length * math.sin(a2))
        cr.stroke()

    # ------------------- Maus -------------------

    def on_button_press(self, widget, event):
        if event.button == 1:
            if self.current_tool == Tool.TEXT:
                self.show_text_popup(event.x, event.y)
                return

            self.drawing = True
            self.start_x = event.x
            self.start_y = event.y
            self.current_x = event.x
            self.current_y = event.y

    def on_mouse_move(self, widget, event):
        if self.drawing:
            self.current_x = event.x
            self.current_y = event.y
            self.drawing_area.queue_draw()

    def on_button_release(self, widget, event):
        if self.drawing and event.button == 1:
            self.drawing = False
            shape = self.make_shape(
                self.current_tool,
                self.start_x,
                self.start_y,
                event.x,
                event.y,
            )
            self.shapes.append(shape)
            self.undo_stack.append(shape)
            self.redo_stack.clear()
            self.drawing_area.queue_draw()

    # ------------------- Text -------------------

    def show_text_popup(self, x, y):
        dialog = Gtk.Dialog(
            title="Text eingeben",
            transient_for=self,
            modal=True,
            destroy_with_parent=True
        )
        dialog.set_default_size(300, 100)
        
        box = dialog.get_content_area()
        box.set_spacing(10)
        box.set_border_width(10)
        
        entry = Gtk.Entry()
        entry.set_placeholder_text("Text hier eingeben...")
        entry.set_activates_default(True)
        box.add(entry)

        dialog.add_button("Abbrechen", Gtk.ResponseType.CANCEL)
        dialog.add_button("OK", Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)

        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            text = entry.get_text().strip()
            if text:
                shape = self.make_shape(Tool.TEXT, x, y, x, y, text=text)
                self.shapes.append(shape)
                self.undo_stack.append(shape)
                self.redo_stack.clear()
                self.drawing_area.queue_draw()

        dialog.destroy()

    # ------------------- Werkzeug-Handler -------------------

    def on_tool_toggled(self, btn, tool_id):
        if btn.get_active():
            self.current_tool = tool_id
            # Deaktiviere andere Buttons in der Gruppe
            for other_btn in self.tool_group:
                if other_btn != btn and other_btn.get_active():
                    other_btn.set_active(False)

    def on_color_set(self, color_button):
        color = color_button.get_rgba()
        self.current_color = (
            color.red,
            color.green,
            color.blue,
            color.alpha,
        )

    def on_linewidth_changed(self, combo):
        index = combo.get_active()
        if 0 <= index < len(self.line_widths):
            self.current_line_width = self.line_widths[index]

    def on_textsize_changed(self, combo):
        index = combo.get_active()
        if 0 <= index < len(self.font_sizes):
            self.current_text_size = self.font_sizes[index]

    # ------------------- Undo / Redo -------------------

    def on_undo_clicked(self, btn):
        if self.shapes:
            s = self.shapes.pop()
            self.redo_stack.append(s)
            self.drawing_area.queue_draw()

    def on_redo_clicked(self, btn):
        if self.redo_stack:
            s = self.redo_stack.pop()
            self.shapes.append(s)
            self.drawing_area.queue_draw()

    # ------------------- Speichern -------------------

    def on_save_clicked(self, btn):
        dialog = Gtk.FileChooserDialog(
            title="Bild speichern",
            transient_for=self,
            action=Gtk.FileChooserAction.SAVE,
            buttons=(
                "Abbrechen", Gtk.ResponseType.CANCEL,
                "Speichern", Gtk.ResponseType.OK
            )
        )
        
        dialog.set_default_response(Gtk.ResponseType.OK)
        
        # Vorgeschlagener Dateiname mit Zeitstempel
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dialog.set_current_name(f"screenshot_{timestamp}.png")
        
        # Filter für PNG
        filter_png = Gtk.FileFilter()
        filter_png.set_name("PNG Bilder")
        filter_png.add_mime_type("image/png")
        filter_png.add_pattern("*.png")
        dialog.add_filter(filter_png)
        
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            
            # Sicherstellen, dass die Datei mit .png endet
            if not filename.lower().endswith('.png'):
                filename += '.png'
            
            # Bild zusammenstellen und speichern
            width = self.background_surface.get_width()
            height = self.background_surface.get_height()
            
            # Neue Cairo-Surface erstellen
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            cr = cairo.Context(surface)
            
            # Hintergrund zeichnen
            cr.set_source_surface(self.background_surface, 0, 0)
            cr.paint()
            
            # Alle Formen zeichnen
            for shape in self.shapes:
                self.draw_shape(cr, shape)
            
            # Speichern
            surface.write_to_png(filename)
            
            if self.request_mode:
                # Im Request-Modus: Pfad ausgeben und beenden
                print(json.dumps({"status": "success", "file": filename}))
                self.destroy()
                Gtk.main_quit()
            else:
                # Erfolgsmeldung
                message_dialog = Gtk.MessageDialog(
                    transient_for=self,
                    flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="Bild gespeichert"
                )
                message_dialog.format_secondary_text(f"Datei gespeichert als:\n{filename}")
                message_dialog.run()
                message_dialog.destroy()
        
        dialog.destroy()

    def on_cancel_clicked(self):
        """Im Request-Modus abbrechen"""
        if self.request_mode:
            print(json.dumps({"status": "cancelled", "file": None}))
            self.destroy()
            Gtk.main_quit()
        else:
            self.destroy()

    def show_info(self):
        """Info-Dialog anzeigen"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="GuideOS Bildschirmfoto-Editor"
        )
        dialog.format_secondary_text(
            "Ein einfaches Screenshot-Tool für Cinnamon Desktop\n\n"
            "Verwendung:\n"
            "1. Bereich auswählen\n"
            "2. Mit Werkzeugen annotieren\n"
            "3. Speichern\n\n"
            "Tastenkürzel:\n"
            "• ESC: Abbrechen\n"
            "• Enter/Space: Auswahl bestätigen"
        )
        dialog.run()
        dialog.destroy()


# ===================== Request-Sub-Process =====================

def run_request_mode():
    """Startet den Screenshot-Prozess im Request-Modus"""
    Gdk.init([])
    
    # Bereichsauswahl starten
    selector = AreaSelectorWindow()
    rect = selector.run()
    
    if rect is None:
        print(json.dumps({"status": "cancelled", "file": None}))
        return
    
    x, y, w, h = rect
    
    # Screenshot aufnehmen
    pixbuf = ScreenshotEngine.capture_area(x, y, w, h)
    
    if pixbuf is None:
        print(json.dumps({"status": "error", "message": "Screenshot fehlgeschlagen"}))
        return
    
    # Editor starten
    editor = EditorWindow(pixbuf, request_mode=True)
    editor.connect("destroy", Gtk.main_quit)
    
    try:
        Gtk.main()
    except KeyboardInterrupt:
        print(json.dumps({"status": "cancelled", "file": None}))


# ===================== Start-Fenster =====================

class StartWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="GuideOS Bildschirmfoto-Editor")
        # Breiteres, liegendes Rechteck (500x150 statt 400x150)
        self.set_default_size(400, 150)
        self.set_border_width(20)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_default_icon_name("applets-screenshooter")

        # CSS für Cinnamon Aussehen mit Farbe #2573bf
        css_provider = Gtk.CssProvider()
        css = """
        window {
            background-color: @theme_base_color;
        }
        .suggested-action {
            background-color: #2573bf;
            color: white;
        }
        .suggested-action:hover {
            background-color: #1a5a9c;
        }
        """
        css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        main_box = Gtk.VBox(spacing=20)
        self.add(main_box)

        # HeaderBar mit Window Controls für Cinnamon
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.set_title("GuideOS Bildschirmfoto-Editor")
        self.set_titlebar(header_bar)

        # Haupt-Button
        btn_area = Gtk.Button.new_with_label("Bereich auswählen")
        btn_area.get_style_context().add_class("suggested-action")
        btn_area.set_size_request(200, 50)
        btn_area.set_margin_top(10)
        btn_area.connect("clicked", self.on_area_clicked)
        main_box.pack_start(btn_area, True, True, 0)

        # Info (korrigiert - ohne class-Attribut)
        info_label = Gtk.Label()
        info_label.set_markup("<span size='small'>Wähle einen Bereich auf dem Bildschirm aus</span>")
        info_label.set_margin_bottom(10)
        main_box.pack_start(info_label, False, False, 0)

        self.show_all()

    def open_editor_with_pixbuf(self, pixbuf):
        if pixbuf is None:
            error_dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Fehler beim Aufnehmen"
            )
            error_dialog.format_secondary_text("Das Screenshot konnte nicht erstellt werden.")
            error_dialog.run()
            error_dialog.destroy()
            self.show()
            return
        
        editor = EditorWindow(pixbuf)
        editor.connect("destroy", self.on_editor_closed)
        editor.show_all()
        self.hide()

    def on_editor_closed(self, widget):
        self.show()

    def on_area_clicked(self, btn):
        self.hide()
        
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        
        GLib.timeout_add(100, self.start_area_selection)
    
    def start_area_selection(self):
        selector = AreaSelectorWindow()
        rect = selector.run()
        
        if rect is None:
            self.show()
            return
        
        x, y, w, h = rect
        
        GLib.timeout_add(50, lambda: self.capture_area_delayed(x, y, w, h))
        return False
    
    def capture_area_delayed(self, x, y, w, h):
        pb = ScreenshotEngine.capture_area(x, y, w, h)
        self.open_editor_with_pixbuf(pb)
        return False


# ===================== main() =====================

def main():
    Gdk.init([])
    
    # Prüfen, ob wir im Request-Modus sind
    if len(sys.argv) > 1 and sys.argv[1] == "--request":
        run_request_mode()
    else:
        # Normales Startfenster
        win = StartWindow()
        win.connect("destroy", Gtk.main_quit)
        
        try:
            Gtk.main()
        except KeyboardInterrupt:
            print("\nProgramm beendet.")

if __name__ == "__main__":
    main()
