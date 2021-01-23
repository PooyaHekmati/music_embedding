import numpy as np
from .interval import interval       
    
class embedder:
    """ The embedding class for musical data. Provides functionallities to convert pianorolls into intervals and vice versa (embedding). 
    
    Dependencies
    ----------
    Numpy as np
    interval class
    
    Attributes
    ----------
    pianoroll : ndarray, dtype=uint8, shape=(?, 128), optional
        First dimension is timesteps and second dimension is fixed 128 per MIDI standard. The default is None.
            
    intervals : ndarray, dtype=int8, shape=(?, interval.feature_dimensions), optional
        First dimension is timesteps and second dimension is interval features. The default is None.
            
    default_velocity : int
        When creating pianorolls this value is used for notes' velocities. The default is 100.
            
    origin : int
        The reference note of a melody; when decoding a melody, this indicates the first note. The default is 60.
            
    pixels_per_bar : int
        Number of pixels in each bar. Equals time signature's numarator multiplied by resolution per pixel. The default is 96.
    """
    def __init__ (self, pianoroll=None, intervals=None, default_velocity=100, origin=60, pixels_per_bar=96): 
        self.pianoroll=pianoroll
        self.intervals=intervals
        self.default_velocity=default_velocity 
        self.origin=origin
        self.pixels_per_bar=pixels_per_bar
    
    def extract_highest_pitch_notes_from_pianoroll(self, preserve_pianoroll=True): 
        """Does not perform any checks. Works on self.pianoroll, fill it before calling this function.  
        Example: Given the pianoroll of an SATB choir, returns Soprano notes.
        
        Parameters
        ----------
        preserve_pianoroll : boolean
            Determines if self.pianoroll needs to be preserved. Setting it to False slightly increases the performance.  
            
        Returns
        -------
        array, dtype=int64, shape=(?)
            Contains the highest pitch note at each timestep. Indicates silence with 0.
        """
        if preserve_pianoroll:
            pianoroll=np.copy(self.pianoroll)   #to make the process non-destructive and presereve the pianoroll
        else:
            pianoroll=self.pianoroll            #to make the process faster but in a destructive manner

        np.clip(pianoroll,0,1,out=pianoroll)    #clipping is applied to ensure coef works as expected.
        
        coef=np.arange(1,129,dtype=np.uint32)   #128 is the number of notes in MIDI, arange's stop is exclusive so it has to be 129                               
        for i in range(pianoroll.shape[0]):
            pianoroll[i,:]*=coef                #coef is a constantly growing series. Its multiplication is needed to ensure the note with the highest pitch is selected in a chord.
        
        return np.argmax(pianoroll,axis=1)        
        
    def get_melodic_intervals_from_pianoroll(self, pianoroll=None):
        """Does not perform any checks. Works on highest pitch notes in self.pianoroll, Updates self.pianoroll if pianoroll argument is passed. Updates self.intervals.
        Example: Given the pianoroll of an SATB choir, returns melodic intervals of Soprano.
        
        Parameters
        ----------
        pianoroll : ndarray, dtype=uint8, shape=(?, 128), optional
            If None, the function expects self.pianoroll to have value; else, it overwrites self.pianoroll. First dimension is timesteps and second dimension is fixed 128 per MIDI standard.
            
        Returns
        -------
        ndarray, dtype=int8, shape=(?, interval.feature_dimensions)
            First dimension is timesteps and second dimension is interval features.
            
        """        
        if pianoroll is not None:
            self.pianoroll=pianoroll
        
        notes=self.extract_highest_pitch_notes_from_pianoroll(self) #first get the notes of the melody
        
        self.intervals=np.zeros((len(notes)-1,interval.feature_dimensions),dtype=np.int8) #create the placeholder of intervals. Because origin is the first note of the melody, we need one less value.
        curser=interval()
        last_voice_index=0
        
        silent_interval = interval.get_silence_specs_list()
        
        if notes[0]==0:                         #if the first pixel is silence there is no interval to calculate
            self.intervals[0]=silent_interval
        for i in range(1,len(notes)):
            if notes[i]==0:                     #it is silence and there is no interval to calculate
                self.intervals[i-1]=silent_interval   
            else:
                curser.semitones=notes[i]-notes[last_voice_index]
                curser.semitone2interval()
                self.intervals[i-1]=curser.get_specs_list()
                last_voice_index=i
        return self.intervals        
    def pianoroll2intervals_melody(self):
        """
        This method is depricated.

        Returns
        -------
        Call to function:
            self.get_melodic_intervals_from_pianoroll()
            
        """
        return self.get_melodic_intervals_from_pianoroll()
    
    def get_pianoroll_from_melodic_intervals(self, intervals=None, origin=None, velocity=None, leading_silence=0):
        """Does not perform any checks. Works on self.intervals, Updates self.intervals if intervals argument is passed. Updates self.pianoroll.

        Parameters
        ----------
        intervals : ndarray, dtype=int8, shape=(?, interval.feature_dimensions), optional
            If None, the function expects self.intervals to have value; else, it overwrites self.intervals. First dimension is timesteps and second dimension is interval features.
            
        origin: int, optional
            The reference note of the melody; when decoding the melody, this indicates the first note. The default is self.origin.
            
        velocity : int, optional
           When creating pianorolls this value is used for notes' velocities. The default is self.default_velocity.
           
        leading_silence: int, optional
            Number of silent pixels at the beginning of the melody.

        Returns
        -------
        ndarray, dtype=uint8, shape=(?, 128)
            First dimension is timesteps and second dimension is fixed 128 per MIDI standard.

        """
        if intervals is not None:
            self.intervals=intervals
            
        if origin is None:
            origin=self.origin
            
        if velocity is None:
            velocity=self.default_velocity
            
        self.pianoroll=np.zeros((len(self.intervals)+1,128),dtype=np.uint8)   #128 is the number of notes in MIDI        
        self.pianoroll [ leading_silence, origin ]=velocity        
        
        curser=interval()
        curser.set_specs_list(self.intervals[leading_silence])
        if not curser.is_silence():
            origin += curser.interval2semitone()
            self.pianoroll [ leading_silence + 1, origin ] = velocity
            
        for i in range(leading_silence + 1, len(self.intervals)):
            curser.set_specs_list(self.intervals[i])
            if not curser.is_silence():   
                if not np.array_equal(self.intervals[i],self.intervals[i-1]):       #if they are different
                    origin+=curser.interval2semitone()
                self.pianoroll[i+1,origin]=velocity        
            
        return self.pianoroll
    def intervals2pianoroll_melody(self):
        """
        This method is depricated.

        Returns
        -------
        Call to function:
            self.get_pianoroll_from_melodic_intervals()

        """
        return self.get_pianoroll_from_melodic_intervals()
        
          
    def get_harmonic_intervals_from_pianoroll(self, ref_pianoroll, pianoroll=None): 
        """Does not perform any checks. Updates self.pianoroll if pianoroll argument is passed. Updates self.intervals.
        Calculates the harmonic intervals of the highest pitch notes in self.pianoroll with respect to ref_pianoroll.        

        Parameters
        ----------
        pianoroll : ndarray, dtype=uint8, shape=(?, 128), optional
            If None, the function expects self.pianoroll to have value; else, it overwrites self.pianoroll. First dimension is timesteps and second dimension is fixed 128 per MIDI standard.
            
        ref_pianoroll : ndarray, dtype=uint8, shape=(?, 128)
            Harmonic intervals are calculated with reference to this pianoroll.

        Returns
        -------
        ndarray, dtype=int8, shape=(?, interval.feature_dimensions)
            First dimension is timesteps and second dimension is interval features.
        """
        if pianoroll is not None:
            self.pianoroll=pianoroll
            
        notes=self.extract_highest_pitch_notes_from_pianoroll(self)
        self.intervals=np.zeros((len(notes),interval.feature_dimensions),dtype=np.int8)
        curser=interval()
        
        silent_interval = interval.get_silence_specs_list()
        
        for i in range(len(notes)):
            if notes[i]==0:                     #it is silence
                self.intervals[i]=silent_interval   
            else:
                ref_note=notes[i]-1
                while ref_note >= 0 and ref_pianoroll[i,ref_note] == 0:
                    ref_note-=1
                if ref_note >= 0:                    
                    curser.semitones=notes[i]-ref_note
                    curser.semitone2interval()
                    self.intervals[i]=curser.get_specs_list()
                else:
                    self.intervals[i]=silent_interval 
                
        return self.intervals
    def pianoroll2intervals_harmony(self):    
        """
        This method is depricated.

        Returns
        -------
        Call to function:
            self.get_harmonic_intervals_from_pianoroll()

        """
        return self.get_harmonic_intervals_from_pianoroll()

    
    def get_pianoroll_from_harmonic_intervals(self, pianoroll=None, intervals=None, velocity=None):
        """Does not perform any checks. Works on self.intervals, Updates self.intervals if intervals argument is passed. Updates self.pianoroll.
        Extracts highest pitch notes from self.pianoroll first, then builds a new pianoroll based on the extracted notes and self.intervals(harmonic).
        Example: Given ATB choir pianoroll and Soprano's harmonic intervals with respect to Alto, returns Soprano's pianoroll.

        Parameters
        ----------
        pianoroll : ndarray, dtype=uint8, shape=(?, 128), optional
            If None, the function expects self.pianoroll to have value; else, it overwrites self.pianoroll. First dimension is timesteps and second dimension is fixed 128 per MIDI standard.
            
        intervals : ndarray, dtype=int8, shape=(?, interval.feature_dimensions), optional
            If None, the function expects self.intervals to have value; else, it overwrites self.intervals. First dimension is timesteps and second dimension is interval features.
        
        velocity : int, optional
           When creating pianorolls this value is used for notes' velocities. The default is self.default_velocity.

        Returns
        -------
        ndarray, dtype=uint8, shape=(?, 128)
            First dimension is timesteps and second dimension is fixed 128 per MIDI standard.

        """
        if pianoroll is not None:
            self.pianoroll=pianoroll
            
        if intervals is not None:
            self.intervals=intervals
            
        if velocity is None:
            velocity=self.default_velocity
            
        ref_notes=self.extract_highest_pitch_notes_from_pianoroll(self)
        self.pianoroll=np.zeros((len(self.intervals),128),dtype=np.uint8)   #128 is the number of notes in MIDI
        curser=interval()
        for i in range (len(ref_notes)):
            if ref_notes[i] != 0:                               #if it is not silence
                curser.set_specs_list(self.intervals[i])
                note=curser.interval2semitone()
                self.pianoroll[i, ref_notes[i] + note]=velocity
        return self.pianoroll
    def intervals2pianoroll_harmony(self):
        """
        This method is depricated.

        Returns
        -------
        Call to function:
            self.get_pianoroll_from_harmonic_intervals()

        """
        return self.get_pianoroll_from_harmonic_intervals()

    
    def get_barwise_intervals_from_pianoroll(self, pianoroll=None, pixels_per_bar=None):
        """Does not perform any checks. Works on highest pitch notes in self.pianoroll, Updates self.pianoroll if pianoroll argument is passed. Updates self.intervals.
        Calculates intervals with respect to the first note of bar. For first notes the interval is calculated with respect to the first note of the last bar.
        
        Parameters
        ----------
        pianoroll : ndarray, dtype=uint8, shape=(?, 128), optional
            If None, the function expects self.pianoroll to have value; else, it overwrites self.pianoroll. First dimension is timesteps and second dimension is fixed 128 per MIDI standard.
        
        pixels_per_bar: int, optional
            Number of pixels in each bar. Equals time signature's numarator multiplied by resolution per pixel. The default is self.pixels_per_bar.
            
        Returns
        -------
        ndarray, dtype=int8, shape=(?, interval.feature_dimensions)
            First dimension is timesteps and second dimension is interval features.
            
        """     
        if pianoroll is not None:
            self.pianoroll=pianoroll
        
        if pixels_per_bar is None:
            pixels_per_bar=self.pixels_per_bar
            
        notes=self.extract_highest_pitch_notes_from_pianoroll(self) #get the notes of the melody
        self.intervals=np.zeros((len(notes),interval.feature_dimensions),dtype=np.int8) #create the placeholder of intervals. 
                
        last_bar_ref_note = -1      #init with an impossible value
        for note in notes:          #find first note
            if note!=0:
                last_bar_ref_note = note
                break
        if last_bar_ref_note == -1: #this means all notes are 0; there is nothing to process
            return self.intervals
                
        curser=interval()
        silent_interval = interval.get_silence_specs_list()
        
        for bar_number in range(int(len(notes)/pixels_per_bar)):        #traversing bars
            i=bar_number*pixels_per_bar                                   #init counter i with the first pixel of the bar
            while i<(bar_number + 1) * pixels_per_bar and notes[i]==0:    #finding the first note of the bar
                self.intervals[i]=silent_interval 
                i+=1
            
            if i<len(notes):                                        #this ensures i does not exceed array boundaries which might happen at the last pixel of the last bar.
                ref_note = notes[i]
            else:
                break
            
            curser.semitones=ref_note-last_bar_ref_note         #finding the interval of the first note of the current bar with respect to the first note of the last bar
            curser.semitone2interval()
            self.intervals[i]=curser.get_specs_list()
            last_bar_ref_note=ref_note
            
            for i in range(i+1, (bar_number + 1) * pixels_per_bar):
                if notes[i]==0:
                    self.intervals[i]=silent_interval 
                else:
                    curser.semitones=notes[i]-ref_note
                    curser.semitone2interval()
                    self.intervals[i]=curser.get_specs_list()

        return self.intervals
    

    def get_pianoroll_from_barwise_intervals(self, intervals=None, origin=None, velocity=None, leading_silence=0, pixels_per_bar=None):
        """Does not perform any checks. Works on self.intervals, Updates self.intervals if intervals argument is passed. Updates self.pianoroll.        

        Parameters
        ----------
        intervals : ndarray, dtype=int8, shape=(?, interval.feature_dimensions), optional
            If None, the function expects self.intervals to have value; else, it overwrites self.intervals. First dimension is timesteps and second dimension is interval features.
            
        origin: int, optional
            The reference note of the melody; when decoding the melody, this indicates the first note. The default is self.origin.
            
        velocity : int, optional
           When creating pianorolls this value is used for notes' velocities. The default is self.default_velocity.
            
        leading_silence: int, optional
            Number of silent pixels at the beginning of the melody.
            
        pixels_per_bar: int, optional
            Number of pixels in each bar. Equals time signature's numarator multiplied by resolution per pixel. The default is self.pixels_per_bar.

        Returns
        -------
        ndarray, dtype=uint8, shape=(?, 128)
            First dimension is timesteps and second dimension is fixed 128 per MIDI standard.

        """
        if intervals is not None:
            self.intervals=intervals
        
        if origin is None:
            origin=self.origin
            
        if velocity is None:
            velocity=self.default_velocity
            
        if pixels_per_bar is None:
            pixels_per_bar=self.pixels_per_bar
        
        self.pianoroll=np.zeros((len(self.intervals),128),dtype=np.uint8)   #128 is the number of notes in MIDI        
        self.pianoroll [ leading_silence, origin]=velocity
       
        curser=interval()            
        last_known_origin = origin
        origin_is_unkown=True
        for i in range(leading_silence, len(self.intervals)):
            if i % pixels_per_bar == 0:         #a new bar has started, we need to find its first note
                origin_is_unkown = True
                
            if origin_is_unkown: 
                curser.set_specs_list(self.intervals[i])                    #this is the interval of the first note of the current bar with respect to the first note of the last bar
                if not curser.is_silence():       #skip silences
                    origin = last_known_origin + curser.interval2semitone()     #finding the first note of the current bar
                    last_known_origin = origin
                    self.pianoroll [ i, origin ] = velocity
                    origin_is_unkown = False
            else: 
                curser.set_specs_list(self.intervals[i])
                if not curser.is_silence():      #skip silences                    
                    self.pianoroll [ i, origin + curser.interval2semitone() ] = velocity            
        return self.pianoroll
    
    def chunk_sequence_of_intervals(self, intervals=None, pixels_per_chunk=None):
        """Does not perform any checks. Works on self.intervals, Updates self.intervals if intervals argument is passed. 
        Recieves a long sequence of intervals and breaks it into chunks.        

        Parameters
        ----------
        intervals : ndarray, dtype=int8, shape=(?, interval.feature_dimensions), optional
            If None, the function expects self.intervals to have value; else, it overwrites self.intervals. First dimension is timesteps and second dimension is interval features.
            
        pixels_per_chunk: int, optional
            Number of pixels in each chunk. Set it to time signature's numarator multiplied by resolution per pixel to get chunk_per-bar. The default is self.pixels_per_bar.

        Returns
        -------
        ndarray, dtype=int8, shape=(?, pixels_per_chunk, interval.feature_dimensions)
            First dimension is bars, second dimension is pixels in each chunk and, third dimension is interval features.

        """
        if intervals is not None:
            self.intervals=intervals
            
        if pixels_per_chunk is None:
            pixels_per_chunk=self.pixels_per_bar
            
        return np.reshape(self.intervals, (self.intervals.shape[0]//pixels_per_chunk , pixels_per_chunk, self.intervals.shape[1] ))
    
    
    def merge_chunked_intervals(self, chunked_intervals):
        """Does not perform any checks. Updates self.intervals.
        Recieves chunks of interval sequences and merges them.

        Parameters
        ----------
        chunked_intervals : ndarray, dtype=int8, shape=(?, ?, interval.feature_dimensions)
            Merging happens along the first dimension and removes the second dimension.

        Returns
        -------
        ndarray, dtype=int8, shape=(?, interval.feature_dimensions)
            First dimension is timesteps and second dimension is interval features.

        """
        self.intervals=np.reshape(chunked_intervals, ( chunked_intervals.shape[0]*chunked_intervals.shape[1], chunked_intervals.shape[2]  ) )
        return self.intervals

    def get_RLE_from_intervals(self, intervals=None):
        """ Does not perform any checks. Works on self.intervals, Updates self.intervals if intervals argument is passed.       
        Compresses sequence of intervals using Run-Length Encoding.

        Parameters
        ----------
        intervals : ndarray, dtype=int8, shape=(?, interval.feature_dimensions), optional
            If None, the function expects self.intervals to have value; else, it overwrites self.intervals. First dimension is timesteps and second dimension is interval features.

        Returns
        -------
        ndarray, dtype=int32, shape=(?, interval.feature_dimensions + 1)
            First dimension is compressed timesteps. The last element in the second dimension indicates number of repeatitions for the rest of the elements in the second dimension.

        """
        if intervals is not None:
            self.intervals=intervals
        
        RLE=np.zeros((self.intervals.shape[0], self.intervals.shape[1] + 1), dtype=int)
        
        RLE[0,:self.intervals.shape[1]]=self.intervals[0]
        RLE[0,-1]=1
        index=0
        for i in range(1,self.intervals.shape[0]):
            if np.array_equal(self.intervals[i],self.intervals[i-1]):
                RLE[index,-1]+=1
            else:
                index+=1
                RLE[index,:self.intervals.shape[1]]=self.intervals[i]
                RLE[index,-1]=1
                
        return RLE[:index + 1,:]
    
    def get_intervals_from_RLE(self, RLE_data):
        """Does not perform any checks. Updates self.intervals.
        Uncompresses Run-Length Encoded intervals data.

        Parameters
        ----------
        RLE_data : ndarray, dtype=int32, shape=(?, interval.feature_dimensions + 1)
            First dimension is compressed timesteps. The last element in the second dimension indicates number of repeatitions for the rest of the elements in the second dimension.

        Returns
        -------
        ndarray, dtype=int8, shape=(?, interval.feature_dimensions)
            First dimension is timesteps and second dimension is interval features.

        """
        s=np.sum(RLE_data,axis=0)
        self.intervals=np.zeros( (s[-1],len(s)-1), dtype=np.int8 )
        index=0
        for i in range(RLE_data.shape[0]):
            replacement=np.repeat(RLE_data[i,:self.intervals.shape[1]],repeats=RLE_data[i,-1])            
            replacement=np.reshape(replacement,(RLE_data[i,-1],self.intervals.shape[1]),order='F')
            self.intervals[index:index+RLE_data[i,-1],:self.intervals.shape[1]]=replacement
            index+=RLE_data[i,-1]
        return self.intervals
    
    def get_RLE_from_intervals_bulk(self, bulk_intervals):
        """ Does not perform any checks.
        Bulk version of self.get_RLE_from_intervals.

        Parameters
        ----------
        bulk_intervals : ndarray, dtype=int8, shape=(?, pixels_per_chunk, interval.feature_dimensions)
            First dimension is chunks, second dimension is pixels in each chunk and, third dimension is interval features.

        Returns
        -------
        list
            List of RLE_compressed data, see self.get_intervals_from_RLE.

        """
        
        RLE_bulk=[]
        
        for intervals in bulk_intervals:
            RLE_bulk.append(self.get_RLE_from_intervals(intervals))        
                
        return RLE_bulk
    
    def get_intervals_from_RLE_bulk(self, bulk_RLE_data):
        """Does not perform any checks. 
        Bulk version of self.get_intervals_from_RLE.
    
        Parameters
        ----------
        bulk_RLE_data : list
            List of RLE_compressed data, see self.get_intervals_from_RLE.

        Returns
        -------
        ndarray, dtype=int8, shape=(?, pixels_per_chunk, interval.feature_dimensions)
            First dimension is chunks, second dimension is pixels in each chunk and, third dimension is interval features.

        """
        
        bulk_intervals=[]
        
        for RLE_data in bulk_RLE_data:
            bulk_intervals.append(self.get_intervals_from_RLE(RLE_data))         
        
        return bulk_intervals