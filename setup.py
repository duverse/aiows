import setuptools
from distutils.core import setup


setup(
    name='aiows',
    version='0.1a',
    packages=setuptools.find_packages(),
    url='https://github.com/duverse/aiows',
    license='General Public License v3.0',
    description='Easy to use aiohttp websockets application.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=[
        'aiohttp',
        'async-timeout',
    ],
    entry_points={
        'console_scripts': ['aiows=aiows.aiows:main'],
    },
    classifiers=[
        'Framework :: AsyncIO',
    ]
)
