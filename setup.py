from codecs import open
from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file.
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

import unittest


def my_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('grobid/tests', pattern='test_*.py')
    return test_suite


setup(
    name='grobid-quantities-client',
    version='0.1.0',
    description='A minimal client for grobid-quantities service.',
    long_description=long_description,
    url='https://github.com/lfoppiano/grobid-quantitites-python-client',
    author='Luca Foppiano',
    author_email='FOPPIANO.Luca@nims.go.jp',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=['measurements', 'text mining', 'tdm', 'grobid'],
    install_requires=['requests', 'zenlog'],
    packages=['grobid'],
    zip_safe=False,
    test_suite='setup.my_test_suite'
)
