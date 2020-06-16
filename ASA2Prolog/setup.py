from setuptools import setup, find_packages
from os import path

setup(
    name='ASAtoProlog',
    version='1.0.0',
    description='ASAの出力からPrologの木構造を作成',
    author='Shu Ogasawara',
    author_email='p28m4h8q@s.okayama-u.ac.jp',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    packages=['ASAtoProlog'],  
)
