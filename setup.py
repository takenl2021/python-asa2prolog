from setuptools import setup


def _requires_from_file(filename):
    return open(filename).read().splitlines()


setup(
    name="asa2prolog",
    version="1.0.0",
    install_requires=[
        'mecab-python3',
        'cabocha-python',
        'graphviz',
    ],
    packages=['asa2prolog']
)
