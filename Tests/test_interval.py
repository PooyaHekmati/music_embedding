from music_embedding.interval import interval
import pytest

def test_interval2semitone():
    assert interval().interval2semitone([1,0,0,0]) == 0
    assert interval().interval2semitone([2,-1,0,0]) == 1
    assert interval().interval2semitone([2,1,0,0]) == 2
    assert interval().interval2semitone([3,-1,0,0]) == 3
    assert interval().interval2semitone([3,1,0,0]) == 4
    assert interval().interval2semitone([4,0,0,0]) == 5
    assert interval().interval2semitone([5,-2,0,0]) == 6
    assert interval().interval2semitone([5,0,0,0]) == 7
    assert interval().interval2semitone([6,-1,0,0]) == 8
    assert interval().interval2semitone([6,1,0,0]) == 9
    assert interval().interval2semitone([7,-1,0,0]) == 10
    assert interval().interval2semitone([7,1,0,0]) == 11
    assert interval().interval2semitone([0,0,0,1]) == 12
    assert interval().interval2semitone([0,0,1,1]) == -12
    
def test_semitone2interval():
    for i in range(-30, 30):
        assert interval().interval2semitone(interval().semitone2interval(i)) == i
    
def test_is_silence():
    interval_obj = interval()
    interval_obj.set_specs_list(interval_obj.get_silence_specs_list())
    assert interval_obj.is_silence()
    
def test_get_specs_list():
    interval_obj = interval()
    interval_obj.set_specs_list([3,2,1,0])
    assert interval_obj.get_specs_list() == [3,2,1,0]
    
def test_set_specs_list():
    with pytest.raises(ValueError):
        interval().interval2semitone([-1,0,0,0])
    with pytest.raises(ValueError):
        interval().interval2semitone([8,0,0,0])
    
    with pytest.raises(ValueError):
        interval().interval2semitone([0,-3,0,0])
    with pytest.raises(ValueError):
        interval().interval2semitone([0,3,0,0])
        
    with pytest.raises(ValueError):
        interval().interval2semitone([0,0,-1,0])
    with pytest.raises(ValueError):
        interval().interval2semitone([0,0,2,0])
    
    with pytest.raises(ValueError):
        interval().interval2semitone([0,0,0,-1])
    with pytest.raises(ValueError):
        interval().interval2semitone([0,0,0,10])
    
def test_get_one_hot_specs_list():
    interval_obj = interval()
    interval_obj.set_specs_list([3,2,1,0])
    expected = {'interval_order': [0, 0, 1, 0, 0, 0, 0],
                 'interval_type': [0, 0, 0, 0, 1],
                 'is_descending': 1,
                 'octave_offset': 0}
    assert interval_obj.get_one_hot_specs_list() == expected
    
def test_set_one_hot_specs_list():
    interval_obj = interval()
    interval_obj.set_one_hot_specs_list( [0, 0, 1, 0, 0, 0, 0],[0, 0, 0, 0, 1],1,0)
    assert interval_obj.get_specs_list() == [3,2,1,0]
    
def test_get_silence_specs_list():
    interval_obj = interval()
    interval_obj.set_specs_list(interval_obj.get_silence_specs_list())
    assert interval_obj.is_silence()
    
# def test_get_name():
#     assert True
    
    