from setuptools import setup

setup(
    name="asa2prolog",
    version="1.0.2",
    install_requires=[
        'mecab-python3',
        'cabocha-python',
        'graphviz',
    ],
    packages=['asa2prolog']
)
