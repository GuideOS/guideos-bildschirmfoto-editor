#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
#  GuideOS Bildschirmfoto‑Editor – Erweiterte Edition
#  --------------------------------------------------
#  Ein leistungsstarkes Screenshot‑ und Markup‑Werkzeug mit:
#    • Vollständiger Multi‑Monitor‑Unterstützung
#    • Präziser Bereichsauswahl inkl. Live‑Größenanzeige
#    • Wayland‑Fallback und korrekter Monitor‑Geometrie
#    • Lupenwerkzeug, Pfeile, Linien, Rechtecke, Kreise, Text
#    • Freihand‑Modus, Marker, Farbwahl, variable Liniendicken
#    • Undo/Redo‑System und PNG‑Export mit Zeitstempel
#    • JSON‑Request‑Modus für automatisierte Abläufe
#
#  Projekt:   GuideOS – Bildschirmfoto‑Editor
#  Datei:     guideos-screenshot-editor.py
#  Autoren:   evilware666 & Helga
#  Version:   1.8
#  Lizenz:    MIT
#  Datum:     18.02.2026
#
#  Hinweis:
#    Ideal für Dokumentation, Support, Tutorials und präzise Markups.
#    Unterstützt X11 und Wayland (Fallback‑Mechanismen integriert).
# ==============================================================================

#
# Hinweis     : - Multi-Monitor-Auswahl mit korrekter Geometrie-Erkennung.
#               - Bereichsauswahl zeigt Live-Gr\u00f6\u00dfe und Monitor-Info an.
#               - Screenshot-Engine unterst\u00fctzt Monitor-Offsets und Wayland-Fallback.
#               - Editor bietet Lupe, Text, Pfeile, Formen, Freihand, Undo/Redo.
#               - PNG-Export mit Zeitstempel und Dateidialog.
#               - Request-Modus gibt JSON zur\u00fcck (f\u00fcr Automatisierung).
#               - Ideal f\u00fcr Dokumentation, Support, Tutorials und pr\u00e4zise Markups.
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
    def capture_area(x, y, width, height, monitor_num=None):
        """Nimmt einen Bereich des Bildschirms auf"""
        display = Gdk.Display.get_default()
        screen = display.get_default_screen()
        
        if monitor_num is not None:
            monitor = display.get_monitor(monitor_num)
            geometry = monitor.get_geometry()
            monitor_x, monitor_y = geometry.x, geometry.y
            monitor_width, monitor_height = geometry.width, geometry.height
            
            x += monitor_x
            y += monitor_y
            
            if x < monitor_x:
                x = monitor_x
            if y < monitor_y:
                y = monitor_y
            if x + width > monitor_x + monitor_width:
                width = monitor_width - (x - monitor_x)
            if y + height > monitor_y + monitor_height:
                height = monitor_height - (y - monitor_y)
        
        root = Gdk.get_default_root_window()
        if not root:
            print("Kein Root-Window gefunden")
            return None
        
        pb = Gdk.pixbuf_get_from_window(root, int(x), int(y), int(width), int(height))

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
    
    @staticmethod
    def get_monitors():
        """Gibt Informationen \u00fcber alle Monitore zur\u00fcck"""
        display = Gdk.Display.get_default()
        monitors = []
        
        for i in range(display.get_n_monitors()):
            monitor = display.get_monitor(i)
            geometry = monitor.get_geometry()
            monitors.append({
                'number': i,
                'x': geometry.x,
                'y': geometry.y,
                'width': geometry.width,
                'height': geometry.height,
                'name': monitor.get_model() or f"Monitor {i+1}"
            })
        
        return monitors


# ===================== Bereichsauswahl-Fenster =====================

