#!/usr/bin/env bash

pkgbuild=PKGBUILD
template=PKGBUILD.template

cp $template $pkgbuild

# Update checksum
makepkg -g >> $pkgbuild

# Build package
makepkg --syncdeps --force --rmdeps
# TODO: use --rmdeps to clean up makedeps once its done