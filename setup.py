import os
import codecs
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


# Get the long description from the README file
with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='schdl',
    version='0.1a',
    description='A Scheme-inspired Hardware Description Language',
    long_description=long_description,
    url='https://github.com/jackrosenthal/schdl',

    author='Jack Rosenthal, Adam Frick, Robby Zampino',
    author_email='jack@rosenth.al',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Text Processing :: Linguistic',
        'Programming Language :: Lisp',
        'Programming Language :: Scheme',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='education electronics lisp scheme language',

    packages=['schdl'],

    python_requires='>=3.6, <4',

    install_requires=[],

    entry_points={
        'console_scripts': [
            'shcdl=schdl.__main__:main',
        ],
    }
)