class AreaSelectorWindow(Gtk.Window):
    def __init__(self, multi_monitor=False):
        super().__init__(title="Bereich ausw\u00e4hlen")
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        
        self.multi_monitor = multi_monitor
        
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        if self.multi_monitor:
            display = Gdk.Display.get_default()
            min_x = 0
            min_y = 0
            max_x = 0
            max_y = 0
            
            for i in range(display.get_n_monitors()):
                monitor = display.get_monitor(i)
                geometry = monitor.get_geometry()
                min_x = min(min_x, geometry.x)
                min_y = min(min_y, geometry.y)
                max_x = max(max_x, geometry.x + geometry.width)
                max_y = max(max_y, geometry.y + geometry.height)
            
            self.move(min_x, min_y)
            self.set_default_size(max_x - min_x, max_y - min_y)
            self.fullscreen_on_monitor(screen, 0)
        else:
            self.fullscreen()

        self.start_x = 0
        self.start_y = 0
        self.cur_x = 0
        self.cur_y = 0
        self.selecting = False
        self.finished = False
        self.result_rect = None
        self.selected_monitor = None

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
        cr.set_source_rgba(0, 0, 0.5, 0.4)
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

            cr.set_source_rgba(1, 1, 1, 0.1)
            cr.rectangle(x, y, w, h)
            cr.fill()

            cr.set_source_rgba(1, 1, 1, 0.8)
            cr.set_line_width(2)
            cr.rectangle(x, y, w, h)
            cr.stroke()

            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cr.set_font_size(14)
            text = f"{int(w)} \u00d7 {int(h)}"
            extents = cr.text_extents(text)
            
            text_x = x + 10
            text_y = y + 25
            cr.set_source_rgba(0, 0, 0, 0.7)
            cr.rectangle(text_x - 5, text_y - extents.height - 5, 
                        extents.width + 10, extents.height + 10)
            cr.fill()
            
            cr.set_source_rgba(1, 1, 1, 1)
            cr.move_to(text_x, text_y)
            cr.show_text(text)
            
            if self.multi_monitor and self.selected_monitor is not None:
                monitor_text = f"Monitor {self.selected_monitor + 1}"
                cr.set_font_size(12)
                extents2 = cr.text_extents(monitor_text)
                text_x2 = x + w - extents2.width - 10
                text_y2 = y + h - 10
                
                cr.set_source_rgba(0, 0, 0, 0.7)
                cr.rectangle(text_x2 - 5, text_y2 - extents2.height - 5, 
                            extents2.width + 10, extents2.height + 10)
                cr.fill()
                
                cr.set_source_rgba(1, 1, 1, 1)
                cr.move_to(text_x2, text_y2)
                cr.show_text(monitor_text)

    def on_button_press(self, widget, event):
        if event.button == 1:
            self.start_x = event.x
            self.start_y = event.y
            self.cur_x = event.x
            self.cur_y = event.y
            self.selecting = True
            
            if self.multi_monitor:
                self.selected_monitor = self.get_monitor_at_position(event.x, event.y)
            
            self.queue_draw()

    def on_mouse_move(self, widget, event):
        if self.selecting:
            self.cur_x = event.x
            self.cur_y = event.y
            
            if self.multi_monitor and self.selected_monitor is None:
                self.selected_monitor = self.get_monitor_at_position(event.x, event.y)
            
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

            if w > 10 and h > 10:
                self.result_rect = (x, y, w, h)
            self.finished = True

    def on_key_press(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == "Escape":
            self.result_rect = None
            self.finished = True
        elif keyname == "Return" or keyname == "space":
            self.finished = True

    def get_monitor_at_position(self, x, y):
        """Ermittelt den Monitor an der gegebenen Position"""
        display = Gdk.Display.get_default()
        
        for i in range(display.get_n_monitors()):
            monitor = display.get_monitor(i)
            geometry = monitor.get_geometry()
            
            if (geometry.x <= x < geometry.x + geometry.width and
                geometry.y <= y < geometry.y + geometry.height):
                return i
        
        return None

    def run(self):
        self.show_all()
        self.grab_add()
        self.grab_focus()
        
        while not self.finished:
            while Gtk.events_pending():
                Gtk.main_iteration_do(False)

        self.grab_remove()
        rect = self.result_rect
        monitor = self.selected_monitor
        self.destroy()
        return rect, monitor


# ===================== Tool-Konstanten =====================

class Tool:
    LINE = "line"
    RECT = "rect"
    ELLIPSE = "ellipse"
    ARROW = "arrow"
    TEXT = "text"
    MAGNIFIER = "magnifier"
    MARKER = "marker"
    FREEHAND = "freehand"   # NEU: Freihand-Malen


# ===================== Editor-Fenster =====================

class EditorWindow(Gtk.Window):
    def __init__(self, image_pixbuf, request_mode=False):
        super().__init__(title="GuideOS Bildschirmfoto-Editor")
        self.set_border_width(0)
        self.set_default_icon_name("applets-screenshooter")
        self.request_mode = request_mode
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        css_provider = Gtk.CssProvider()
        css = """
        .tool-button {
            border-radius: 4px;
            padding: 6px 12px;
            border: 1px solid @borders;
        }
        .tool-button:checked,
        .tool-button:active {
            background-color: #2573bf;
            color: white;
            border-color: #1a5a9c;
        }
        .tool-button:hover {
            background-color: alpha(#2573bf, 0.1);
        }
        .suggested-action {
            background-color: #2573bf;
            color: white;
            border: none;
        }
        .suggested-action:hover {
            background-color: #1a5a9c;
        }
        .combobox {
            background-color: @theme_base_color;
            color: @theme_text_color;
        }
        .combobox arrow {
            color: @theme_fg_color;
        }
        .color-button {
            color: @theme_fg_color;
        }
        .color-button > button {
            background-color: @theme_base_color;
            color: @theme_fg_color;
        }
        GtkSeparator {
            background-color: @borders;
        }
        """
        css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.current_tool = None
        self.shapes = []
        self.undo_stack = []
        self.redo_stack = []
        self.drawing = False
        self.start_x = 0
        self.start_y = 0
        self.current_x = 0
        self.current_y = 0
        self.current_color = (0.1451, 0.4510, 0.7490, 1.0)
        self.current_line_width = 3.0
        self.current_text_size = 24.0
        self.magnifier_scale = 2.0

        # NEU: Freihand-Punkte f\u00fcr aktuelle Linie
        self.freehand_points = []

        self.font_sizes = [12, 14, 16, 18, 20, 24, 28, 32, 36, 48]
        self.line_widths = [1, 2, 3, 4, 5, 6, 8, 10]
        self.magnifier_scales = [1.5, 2.0, 2.5, 3.0, 4.0, 5.0]

        self.background_pixbuf = image_pixbuf
        self.background_surface = self.pixbuf_to_surface(image_pixbuf)

        self.image_width = self.background_surface.get_width()
        self.image_height = self.background_surface.get_height()
        
        self.set_default_size(800, 600)
        self.set_size_request(400, 300)

        main_box = Gtk.VBox(spacing=0)
        self.add(main_box)

        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.set_title("GuideOS Bildschirmfoto-Editor")
        header_bar.set_decoration_layout("menu:minimize,maximize,close")
        self.set_titlebar(header_bar)

        quit_btn = Gtk.Button.new_with_label("Beenden")
        quit_btn.get_style_context().add_class("suggested-action")
        quit_btn.connect("clicked", self.on_quit_clicked)
        header_bar.pack_start(quit_btn)

        if self.request_mode:
            cancel_btn = Gtk.Button.new_with_label("Abbrechen")
            cancel_btn.connect("clicked", lambda w: self.on_cancel_clicked())
            header_bar.pack_start(cancel_btn)
        else:
            info_btn = Gtk.Button.new_with_label("Info")
            info_btn.connect("clicked", lambda w: self.show_info())
            header_bar.pack_start(info_btn)

        clipboard_btn = Gtk.Button.new_with_label("Zwischenablage")
        clipboard_btn.get_style_context().add_class("suggested-action")
        clipboard_btn.connect("clicked", self.on_clipboard_clicked)
        header_bar.pack_end(clipboard_btn)
        
        save_btn = Gtk.Button.new_with_label("Speichern")
        save_btn.get_style_context().add_class("suggested-action")
        save_btn.connect("clicked", self.on_save_clicked)
        header_bar.pack_end(save_btn)

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(self.image_width, self.image_height)
        self.drawing_area.connect("draw", self.on_draw)
        self.drawing_area.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK
            | Gdk.EventMask.BUTTON_RELEASE_MASK
            | Gdk.EventMask.POINTER_MOTION_MASK
            | Gdk.EventMask.SCROLL_MASK
        )
        self.drawing_area.connect("button-press-event", self.on_button_press)
        self.drawing_area.connect("button-release-event", self.on_button_release)
        self.drawing_area.connect("motion-notify-event", self.on_mouse_move)
        self.drawing_area.connect("scroll-event", self.on_scroll_event)
        
        viewport = Gtk.Viewport()
        viewport.set_shadow_type(Gtk.ShadowType.NONE)
        viewport.add(self.drawing_area)
        
        align_box = Gtk.Alignment()
        align_box.set(0.5, 0.5, 0, 0)
        align_box.add(viewport)
        
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_shadow_type(Gtk.ShadowType.IN)
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.add(align_box)
        main_box.pack_start(self.scrolled_window, True, True, 0)

        toolbar_container = Gtk.HBox()
        toolbar_container.set_border_width(5)
        toolbar_container.set_margin_top(5)
        toolbar_container.set_margin_bottom(5)
        main_box.pack_start(toolbar_container, False, False, 0)

        left_spacer = Gtk.Label("")
        left_spacer.set_hexpand(True)
        toolbar_container.pack_start(left_spacer, True, True, 0)

        toolbar = Gtk.HBox(spacing=5)
        toolbar_container.pack_start(toolbar, False, False, 0)

        right_spacer = Gtk.Label("")
        right_spacer.set_hexpand(True)
        toolbar_container.pack_start(right_spacer, True, True, 0)

        def create_tool_button_with_custom_icon(custom_icon_names, label, tool_id=None):
            """Erstellt einen Werkzeug-Button mit benutzerdefiniertem Icon oder Fallback"""
            if tool_id:
                btn = Gtk.ToggleButton()
                btn.set_tooltip_text(label)
                btn.set_size_request(40, 40)
                btn.connect("toggled", self.on_tool_toggled, tool_id)
                self.tool_group.append(btn)
            else:
                btn = Gtk.Button()
                btn.set_size_request(40, 40)
            
            fallback_icons = {
                Tool.LINE: "draw-line",
                Tool.RECT: "gtk-justify-center",
                Tool.ELLIPSE: "pan-down",
                Tool.ARROW: "go-next",
                Tool.TEXT: "font-x-generic",
                Tool.MAGNIFIER: "zoom-in",
                Tool.MARKER: "marker",
                Tool.FREEHAND: "input-tablet",  # Fallback f\u00fcr Freihand
            }
            
            icon_loaded = False
            pixmaps_dir = "/usr/share/pixmaps/"
            
            for icon_name in custom_icon_names:
                icon_path = os.path.join(pixmaps_dir, icon_name)
                if os.path.exists(icon_path):
                    try:
                        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, 24, 24)
                        image = Gtk.Image.new_from_pixbuf(pixbuf)
                        btn.add(image)
                        icon_loaded = True
                        break
                    except Exception as e:
                        print(f"Konnte Icon {icon_path} nicht laden: {e}")
                        continue
            
            if not icon_loaded and tool_id:
                try:
                    fallback_icon = fallback_icons.get(tool_id, "image-missing")
                    image = Gtk.Image.new_from_icon_name(fallback_icon, Gtk.IconSize.LARGE_TOOLBAR)
                    btn.add(image)
                except:
                    btn = Gtk.Button(label=label[:3])
                    if tool_id:
                        btn.connect("toggled", self.on_tool_toggled, tool_id)
                        self.tool_group.append(btn)
            
            btn.get_style_context().add_class("tool-button")
            return btn

        self.tool_group = []
        
        line_btn = create_tool_button_with_custom_icon(
            ["Linie.png", "line.png", "Line.png"], "Linie", Tool.LINE
        )
        rect_btn = create_tool_button_with_custom_icon(
            ["Quadrat.png", "quadrat.png", "Rechteck.png", "rectangle.png"], 
            "Rechteck", Tool.RECT
        )
        ellipse_btn = create_tool_button_with_custom_icon(
            ["Kreis.png", "kreis.png", "circle.png", "Circle.png"], 
            "Kreis", Tool.ELLIPSE
        )
        arrow_btn = create_tool_button_with_custom_icon(
            ["Pfeil.png", "pfeil.png", "arrow.png", "Arrow.png"], 
            "Pfeil", Tool.ARROW
        )
        text_btn = create_tool_button_with_custom_icon(
            ["Text.png", "text.png", "T.png", "A.png"], 
            "Text", Tool.TEXT
        )
        magnifier_btn = create_tool_button_with_custom_icon(
            ["Lupe.png", "lupe.png", "magnifier.png", "zoom.png"], 
            "Lupe", Tool.MAGNIFIER
        )
        marker_btn = create_tool_button_with_custom_icon(
            ["Marker.png", "marker.png", "highlighter.png"], 
            "Marker", Tool.MARKER
        )

        # NEU: Freihand-Button
        freehand_btn = create_tool_button_with_custom_icon(
            ["Freihand.png", "freihand.png", "freehand.png", "pencil.png", "Pinsel.png"],
            "Freihand malen", Tool.FREEHAND
        )

        undo_btn = create_tool_button_with_custom_icon(
            ["zur\u00fcck.png", "zurueck.png", "undo.png", "Undo.png"], 
            "R\u00fcckg\u00e4ngig", None
        )
        undo_btn.connect("clicked", self.on_undo_clicked)
        
        redo_btn = create_tool_button_with_custom_icon(
            ["vor.png", "Vor.png", "redo.png", "Redo.png"], 
            "Wiederholen", None
        )
        redo_btn.connect("clicked", self.on_redo_clicked)
        
        color_btn = Gtk.ColorButton()
        color_btn.set_rgba(Gdk.RGBA(*self.current_color))
        color_btn.set_tooltip_text("Farbe")
        color_btn.set_size_request(40, 40)
        color_btn.connect("color-set", self.on_color_set)
        color_btn.get_style_context().add_class("color-button")
        
        linewidth_box = Gtk.VBox(spacing=2)
        linewidth_label = Gtk.Label()
        linewidth_label.set_markup("<span size='small'>Strichgr\u00f6\u00dfe</span>")
        linewidth_combo = Gtk.ComboBoxText()
        linewidth_combo.set_tooltip_text("Liniendicke")
        linewidth_combo.set_size_request(80, 30)
        for w in self.line_widths:
            linewidth_combo.append_text(f"{w} px")
        linewidth_combo.set_active(2)
        linewidth_combo.connect("changed", self.on_linewidth_changed)
        linewidth_combo.get_style_context().add_class("combobox")
        linewidth_box.pack_start(linewidth_label, False, False, 0)
        linewidth_box.pack_start(linewidth_combo, False, False, 0)
        
        textsize_box = Gtk.VBox(spacing=2)
        textsize_label = Gtk.Label()
        textsize_label.set_markup("<span size='small'>Schriftgr\u00f6\u00dfe</span>")
        textsize_combo = Gtk.ComboBoxText()
        textsize_combo.set_tooltip_text("Textgr\u00f6\u00dfe")
        textsize_combo.set_size_request(80, 30)
        for s in self.font_sizes:
            textsize_combo.append_text(f"{s} pt")
        textsize_combo.set_active(5)
        textsize_combo.connect("changed", self.on_textsize_changed)
        textsize_combo.get_style_context().add_class("combobox")
        textsize_box.pack_start(textsize_label, False, False, 0)
        textsize_box.pack_start(textsize_combo, False, False, 0)
        
        magnifier_box = Gtk.VBox(spacing=2)
        magnifier_label = Gtk.Label()
        magnifier_label.set_markup("<span size='small'>Lupenvergr\u00f6\u00dferung</span>")
        magnifier_combo = Gtk.ComboBoxText()
        magnifier_combo.set_tooltip_text("Vergr\u00f6\u00dferung")
        magnifier_combo.set_size_request(100, 30)
        for scale in self.magnifier_scales:
            magnifier_combo.append_text(f"{scale:.1f}\u00d7")
        magnifier_combo.set_active(1)
        magnifier_combo.connect("changed", self.on_magnifier_changed)
        magnifier_combo.get_style_context().add_class("combobox")
        magnifier_box.pack_start(magnifier_label, False, False, 0)
        magnifier_box.pack_start(magnifier_combo, False, False, 0)

        # Werkzeuge zur Toolbar hinzuf\u00fcgen \u2014 freehand_btn neu integriert
        for btn in [line_btn, rect_btn, ellipse_btn, arrow_btn, text_btn,
                   marker_btn, freehand_btn, magnifier_btn,
                   Gtk.SeparatorToolItem(), color_btn,
                   Gtk.SeparatorToolItem(), undo_btn, redo_btn,
                   Gtk.SeparatorToolItem(), linewidth_box,
                   Gtk.SeparatorToolItem(), textsize_box,
                   Gtk.SeparatorToolItem(), magnifier_box]:
            if isinstance(btn, Gtk.Widget):
                if isinstance(btn, (Gtk.Button, Gtk.ComboBoxText, Gtk.ToggleButton, Gtk.ColorButton, Gtk.VBox)):
                    container = Gtk.ToolItem()
                    container.add(btn)
                    toolbar.add(container)
                else:
                    toolbar.add(btn)

        self.zoom_level = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 10.0
        self.zoom_step = 0.1
        
        self.connect("configure-event", self.on_configure_event)
        self.connect("show", self.on_show)

    def on_configure_event(self, widget, event):
        pass

    def on_show(self, widget):
        screen = Gdk.Screen.get_default()
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        max_width = int(screen_width * 0.9)
        max_height = int(screen_height * 0.9)
        
        toolbar_height = 100
        header_height = 40
        
        window_width = min(self.image_width + 40, max_width)
        window_height = min(self.image_height + toolbar_height + header_height + 40, max_height)
        
        self.resize(window_width, window_height)

    def pixbuf_to_surface(self, pixbuf):
        width = pixbuf.get_width()
        height = pixbuf.get_height()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        cr = cairo.Context(surface)
        Gdk.cairo_set_source_pixbuf(cr, pixbuf, 0, 0)
        cr.paint()
        return surface

    # ------------------- Beenden -------------------
    
    def on_quit_clicked(self, btn):
        if self.request_mode:
            print(json.dumps({"status": "cancelled", "file": None}))
        self.destroy()
        Gtk.main_quit()

    # ------------------- Zoom-Koordinaten -------------------
    
    def screen_to_image_coords(self, screen_x, screen_y):
        alloc = self.drawing_area.get_allocation()
        offset_x = (alloc.width - self.image_width * self.zoom_level) / 2
        offset_y = (alloc.height - self.image_height * self.zoom_level) / 2
        image_x = (screen_x - offset_x) / self.zoom_level
        image_y = (screen_y - offset_y) / self.zoom_level
        image_x = max(0, min(image_x, self.image_width))
        image_y = max(0, min(image_y, self.image_height))
        return image_x, image_y

    # ------------------- Zoom -------------------
    
    def on_scroll_event(self, widget, event):
        ctrl_pressed = event.state & Gdk.ModifierType.CONTROL_MASK
        if ctrl_pressed:
            if event.direction == Gdk.ScrollDirection.UP:
                self.zoom_in()
            elif event.direction == Gdk.ScrollDirection.DOWN:
                self.zoom_out()
            return True
        return False
    
    def zoom_in(self):
        if self.zoom_level < self.max_zoom:
            self.zoom_level += self.zoom_step
            self.update_zoom()
    
    def zoom_out(self):
        if self.zoom_level > self.min_zoom:
            self.zoom_level -= self.zoom_step
            self.update_zoom()
    
    def update_zoom(self):
        width = int(self.image_width * self.zoom_level)
        height = int(self.image_height * self.zoom_level)
        self.drawing_area.set_size_request(width, height)
        self.drawing_area.queue_draw()
        zoom_percent = int(self.zoom_level * 100)
        self.set_title(f"GuideOS Bildschirmfoto-Editor ({zoom_percent}%)")

    # ------------------- Zeichnen -------------------

    def on_draw(self, widget, cr):
        alloc = widget.get_allocation()
        offset_x = (alloc.width - self.image_width * self.zoom_level) / 2
        offset_y = (alloc.height - self.image_height * self.zoom_level) / 2
        cr.translate(offset_x, offset_y)
        cr.scale(self.zoom_level, self.zoom_level)
        
        cr.set_source_surface(self.background_surface, 0, 0)
        cr.paint()

        for s in self.shapes:
            self.draw_shape(cr, s)

        # Aktuelle Zeichnung live anzeigen
        if self.drawing:
            if self.current_tool == Tool.MAGNIFIER:
                img_start_x, img_start_y = self.screen_to_image_coords(self.start_x, self.start_y)
                img_current_x, img_current_y = self.screen_to_image_coords(self.current_x, self.current_y)
                self.draw_magnifier(cr, img_start_x, img_start_y, img_current_x, img_current_y)
            elif self.current_tool == Tool.FREEHAND:
                # NEU: Freihand-Vorschau w\u00e4hrend des Zeichnens
                if len(self.freehand_points) > 1:
                    self.draw_freehand_points(cr, self.freehand_points, self.current_color, self.current_line_width)
            elif self.current_tool != Tool.TEXT:
                img_start_x, img_start_y = self.screen_to_image_coords(self.start_x, self.start_y)
                img_current_x, img_current_y = self.screen_to_image_coords(self.current_x, self.current_y)
                temp = self.make_shape(
                    self.current_tool,
                    img_start_x,
                    img_start_y,
                    img_current_x,
                    img_current_y,
                )
                self.draw_shape(cr, temp)

    def make_shape(self, tool, x1, y1, x2, y2, text=None, points=None):
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
            "points": points,  # NEU: f\u00fcr Freihand-Pfad
        }

    def draw_shape(self, cr, s):
        cr.set_source_rgba(*s["color"])

        if s["type"] == Tool.FREEHAND:
            # NEU: Freihand-Pfad zeichnen
            points = s.get("points", [])
            if len(points) > 1:
                self.draw_freehand_points(cr, points, s["color"], s["width"])

        elif s["type"] == Tool.MARKER:
            marker_width = s["width"] * 3
            cr.set_line_width(marker_width)
            r, g, b, a = s["color"]
            cr.set_source_rgba(r, g, b, a * 0.4)
            cr.move_to(s["x1"], s["y1"])
            cr.line_to(s["x2"], s["y2"])
            cr.stroke()
            
        elif s["type"] == Tool.LINE:
            cr.set_line_width(s["width"])
            cr.move_to(s["x1"], s["y1"])
            cr.line_to(s["x2"], s["y2"])
            cr.stroke()

        elif s["type"] == Tool.RECT:
            cr.set_line_width(s["width"])
            x = min(s["x1"], s["x2"])
            y = min(s["y1"], s["y2"])
            w = abs(s["x2"] - s["x1"])
            h = abs(s["y2"] - s["y1"])
            cr.rectangle(x, y, w, h)
            cr.stroke()

        elif s["type"] == Tool.ELLIPSE:
            cr.set_line_width(s["width"])
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
            cr.set_line_width(s["width"])
            self.draw_arrow(cr, s["x1"], s["y1"], s["x2"], s["y2"])

        elif s["type"] == Tool.TEXT and s["text"]:
            cr.set_line_width(s["width"])
            cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            cr.set_font_size(s["text_size"])
            cr.move_to(s["x1"], s["y1"])
            cr.show_text(s["text"])
            cr.stroke()

    def draw_freehand_points(self, cr, points, color, line_width):
        """Zeichnet einen glatten Freihand-Pfad durch die gegebenen Punkte"""
        if len(points) < 2:
            return
        cr.set_source_rgba(*color)
        cr.set_line_width(line_width)
        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)
        cr.move_to(points[0][0], points[0][1])
        # Glatte Kurve durch alle Punkte mit quadratischen Bezier-Kurven
        for i in range(1, len(points) - 1):
            mid_x = (points[i][0] + points[i + 1][0]) / 2
            mid_y = (points[i][1] + points[i + 1][1]) / 2
            cx, cy = points[i][0], points[i][1]
            cr.curve_to(cx, cy, cx, cy, mid_x, mid_y)
        # Letzten Punkt direkt verbinden
        cr.line_to(points[-1][0], points[-1][1])
        cr.stroke()
        # Line-Cap und Join zur\u00fccksetzen
        cr.set_line_cap(cairo.LINE_CAP_BUTT)
        cr.set_line_join(cairo.LINE_JOIN_MITER)

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

    def draw_magnifier(self, cr, x1, y1, x2, y2):
        size = 150
        
        cr.set_source_rgba(0, 0, 0, 0.7)
        cr.set_line_width(2)
        cr.arc(x2, y2, size/2, 0, 2 * math.pi)
        cr.stroke()
        
        scale = self.magnifier_scale
        source_x = x2 - (size/2) / scale
        source_y = y2 - (size/2) / scale
        source_size = size / scale
        
        if source_x < 0:
            source_x = 0
        if source_y < 0:
            source_y = 0
        if source_x + source_size > self.image_width:
            source_x = self.image_width - source_size
        if source_y + source_size > self.image_height:
            source_y = self.image_height - source_size
        
        cr.save()
        cr.arc(x2, y2, size/2 - 2, 0, 2 * math.pi)
        cr.clip()
        cr.translate(x2, y2)
        cr.scale(scale, scale)
        cr.translate(-source_x - source_size/2, -source_y - source_size/2)
        cr.set_source_surface(self.background_surface, 0, 0)
        cr.paint()
        for shape in self.shapes:
            self.draw_shape(cr, shape)
        cr.restore()
        
        cr.set_source_rgba(1, 0, 0, 0.8)
        cr.set_line_width(2)
        cr.move_to(x2, y2 - 10)
        cr.line_to(x2, y2 + 10)
        cr.move_to(x2 - 10, y2)
        cr.line_to(x2 + 10, y2)
        cr.stroke()

    # ------------------- Maus -------------------

    def on_button_press(self, widget, event):
        if event.button == 1:
            if self.current_tool == Tool.TEXT:
                img_x, img_y = self.screen_to_image_coords(event.x, event.y)
                self.show_text_popup(img_x, img_y)
                return

            if self.current_tool is not None:
                self.drawing = True
                self.start_x = event.x
                self.start_y = event.y
                self.current_x = event.x
                self.current_y = event.y

                # NEU: Freihand-Punkte zur\u00fccksetzen und Startpunkt hinzuf\u00fcgen
                if self.current_tool == Tool.FREEHAND:
                    img_x, img_y = self.screen_to_image_coords(event.x, event.y)
                    self.freehand_points = [(img_x, img_y)]

    def on_mouse_move(self, widget, event):
        if self.drawing:
            self.current_x = event.x
            self.current_y = event.y

            # NEU: Freihand-Punkt sammeln
            if self.current_tool == Tool.FREEHAND:
                img_x, img_y = self.screen_to_image_coords(event.x, event.y)
                self.freehand_points.append((img_x, img_y))

            self.drawing_area.queue_draw()

    def on_button_release(self, widget, event):
        if self.drawing and event.button == 1:
            self.drawing = False

            if self.current_tool == Tool.MAGNIFIER:
                pass  # Lupe wird nicht gespeichert

            elif self.current_tool == Tool.FREEHAND:
                # NEU: Freihand-Form mit allen Punkten speichern
                if len(self.freehand_points) > 1:
                    img_x, img_y = self.screen_to_image_coords(event.x, event.y)
                    self.freehand_points.append((img_x, img_y))
                    shape = self.make_shape(
                        Tool.FREEHAND,
                        self.freehand_points[0][0],
                        self.freehand_points[0][1],
                        self.freehand_points[-1][0],
                        self.freehand_points[-1][1],
                        points=list(self.freehand_points)
                    )
                    self.shapes.append(shape)
                    self.undo_stack.append(shape)
                    self.redo_stack.clear()
                self.freehand_points = []

            else:
                img_start_x, img_start_y = self.screen_to_image_coords(self.start_x, self.start_y)
                img_current_x, img_current_y = self.screen_to_image_coords(event.x, event.y)
                shape = self.make_shape(
                    self.current_tool,
                    img_start_x,
                    img_start_y,
                    img_current_x,
                    img_current_y,
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
            for other_btn in self.tool_group:
                if other_btn != btn and other_btn.get_active():
                    other_btn.set_active(False)
        else:
            if self.current_tool == tool_id:
                self.current_tool = None

    def on_color_set(self, color_button):
        color = color_button.get_rgba()
        self.current_color = (color.red, color.green, color.blue, color.alpha)

    def on_linewidth_changed(self, combo):
        index = combo.get_active()
        if 0 <= index < len(self.line_widths):
            self.current_line_width = self.line_widths[index]

    def on_textsize_changed(self, combo):
        index = combo.get_active()
        if 0 <= index < len(self.font_sizes):
            self.current_text_size = self.font_sizes[index]

    def on_magnifier_changed(self, combo):
        index = combo.get_active()
        if 0 <= index < len(self.magnifier_scales):
            self.magnifier_scale = self.magnifier_scales[index]

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

    # ------------------- Zwischenablage -------------------
    
    def on_clipboard_clicked(self, btn):
        try:
            width = self.image_width
            height = self.image_height
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            cr = cairo.Context(surface)
            cr.set_source_surface(self.background_surface, 0, 0)
            cr.paint()
            for shape in self.shapes:
                self.draw_shape(cr, shape)
            
            import array
            data = surface.get_data()
            stride = surface.get_stride()
            rgb_data = array.array('B')
            for y in range(height):
                for x in range(width):
                    offset = y * stride + x * 4
                    b = data[offset + 0]
                    g = data[offset + 1]
                    r = data[offset + 2]
                    a = data[offset + 3]
                    rgb_data.append(r)
                    rgb_data.append(g)
                    rgb_data.append(b)
                    rgb_data.append(a)
            
            pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                rgb_data.tobytes(),
                GdkPixbuf.Colorspace.RGB,
                True, 8, width, height, width * 4
            )
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            clipboard.set_image(pixbuf)
            clipboard.store()
            
            message_dialog = Gtk.MessageDialog(
                transient_for=self, flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="In Zwischenablage kopiert"
            )
            message_dialog.format_secondary_text(
                "Das Bild wurde in die Zwischenablage kopiert und kann nun in andere Anwendungen eingef\u00fcgt werden."
            )
            label = message_dialog.get_message_area().get_children()[0]
            label.set_markup('<span background="#2573bf" foreground="white" weight="bold" size="large"> In Zwischenablage kopiert </span>')
            message_dialog.run()
            message_dialog.destroy()
            print("Bild erfolgreich in die Zwischenablage kopiert.")
        except Exception as e:
            error_dialog = Gtk.MessageDialog(
                transient_for=self, flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Fehler beim Kopieren"
            )
            error_dialog.format_secondary_text(f"Das Bild konnte nicht in die Zwischenablage kopiert werden:\n{str(e)}")
            error_dialog.run()
            error_dialog.destroy()
            print(f"Fehler beim Kopieren in Zwischenablage: {e}")

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
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dialog.set_current_name(f"screenshot_{timestamp}.png")
        filter_png = Gtk.FileFilter()
        filter_png.set_name("PNG Bilder")
        filter_png.add_mime_type("image/png")
        filter_png.add_pattern("*.png")
        dialog.add_filter(filter_png)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            if not filename.lower().endswith('.png'):
                filename += '.png'
            width = self.image_width
            height = self.image_height
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            cr = cairo.Context(surface)
            cr.set_source_surface(self.background_surface, 0, 0)
            cr.paint()
            for shape in self.shapes:
                self.draw_shape(cr, shape)
            surface.write_to_png(filename)
            if self.request_mode:
                print(json.dumps({"status": "success", "file": filename}))
                self.destroy()
                Gtk.main_quit()
            else:
                message_dialog = Gtk.MessageDialog(
                    transient_for=self, flags=0,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="Bild gespeichert"
                )
                message_dialog.format_secondary_text(f"Datei gespeichert als:\n{filename}")
                message_dialog.run()
                message_dialog.destroy()
        dialog.destroy()

    def on_cancel_clicked(self):
        if self.request_mode:
            print(json.dumps({"status": "cancelled", "file": None}))
            self.destroy()
            Gtk.main_quit()
        else:
            self.destroy()

    def show_info(self):
        dialog = Gtk.MessageDialog(
            transient_for=self, flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="GuideOS Bildschirmfoto-Editor"
        )
        dialog.format_secondary_text(
            "Ein einfaches Screenshot-Tool f\u00fcr Cinnamon Desktop\n\n"
            "Verwendung:\n"
            "1. Bereich ausw\u00e4hlen\n"
            "2. Mit Werkzeugen annotieren\n"
            "3. Speichern oder in Zwischenablage kopieren\n"
            "4. Mit Beenden-Button Programm schlie\u00dfen\n\n"
            "Tastenk\u00fcrzel:\n"
            "\u2022 ESC: Abbrechen\n"
            "\u2022 Enter/Space: Auswahl best\u00e4tigen\n"
            "\u2022 Strg + Mausrad: Zoom\n\n"
            "Werkzeuge:\n"
            "\u2022 Linie, Rechteck, Kreis, Pfeil, Text\n"
            "\u2022 Marker: Halbtransparente Markierungen\n"
            "\u2022 Freihand: Freies Malen mit der Maus\n"
            "\u2022 Lupe: Vergr\u00f6\u00dfert Details\n\n"
            "Neue Funktionen:\n"
            "\u2022 Multi-Monitor: Unterst\u00fctzt mehrere Bildschirme\n"
            "\u2022 Zoom: Strg + Mausrad f\u00fcr Vergr\u00f6\u00dferung/Verkleinerung\n"
            "\u2022 Zwischenablage: Kopiert Bild direkt in die Zwischenablage\n"
            "\u2022 Freihand: Freies Malen und Markieren\n"
            "\u2022 Beenden: Programm komplett schlie\u00dfen"
        )
        dialog.run()
        dialog.destroy()


