# Maintainer: Actionschnitzel <actionschnitzel@guideos.de>

pkgname=guideos-screenshot-editor
pkgver=2.1
pkgrel=1
pkgdesc="Erweiterter Screenshot-Editor mit Multi-Monitor-Support, XFCE4-Unterstützung, Annotationen und JSON-Request-Modus"
arch=('any')
url=""
license=('MIT')
depends=(
    'python'
    'python-gobject'
    'python-cairo'
    'gtk3'
    'gdk-pixbuf2'
    'pango'
    'scrot'          # Fallback-Screenshot-Methode für XFCE4/xfwm4
)
makedepends=()
optdepends=(
    'imagemagick: alternativer Screenshot-Fallback'
    'xfconf: XFCE4-Theme-Erkennung'
)

# Kein Remote-Quell-Archiv – Paket wird direkt aus dem Projektverzeichnis gebaut.
# makepkg im Projektverzeichnis ausführen: cd /pfad/zum/projekt && makepkg -si
source=()
sha256sums=()

package() {
    local _src="$startdir"

    # Hauptskript
    install -Dm755 "$_src/guideos-screenshot-editor" \
        "$pkgdir/usr/lib/guideos/guideos-screenshot-editor/guideos-screenshot-editor"

    # Wrapper in /usr/bin
    install -d "$pkgdir/usr/bin"
    printf '#!/bin/bash\nexec python3 /usr/lib/guideos/guideos-screenshot-editor/guideos-screenshot-editor "$@"\n' \
        > "$pkgdir/usr/bin/guideos-screenshot-editor"
    chmod 755 "$pkgdir/usr/bin/guideos-screenshot-editor"

    # Desktop-Eintrag
    install -Dm644 "$_src/guideos-screenshot-editor.desktop" \
        "$pkgdir/usr/share/applications/guideos-screenshot-editor.desktop"

    # Icon (skalierbar)
    install -Dm644 "$_src/guideos-screenshot-editor.svg" \
        "$pkgdir/usr/share/icons/hicolor/scalable/apps/guideos-screenshot-editor.svg"

    # Toolbar-Pixmaps
    install -d "$pkgdir/usr/share/pixmaps"
    cp "$_src/usr/share/pixmaps/"* "$pkgdir/usr/share/pixmaps/"

    # Lizenz
    install -Dm644 "$_src/README.md" \
        "$pkgdir/usr/share/doc/$pkgname/README.md"
}
