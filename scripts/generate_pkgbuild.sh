#!/usr/bin/env bash

pkgbuild_dir="PKGBUILD"
cd $pkgbuild_dir || exit 1

pkgbuild="PKGBUILD"
template="PKGBUILD.template"

cp $template $pkgbuild

# Update checksum
makepkg --geninteg >> $pkgbuild 2>/dev/null

# Clean up empty folders
rm -rf "src"
