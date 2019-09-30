from setuptools import setup, find_packages


setup(
    name='ALifeEngine',
    version='0.0.1',
    packages=find_packages(exclude=('alifeengine_node', 'dind_python')),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "ae-cli=alifeengine.cli:main",
        ]
    }
)
