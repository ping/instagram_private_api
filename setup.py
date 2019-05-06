from os import path
from io import open
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    import unittest.mock
    has_mock = True
except ImportError:
    has_mock = False

__author__ = 'ping <lastmodified@gmail.com>'
__version__ = '1.6.0'

packages = [
    'instagram_private_api',
    'instagram_private_api.endpoints',
    'instagram_web_api'
]
test_reqs = [] if has_mock else ['mock']

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='instagram_private_api',
    version=__version__,
    author='ping',
    author_email='lastmodified@gmail.com>',
    license='MIT',
    url='https://github.com/ping/instagram_private_api/tree/master',
    install_requires=[],
    test_requires=test_reqs,
    keywords='instagram private api',
    description='A client interface for the private Instagram API.',
    long_description=long_description,
    packages=packages,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ]
)
