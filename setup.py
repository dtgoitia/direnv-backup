import os

from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="direnv_backup",
    version="0.0.1",
    author="David Torralba Goitia",
    author_email="david.torralba.goitia@gmail.com",
    description="Tool to backup/restore direnv files with optional encryption",
    license="GLP3",
    keywords=["direnv", "backup", "restore", "encrypted"],
    packages=[],
    install_requires=["setuptools"],
    include_package_data=True,
)
