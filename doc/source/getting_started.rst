===============
Getting Started
===============

Welcome to Music Embedding! We will go through some basic concepts in this short tutorial.

.. Hint:: Be sure you have Music Embedding installed. To install Music Embedding, please run ``pip install music_embedding``.
.. Hint:: In this tutorial, we will use Pypianoroll to convert MIDI files into pianorolls. To install Pypianoroll, please run ``pip install pypianoroll``.

.. Hint:: In the tutorial, we will use `this MIDI file <https://github.com/PooyaHekmati/music_embedding/blob/main/Tests/music%20embedding%20example.mid>`_ as an example.

First of all, let's import the pypianoroll library and interval and embedder modules from music_embedding library. ::

    from music_embedding import interval, embedder
	import pypianoroll	

Now, let's read the example MIDI file into a Multitrack object. ::

    multitrack = pypianoroll.read("music embedding example.mid")

Let's create an embedder object and use it to get the melodic intervals of the first track. ::
	
	embedder_object = embedder.embedder()
	melodic_intervals = embedder_object.get_melodic_intervals_from_pianoroll(multitrack.tracks[0])
	print(melodic_intervals.shape)
	
Here's what we got: ::
	
	(384, 4)
	
The MIDI file we used has 4 4-beat bars. Pypianoroll assigns 24 pixels to each beat, so total number of pixels is *4*4*24 = 384*, which is the first dimension of our ``melodic intervals``. Music Embedding implements intervals using 4-dimension vectors, which is the second dimension of ``melodic_intervals``. These features are:

interval_order: int
	first to seventh
interval_type: int
	-2: dim, -1: min, 0: perfect, 1: Maj, 2: Aug
octave_offset : int8
	octave offset of a compound interval, 0 if interval is not compund
is_descending : boolean
	true if interval is descending

Let's create an interval object and use it to see the first `30` intervals in ``melodic_intervals``. ::

	interval_object = interval.interval()    
	for i in range(30):
		interval_object.set_specs_list(melodic_intervals[i])
		print(interval_object)		
		
The output is: ::

	Silence
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	Maj 2nd
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	perfect 1st
	
Melodic intervals are defined as the relatation between two consequtive notes. Since there is no note before the very first note, the very first note is shown as `silence`.

.. Hint:: When converting melodic intervals to pianorolls, argument ``origin`` defines the first note and everything will be calculated based on that. 

Since each note is stretched through multiple pianoroll pixels, when converted into intervals, each note appears as its true interval followed by multiple `perfect 1st` intervals. Let's fix this by applying Run-Length Encoding: ::

	melodic_intervals_rle = embedder_object.get_RLE_from_intervals(melodic_intervals)
	print (melodic_intervals_rle.shape)
	
Here's what we got: ::

	(46, 5)
	
The first dimension is the compressed `384` that we had before. The second dimension contains the four features of an interval plus the fifth dimension which shows how many repeatitions are summerized into one. Let's get a closer look: ::

	print('Count \t interval')
	print('-' * 17)
	for i in range(melodic_intervals_rle.shape[0]):
		interval_object.set_specs_list(melodic_intervals_rle[i, : -1])
		print(f'{melodic_intervals_rle[i,-1]} \t\t {interval_object}')
		
The output is: ::

	Count 	 interval
	-----------------
	1 	 Silence
	23 	 perfect 1st
	1 	 Maj 2nd
	23 	 perfect 1st
	1 	 Maj 2nd
	23 	 perfect 1st
	1 	 min 2nd
	23 	 perfect 1st
	1 	 Maj 2nd
	23 	 perfect 1st
	1 	 Maj 2nd
	23 	 perfect 1st
	1 	 Maj 2nd
	23 	 perfect 1st
	1 	 min 2nd
	22 	 perfect 1st
	1 	 Silence
	12 	 perfect 1st
	1 	 Descending perfect 8th
	11 	 perfect 1st
	1 	 Maj 7th
	23 	 perfect 1st
	1 	 Descending Maj 2nd
	11 	 perfect 1st
	1 	 Descending Maj 6th
	11 	 perfect 1st
	1 	 perfect 5th
	23 	 perfect 1st
	1 	 Descending Maj 2nd
	11 	 perfect 1st
	1 	 Descending min 3rd
	11 	 perfect 1st
	1 	 Maj 2nd
	23 	 perfect 1st
	1 	 Descending Maj 2nd
	11 	 perfect 1st
	1 	 Descending perfect 5th
	5 	 perfect 1st
	1 	 Maj 2nd
	5 	 perfect 1st
	1 	 Maj 2nd
	5 	 perfect 1st
	1 	 min 3rd
	5 	 perfect 1st
	1 	 Descending Maj 2nd
	11 	 perfect 1st