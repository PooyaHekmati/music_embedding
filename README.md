Music Embedding
===============

[![Travis CI](https://www.travis-ci.com/PooyaHekmati/music_embedding.svg?branch=main)](https://www.travis-ci.com/github/PooyaHekmati/music_embedding)
[![Codecov](https://img.shields.io/codecov/c/github/PooyaHekmati/music_embedding)](https://codecov.io/gh/PooyaHekmati/music_embedding)
[![GitHub license](https://img.shields.io/github/license/PooyaHekmati/music_embedding)](https://github.com/PooyaHekmati/music_embedding/blob/main/LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/PooyaHekmati/music_embedding?include_prereleases)](https://github.com/PooyaHekmati/music_embedding/releases)
[![GitHub Stars](https://img.shields.io/github/stars/pooyahekmati/music_embedding)](https://github.com/PooyaHekmati/music_embedding/stargazers)
![Repo Size](https://img.shields.io/github/repo-size/pooyahekmati/music_embedding)
![Code Size](https://img.shields.io/github/languages/code-size/pooyahekmati/music_embedding)
[![Code Quality](https://img.shields.io/codefactor/grade/github/pooyahekmati/music_embedding)](https://www.codefactor.io/repository/github/pooyahekmati/music_embedding/overview/main)

By Pooya Hekmati 2021-24

Music Embedding is an open source python package for representing music data based on music theory. It provides tools to convert melodic and harmonic sequences to and from pianorolls.

Features
--------

- Representation of music intervals
- Create a sequence of (harmonic or melodic) intervals from pianoroll presentation
- Create pianoroll from a sequence of (harmonic or melodic) intervals
- Break the sequence of intervals into smaller pieces e.g. bars
- Compress the sequence of intervals using Run Length Encoding (RLE)

Why Music Embedding
-------------------
Embedding is an underexplored area in the intersection of AI and music. While many works try to apply NLP-based embedding and automatic embedding (such as convolution), representing music data based on music theory is important. Music Embedding package aims to make employment of music theory easy to enhance the computationals music projects' results. Some potential use cases are:
- Statistical and probabilistic analysis of music pieces,
- Developing generative models to have AI-synthesized music,
- Genre classification,
- Mood recognition,
- Melody extraction,
- Audio-to-Score alignment,
- Score structure analysis.

Installation
------------

Music Embedding's only prerequisite is the Numpy package. Music Embedding is developed and tested in interaction with [Pypianoroll](https://github.com/salu133445/pypianoroll); yet, any other code which can handle pianorolls should work just fine.

To install Music Embedding, please run `pip install music_embedding`. To build Music Embedding from source, please download the [source](https://github.com/PooyaHekmati/music_embedding/releases) and run `python setup.py install`.

Semantic Versioning Policy
--------------------------

Music Embedding uses the x.y.z format to indicate the version where x is the major version number, y is the minor version number, and z is the patch number.

Documentation
-------------

Documentation is available [here](https://pooyahekmati.github.io/music_embedding) and as docstrings with the code.

Citing
------

Please cite [this paper](https://arxiv.org/abs/2104.11880) if you use Music Embedding in a published work.

Usage
-----
Please visit the [Getting Started](https://pooyahekmati.github.io/music_embedding/getting_started.html) page.

The following code snippet demonstrates how to convert a midi file into a sequence of harmonic intervals.

```python
import music_embedding
import pypianoroll

if __name__ == '__main__':
    #opening midi file using pypianoroll
    midi_path = r'c:\Moonlight Sonata.mid'
    multi_track = pypianoroll.read(midi_path) 
    
    #mergeing midi tracks into a single pianoroll so harmonic intervals can be extracted
    merged_piano_roll = multi_track.blend('max') 
    
    #getting pianoroll of the first track
    pianoroll = multi_track.tracks[0].pianoroll
    
    #creating embedder object from music embedding package
    embedder = music_embedding.embedder.embedder()        
    
    #extracting harmonic intervals
    harmonic_intervals = embedder.get_harmonic_intervals_from_pianoroll(pianoroll=pianoroll, ref_pianoroll=merged_piano_roll)
    
    #creating interval object from music embedding package
    interval = music_embedding.interval.interval()
    
    #printing the first 20 intervals
    for i in range(20):
        interval.set_specs_list(harmonic_intervals[i])
        print(interval)
```

Issues
------

If you find a problem, please [file a bug](https://github.com/PooyaHekmati/music_embedding/issues/new).

License
-------

This project is licensed under the MIT License - see the [LICENSE](https://github.com/PooyaHekmati/music_embedding/blob/main/LICENSE) file for details.

