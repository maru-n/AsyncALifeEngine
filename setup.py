from setuptools import setup, find_packages


setup(
    name='ALifeEngine',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "ae-cli=alifeengine.cli:main",
        ]
    }
)
