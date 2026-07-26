# Maintainer: GuideOS <maintainer@example.com>

pkgname=guideos-screenshot-editor
depends=(
  'python'
  'python-gobject'
  'python-cairo'
  'gtk3'
  'gdk-pixbuf2'
)
optdepends=(
  'xdotool: active window capture support'
  'wmctrl: active window capture support'
)
pkgver=2.2.1
pkgrel=1
pkgdesc='Erweiterter Screenshot-Editor für Linux mit Annotationen, Multi-Monitor-Support und Öffnen-mit-Funktion'
arch=('any')
url='https://github.com/guideos/guideos-screenshot-editor'
license=('MIT')
source=(
  'guideos-screenshot-editor'
  'guideos-screenshot-editor.desktop'
  'guideos-screenshot-editor.svg'
)
sha256sums=('SKIP' 'SKIP' 'SKIP')

package() {
  install -Dm755 "$srcdir/guideos-screenshot-editor" "$pkgdir/usr/bin/guideos-screenshot-editor"
  install -Dm644 "$srcdir/guideos-screenshot-editor.desktop" "$pkgdir/usr/share/applications/guideos-screenshot-editor.desktop"
  install -Dm644 "$srcdir/guideos-screenshot-editor.svg" "$pkgdir/usr/share/pixmaps/guideos-screenshot-editor.svg"
}

check() {
  if ! command -v xdotool >/dev/null 2>&1 && ! command -v wmctrl >/dev/null 2>&1; then
    echo "error: either xdotool or wmctrl must be installed for active window capture support"
    exit 1
  fi
}
