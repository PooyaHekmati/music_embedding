from music_embedding.interval import interval
from music_embedding.embedder import embedder
import pytest
import numpy as np

def test__get_none_error_message():
    assert embedder()._get_none_error_message("test") == "Both test argument and self.test are None."

def test__get_range_error_message():
    assert embedder()._get_range_error_message() == "Attempted to assign an out of range value. MIDI accepts values in the range 0-127."

def test__get_incompatible_dimension_error_message():
    assert embedder()._get_incompatible_dimension_error_message("pianoroll") == "Wrong pianoroll shape, second dimension must be 128."
    assert embedder()._get_incompatible_dimension_error_message("intervals") == f"Wrong intervals shape, second dimension must be interval.feature_dimensions ({interval().feature_dimensions})."
    with pytest.raises(ValueError):
        embedder._get_incompatible_dimension_error_message("invalid_input")
        
def test_extract_highest_pitch_notes_from_pianoroll_error_handling(): 
    emb = embedder()
    with pytest.raises(TypeError):
        emb.extract_highest_pitch_notes_from_pianoroll()
    
    emb.pianoroll = np.zeros((1,1))
    with pytest.raises(IndexError):
        emb.extract_highest_pitch_notes_from_pianoroll()
    
def test_extract_highest_pitch_notes_from_pianoroll(): 
    assert True      
    
def test_get_melodic_intervals_from_pianoroll():
    assert True 

def test_get_pianoroll_from_melodic_intervals():
    assert True    
     
def test_get_harmonic_intervals_from_pianoroll(): 
    assert True
    

def test_get_pianoroll_from_harmonic_intervals():
    assert True
    

def test_get_barwise_intervals_from_pianoroll():
    assert True

def test_get_pianoroll_from_barwise_intervals():
    assert True

def test_chunk_sequence_of_intervals():
    assert True

def test_merge_chunked_intervals():
    assert True

def test_get_RLE_from_intervals():
    assert True

def test_get_intervals_from_RLE():
    assert True

def test_get_RLE_from_intervals_bulk():
    assert True
    
def test_get_intervals_from_RLE_bulk():
    assert True