Music Embedding
===========

[![GitHub license](https://img.shields.io/github/license/PooyaHekmati/music_embedding?style=for-the-badge)](https://github.com/PooyaHekmati/music_embedding/blob/main/LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/PooyaHekmati/music_embedding?include_prereleases&style=for-the-badge)](https://github.com/PooyaHekmati/music_embedding/releases)

© By SeyyedPooya HekmatiAthar 2021
Music Embedding is an open source python package for representing music data based on music theory. It provides tools to convert melodic and harmonic sequences to and from pianorolls.

Features
--------

- Representation for music intervals
- Create sequence of (harmonic or melodic) intervals from pianoroll presentation
- Create pianoroll from a sequence of (harmonic or melodic) intervals
- Break the sequence of intervals into smaller pieces e.g. bars
- Compress the sequence of intervals using Run Length Encoding (RLE)

Why Music Embedding
---------------
Embedding is an underexplored area in the intersection of AI and music. While many works try to apply NLP-based embedding and automatic embedding (such as convolution), representing music data based on music theory is important. Music Embedding package aims to make employment of music theory easy to enhance the computationals music projects' results. Some potential usecases are:
- Statistical and probabilistic analysis of music pieces,
- Developing generative models to have AI-synthesized music,
- Genre classificaion,
- Mood recognition,
- Melody extraction,
- Audio-to-Score alignment,
- Structure analysis.

Installation
------------

Music Embedding's only prerequisit is the Numpy package. Music Embedding is developed and tested in interaction with [Pypianoroll] (https://github.com/salu133445/pypianoroll); yet, any other code which can handle pianorolls should work just fine.

To install Music Embedding, please run `pip install music_embedding`. To build Music Embedding from source, please download the [source](https://github.com/PooyaHekmati/music_embedding/releases) and run `python setup.py install`.

Documentation
-------------

Currently, docstrings are the best source of documentation. An extensive documentation will be available soon.

License
-------------

This project is licensed under the MIT License - see the [LICENSE](https://github.com/PooyaHekmati/music_embedding/blob/main/LICENSE) file for details.

