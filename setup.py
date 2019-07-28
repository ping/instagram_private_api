from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

def readall(*args):
    with open(path.join(here, *args), encoding='utf-8') as fp:
        return fp.read()

with open('requirements.test.txt') as f:
    test_deps = f.read().splitlines()

documentation = readall('README.md')
version = readall('instapi', 'version.txt')

setup(
    name='instapi',
    version=version,
    author='Felix Breuer',
    author_email='hi@felixbreuer.me',
    license='MIT',
    url='https://github.com/breuerfelix/instapi',
    install_requires=[],
    test_requires=test_deps,
    keywords='instagram private api',
    description='A client interface for the private Instagram API.',
    long_description=documentation,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires=">=3",
    package_data={
        'instapi': ["version.txt"]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
    ]
)
