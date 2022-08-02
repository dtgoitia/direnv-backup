#!/usr/bin/env bash

pkgbuild=PKGBUILD
template=PKGBUILD.template

cp $template $pkgbuild

work_dir="TO_DELETE"
mkdir $work_dir
cp $pkgbuild "$work_dir/$pkgbuild"
cd $work_dir

# Update checksum
makepkg -g >> $pkgbuild

# Build package
makepkg --syncdeps --force
# TODO: use --rmdeps to clean up makedeps once its done