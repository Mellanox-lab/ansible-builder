#!/usr/bin/env python3.9
"""Setuptools shim for pre-PEP571 build methods."""
import setuptools  # type: ignore
#from setuptools import setup
#
#setup(
#    setup_requires=['pbr'],
#    pbr=True,
#    packages=['ansible_builder'],
#    package_dir={'':'src'}
#)
#

# DO NOT EDIT, use setup.cfg instead.
if __name__ == "__main__":
    setuptools.setup()
