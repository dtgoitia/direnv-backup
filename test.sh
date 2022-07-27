#!/usr/bin/env bash

test_dir="kk_dir"
file_name="20220726_090741.815598_dtg_metadata"
tar_file="backups/$file_name.tar"
encrypted_file="${test_dir}/$file_name.encrypted"
decrypted_file="${test_dir}/${file_name}_decrypted.tar"

rm -rf $test_dir
read -p "Test dir removed. Press ENTER to continue "

mkdir $test_dir

# cp -r $tar_file "$test_dir/$tar_file"

gpg \
    --output $encrypted_file \
    --encrypt \
        --recipient david.torralba.goitia@gmail.com \
    $tar_file

read -p "Encrypted. Press ENTER to decrypt "

gpg --output $decrypted_file --decrypt $encrypted_file
echo "Decrypted"

tar --extract --verbose -f $decrypted_file --directory $test_dir


echo "Extracted"
echo ""
echo ""

find $test_dir
