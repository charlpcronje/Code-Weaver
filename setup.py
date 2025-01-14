from setuptools import setup, find_packages

setup(
    name='codeweaver',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'watchdog',
        'gitpython',
    ],
    entry_points={
        'console_scripts': [
            'weaver=weaver:main',
        ],
    },
)