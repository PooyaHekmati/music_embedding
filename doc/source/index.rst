Music Embedding
===============

.. image:: https://img.shields.io/github/workflow/status/PooyaHekmati/music_embedding/Testing
    :target: https://github.com/PooyaHekmati/music_embedding/actions
    :alt: GitHub workflow
.. image:: https://www.travis-ci.com/PooyaHekmati/music_embedding.svg?branch=main
    :target: https://www.travis-ci.com/github/PooyaHekmati/music_embedding
    :alt: Travis CI
.. image:: https://img.shields.io/codecov/c/github/PooyaHekmati/music_embedding
    :target: https://codecov.io/gh/PooyaHekmati/music_embedding
    :alt: Codecov
.. image:: https://img.shields.io/github/license/PooyaHekmati/music_embedding
    :target: https://github.com/PooyaHekmati/music_embedding/blob/main/LICENSE
    :alt: GitHub license
.. image:: https://img.shields.io/github/v/release/PooyaHekmati/music_embedding?include_prereleases
    :target: https://github.com/PooyaHekmati/music_embedding/releases
    :alt: GitHub release
.. image:: https://img.shields.io/github/stars/pooyahekmati/music_embedding
    :target: https://github.com/PooyaHekmati/music_embedding/stargazers
    :alt: GitHub Stars
.. image:: https://img.shields.io/github/repo-size/pooyahekmati/music_embedding
    :target: #
    :alt: Repo Size
.. image:: https://img.shields.io/github/languages/code-size/pooyahekmati/music_embedding
    :target: #
    :alt: Code Size
.. image:: https://img.shields.io/codefactor/grade/github/pooyahekmati/music_embedding
    :target: https://www.codefactor.io/repository/github/pooyahekmati/music_embedding/overview/main
    :alt: Code Quality
    
Music Embedding is an open source python package for representing music data based on music theory. It provides tools to convert melodic and harmonic sequences to and from pianorolls.

Features
--------

- Representation for music intervals
- Create sequence of (harmonic or melodic) intervals from pianoroll presentation
- Create pianoroll from a sequence of (harmonic or melodic) intervals
- Break the sequence of intervals into smaller pieces e.g. bars
- Compress the sequence of intervals using Run Length Encoding (RLE)

Why Music Embedding
-------------------
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

Music Embedding's only prerequisit is the Numpy package. Music Embedding is developed and tested in interaction with `Pypianoroll <https://github.com/salu133445/pypianoroll>`_ ; yet, any other code which can handle pianorolls should work just fine.

To install Music Embedding, please run ``pip install music_embedding``. To build Music Embedding from source, please download the `source <https://github.com/PooyaHekmati/music_embedding/releases>`_ and run ``python setup.py install``.

Semantic Versioning Policy
--------------------------

Music Embedding uses x.y.z format to indicate the version where x is major versin number, y is minor version number, and z is the patch number. 

Classes Documentation
---------------------

For detailed documenation please visit:
	- `interval <interval.html>`_
	- `embedder <embedder.html>`_

Usage
-----
Please visit the `getting started <getting_started.html>`_ page.

The following code snippet demonstrates how to convert a midi file into a sequence of harmonic intervals. ::

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
		embedder = music_embedding.embedder()        
		
		#extracting harmonic intervals
		harmonic_intervals = embedder.get_harmonic_intervals_from_pianoroll(pianoroll=pianoroll, ref_pianoroll=merged_piano_roll)
		
		#creating interval object from music embedding package
		interval = music_embedding.interval()
		
		#printing the first 20 intervals
		for i in range(20):
			interval.set_specs_list(harmonic_intervals[i])
			print(interval)


Issues
------

If you find a problem, please `file a bug <https://github.com/PooyaHekmati/music_embedding/issues/new>`_.

License
-------

This project is licensed under the MIT License - see the `LICENSE <https://github.com/PooyaHekmati/music_embedding/blob/main/LICENSE>`_ file for details.
