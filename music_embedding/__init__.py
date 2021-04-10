"""A package for representing music data based on music theory.

Music Embedding is an open source python package for representing music data based on music theory. It provides tools to convert melodic and harmonic sequences to and from pianorolls.

Features
--------

- Representation for music intervals
- Create sequence of (harmonic or melodic) intervals from pianoroll presentation
- Create pianoroll from a sequence of (harmonic or melodic) intervals
- Break the sequence of intervals into smaller pieces e.g. bars
- Compress the sequence of intervals using Run Length Encoding (RLE)

"""
from . import interval, embedder