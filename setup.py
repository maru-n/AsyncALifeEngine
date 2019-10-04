from setuptools import setup, find_packages


setup(
    name='ALifeEngine',
    version='0.0.2',
    packages=find_packages(exclude=('docker')),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "ae-cli=alifeengine.cli:main",
        ]
    }
)
