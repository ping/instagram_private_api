try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

__author__ = 'ping <lastmodified@gmail.com>'
__version__ = '1.2.4'

packages = [
    'instagram_private_api',
    'instagram_private_api.endpoints',
    'instagram_web_api'
]

setup(
    name='instagram_private_api',
    version=__version__,
    author='ping',
    author_email='lastmodified@gmail.com>',
    license='MIT',
    url='https://github.com/ping/instagram_private_api/tree/master',
    install_requires=[],
    keywords='instagram private api',
    description='A client interface for the private Instagram API.',
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
