#!/usr/bin/env bash

gap() { 
    echo ""
    echo "---"
    echo ""
}

gap

echo "Home is: ${HOME}"
echo "User is: ${USER}"

gap

echo "Backups folder:"
ls -al "${HOME}/backups"

gap

echo "All .envrc files in system:"
echo ""
find $HOME | grep ".envrc"
find . | grep ".envrc"

gap
