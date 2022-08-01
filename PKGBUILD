# Maintainer: David Torralba Goitia <david.torralba.goitia@gmail.com>

_name=direnv-backup
pkgname="${_name}-git"
# TODO: pick version from pyproject.toml
pkgver=0.0.1
pkgrel=1
# TODO: pick description from pyproject.toml
pkgdesc="Tool to backup/restore direnv files with optional encryption"
arch=("any")
url="https://github.com/dtgoitia/${_name}"
source=("https://github.com/dtgoitia/${_name}.git")


provides=($_name)
conflicts=($_name "${_name}-git" "${_name}-bin")
license=("GLP3")
depends=(python)
makedepends=(git python-build python-installer)
# prepare() {
#     git clone $source --single-branch
# }

build () {
    # cd ..
    # python -m direnv_backup.cli.backup --help   < OK
    python -c "import sys; print(sys.path)"
    # python setup.py build
}

package() {
    pwd
    # cd ..
    # echo "Files:"
    # find .
    # echo ""
    # echo "Variables:"
    # printenv
    # echo ""

    # echo "a: $pkgdir/usr/bin"
    # dst=$(pwd)
    # echo "dst = $dst"
    python setup.py install --root="$pkgdir" --optimize=1
}
sha256sums=('521fdd6c83e9877ec311f1a763b645ce36e02fb0bb605fb9c474b7df465e8ee6')
