#!/usr/bin/env bash

set -e  # exit when a command fails

# --------------------------------------------------------------------------------------
#
#   Assertion 1: PKGBUILD correctly builds a package
#
# --------------------------------------------------------------------------------------

src_dir="/pacman_build_dir"
dst_dir="${HOME}"

from="${src_dir}/PKGBUILD"
to="${dst_dir}/PKGBUILD"

echo "Copying '${from}' to '${to}'"
cp "${from}" "${to}"

echo "Changing directory to '${dst_dir}'"
cd $dst_dir

echo "Building package from PKGBUILD..."
makepkg --noconfirm --cleanbuild --syncdeps --force
echo "SUCCESS: package build run without error"

# Look for the built package
expected_extension="*.pkg.tar.zst"
package_path=$(find ~/ -name "${expected_extension}")

echo ""
echo "Looking for the built package..."
if [ -z "${package_path}" ]; then
    echo "FAILURE: expected to find a file with the '${expected_extension}' extension, but not found"
    exit 1
else
    echo "SUCCESS: found file with the '${expected_extension}' extension at '${package_path}'"
fi


# --------------------------------------------------------------------------------------
#
#   Assertion 2: built package is correctly installed with pacman
#
# --------------------------------------------------------------------------------------

package_name="direnv-backup-git"
command_name="direnv-backup"

is_installed_in_pacman () {
    pacman -Qi "${package_name}" 2>/dev/null
}
command_exists () {
    which "${command_name}" 2>/dev/null
}

echo ""
echo "Ensuring that the package is not installed..."
set +e  # do not exit when a command fails
if [ -n "$(is_installed_in_pacman)" ]; then
    echo "FAILURE: '${package_name}' package is installed according to pacman"
    exit 1
else
    echo "SUCCESS: '${package_name}' package is not installed according to pacman"
fi

if [ -n "$(command_exists)" ]; then
    echo "FAILURE: '${command_name}' command exists"
    exit 1
else
    echo "SUCCESS: '${command_name}' command does not exist"
fi


echo ""
echo "Installing built package with pacman..."
set -e  # exit when a command fails
sudo pacman -U "${package_path}" --noconfirm
set +e  # do not exit when a command fails
echo "SUCCESS: pacman installation run without errors"

echo ""
echo "Ensuring that the package is installed..."
if [ -n "$(is_installed_in_pacman)" ]; then
    echo "SUCCESS: '${package_name}' package is installed according to pacman"
else
    echo "FAILURE: '${package_name}' package is not installed according to pacman"
    exit 1
fi

if [ -n "$(command_exists)" ]; then
    echo "SUCCESS: '${command_name}' command exists"
else
    echo "FAILURE: '${command_name}' command does not exist"
    exit 1
fi