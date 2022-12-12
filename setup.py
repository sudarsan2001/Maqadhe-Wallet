# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in maqadhe_wallet/__init__.py
from maqadhe_wallet import __version__ as version

setup(
	name='maqadhe_wallet',
	version=version,
	description='Wallet Transactions',
	author='Administrator',
	author_email='admin@gmail.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