# ===================== Request-Sub-Process =====================

def run_request_mode():
    Gdk.init([])
    selector = AreaSelectorWindow(multi_monitor=True)
    rect, monitor = selector.run()
    
    if rect is None:
        print(json.dumps({"status": "cancelled", "file": None}))
        return
    
    x, y, w, h = rect
    
    import time
    time.sleep(0.2)
    
    pixbuf = ScreenshotEngine.capture_area(x, y, w, h, monitor)
    
    if pixbuf is None:
        print(json.dumps({"status": "error", "message": "Screenshot fehlgeschlagen"}))
        return
    
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
        self.set_default_size(400, 150)
        self.set_border_width(20)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_default_icon_name("applets-screenshooter")

        css_provider = Gtk.CssProvider()
        css = """
        .suggested-action {
            background-color: #2573bf;
            color: white;
            border: none;
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

        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.set_title("GuideOS Bildschirmfoto-Editor")
        self.set_titlebar(header_bar)

        btn_area = Gtk.Button.new_with_label("Anklicken, um einen Bereich auszuw\u00e4hlen")
        btn_area.get_style_context().add_class("suggested-action")
        btn_area.set_size_request(200, 50)
        btn_area.set_margin_top(10)
        btn_area.connect("clicked", self.on_area_clicked)
        main_box.pack_start(btn_area, True, True, 0)

        zoom_hint = Gtk.Label()
        zoom_hint.set_markup("<span size='small' style='italic'>Tipp: Strg + Mausrad zum Zoomen im Editor</span>")
        zoom_hint.set_margin_top(5)
        main_box.pack_start(zoom_hint, False, False, 0)

        info_label = Gtk.Label()
        info_label.set_markup("<span size='small'></span>")
        info_label.set_margin_bottom(10)
        main_box.pack_start(info_label, False, False, 0)

        self.show_all()

    def open_editor_with_pixbuf(self, pixbuf):
        if pixbuf is None:
            error_dialog = Gtk.MessageDialog(
                transient_for=self, flags=0,
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
        selector = AreaSelectorWindow(multi_monitor=True)
        rect, monitor = selector.run()
        
        if rect is None:
            self.show()
            return
        
        x, y, w, h = rect
        GLib.timeout_add(200, lambda: self.capture_area_delayed(x, y, w, h, monitor))
        return False
    
    def capture_area_delayed(self, x, y, w, h, monitor):
        pb = ScreenshotEngine.capture_area(x, y, w, h, monitor)
        self.open_editor_with_pixbuf(pb)
        return False


# ===================== main() =====================

def main():
    Gdk.init([])
    
    if len(sys.argv) > 1 and sys.argv[1] == "--request":
        run_request_mode()
    else:
        win = StartWindow()
        win.connect("destroy", Gtk.main_quit)
        try:
            Gtk.main()
        except KeyboardInterrupt:
            print("\nProgramm beendet.")

if __name__ == "__main__":
    main()
