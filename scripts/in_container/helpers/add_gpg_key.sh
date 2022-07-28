#!/usr/bin/env bash

# exit when a command fails
set -e

echo "Creating a GPG key"

# create a temporary file with the specification of the key we want to create
# https://www.gnupg.org/documentation/manuals/gnupg-devel/Unattended-GPG-key-generation.html
spec_path=".gpg_spec_file"

cat > $spec_path <<EOF
    %echo Generating a default key
    # Do not ask for a passphrase
    %no-protection
    Key-Type: default
    Subkey-Type: default
    Name-Real: John Doe
    Name-Comment: with stupid passphrase
    Name-Email: john@doe.com
    Expire-Date: 0
    # Do a commit here, so that we can later print "done" :-)
    %commit
    %echo done
EOF

# Generate the key
gpg --batch --gen-key $spec_path

echo "GPG key generated"

gpg --list-keys

echo "Cleaning up spec file"
rm $spec_path
