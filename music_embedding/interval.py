import numpy as np

class interval(object):
    """Implementation of interval concept in music theory.  
        
    Attributes
    ----------
    interval_order: int
        first to seventh
    interval_type: int
        -2: dim, -1: min, 0: perfect, 1: Maj, 2: Aug
    octave_offset : int8
        octave offset of a compound interval, 0 if interval is not compund.
    is_descending : boolean
            true if interval is descending.
    semitones: int
        Number of semitones in the interval.
    """

    feature_dimensions=4
    def __init__ (self,interval_order=1,interval_type=0,octave_offset=0,is_descending=0,semitones=0):
        self.interval_order=interval_order
        self.interval_type=interval_type
        self.octave_offset=octave_offset
        self.is_descending=is_descending
        self.semitones=semitones
        
    def semitone2interval(self, semitones=None):
        """Calculates the interval characterisics based on their semitone distance.
        
        Notes
        -----
        - Updates `self.semitones` if semitones is passed. 
        
        Semitone-interval Q-Table
            =========   ===============
            Semitones   Interval
            =========   ===============
            0           Perfect 1st
            1           minor 2nd
            2           Major 2nd
            3           minor 3rd
            4           Major 3rd
            5           Perfect 4th
            6           diminished 5th
            7           Perfect 5th
            8           minor 6th
            9           Major 6th
            10          minor 7th
            11          Major 7th  
            =========   ===============


        Parameters
        ----------
        semitones : int, optional
            Number of semitones in the interval.

        Returns
        -------
        dict, shape=(4)
            {'interval_order', 'interval_type', 'octave_offset', 'is_descending'}

        """
        if semitones is not None:
            self.semitones=semitones
        
        self.is_descending=0
        if self.semitones<0:
            self.is_descending=1
            self.semitones=-self.semitones
        
        self.octave_offset=self.semitones//12         #becuase 12th semitone is the octave
        remainder_semitones=self.semitones%12
    
        self.interval_order=1
        self.interval_type=0
        if remainder_semitones==0:          #implementing Q-table
            self.interval_order=1
            self.interval_type=0
        elif remainder_semitones==1:
            self.interval_order=2
            self.interval_type=-1
        elif remainder_semitones==2:
            self.interval_order=2
            self.interval_type=1
        elif remainder_semitones==3:
            self.interval_order=3
            self.interval_type=-1
        elif remainder_semitones==4:
            self.interval_order=3
            self.interval_type=1
        elif remainder_semitones==5:
            self.interval_order=4
            self.interval_type=0
        elif remainder_semitones==6:
            self.interval_order=5
            self.interval_type=-2
        elif remainder_semitones==7:
            self.interval_order=5
            self.interval_type=0
        elif remainder_semitones==8:
            self.interval_order=6
            self.interval_type=-1
        elif remainder_semitones==9:
            self.interval_order=6
            self.interval_type=1
        elif remainder_semitones==10:
            self.interval_order=7
            self.interval_type=-1
        elif remainder_semitones==11:
            self.interval_order=7
            self.interval_type=1
        
        return {'interval_order':self.interval_order,'interval_type':self.interval_type,'octave_offset':self.octave_offset,'is_descending':self.is_descending}

    def interval2semitone(self, specs=None):
        """Returns the distance between the two notes of the interval in semitones.  
        
        Notes
        -----
        - Updates intervals parameters if specs is passed.
        
        Faulty interval representation handling: 
            - if interval is 1st, 4th, or 5th and interval type is set to m or M, calculates P interval.
            - if interval is 2nd, 3rd, 6th, or 7th and interval type is set to P, calculates M interval.
               

        Parameters
        ----------
        specs : array, dtype=int, shape=(4), optional
            - interval_order=specs[0] (first to seventh)
            - interval_type=specs[1] (-2: dim, -1: min, 0: perfect, 1: Maj, 2: Aug )
            - is_descending=specs[2]
            - octave_offset=specs[3]

        Returns
        -------
        int
            Number of semitones in the interval

        """
        
        if specs is not None:
            self.set_specs_list(specs)
            
        self.semitones=0
            
        if self.interval_order==1:
            if self.interval_type==-2:
                self.semitones=-1
            elif self.interval_type==-1:
                self.semitones=0
            elif self.interval_type==0:
                self.semitones=0
            elif self.interval_type==1:
                self.semitones=0
            elif self.interval_type==2:
                self.semitones=1
            
        elif self.interval_order==2:           
            if self.interval_type==-2:
                self.semitones=0
            elif self.interval_type==-1:
                self.semitones=1
            elif self.interval_type==0:
                self.semitones=2
            elif self.interval_type==1:
                self.semitones=2
            elif self.interval_type==2:
                self.semitones=3
        
        elif self.interval_order==3:           
            if self.interval_type==-2:
                self.semitones=2
            elif self.interval_type==-1:
                self.semitones=3
            elif self.interval_type==0:
                self.semitones=4
            elif self.interval_type==1:
                self.semitones=4
            elif self.interval_type==2:
                self.semitones=5
                
        elif self.interval_order==4:           
            if self.interval_type==-2:
                self.semitones=4
            elif self.interval_type==-1:
                self.semitones=5
            elif self.interval_type==0:
                self.semitones=5
            elif self.interval_type==1:
                self.semitones=5
            elif self.interval_type==2:
                self.semitones=6
                
        elif self.interval_order==5:           
            if self.interval_type==-2:
                self.semitones=6
            elif self.interval_type==-1:
                self.semitones=7
            elif self.interval_type==0:
                self.semitones=7
            elif self.interval_type==1:
                self.semitones=7
            elif self.interval_type==2:
                self.semitones=8
                
        elif self.interval_order==6:           
            if self.interval_type==-2:
                self.semitones=7
            elif self.interval_type==-1:
                self.semitones=8
            elif self.interval_type==0:
                self.semitones=9
            elif self.interval_type==1:
                self.semitones=9
            elif self.interval_type==2:
                self.semitones=10
                
        elif self.interval_order==7:           
            if self.interval_type==-2:
                self.semitones=9
            elif self.interval_type==-1:
                self.semitones=10
            elif self.interval_type==0:
                self.semitones=11
            elif self.interval_type==1:
                self.semitones=11
            elif self.interval_type==2:
                self.semitones=12
            
        self.semitones+=self.octave_offset*12                  #adds multiplies of 12 to semitones becuase octave is 12 semitones
        
        if self.is_descending==1:       
            self.semitones=-self.semitones
            
        return int(self.semitones)
             
    def is_silence(self):
        """Determines if the interval represents silence.

        Returns
        -------
        boolean
            True if interval is silenmce, False otherwise.

        """
        return np.array_equal(self.get_specs_list(), interval.get_silence_specs_list())
    
    def get_specs_list(self):
        """Returns interval's characteristics.

        Returns
        -------
        list, dtype=int, shape=(4)
            [interval_order, interval_type, is_descending, octave_offset]

        """
        return [self.interval_order,self.interval_type,self.is_descending,self.octave_offset]
    
    def set_specs_list(self, specs):
        """Sets interval's characteristics.

        Parameters
        ----------
        specs : array, dtype=int, shape=(4)
            - interval_order=specs[0] (first to seventh)
            - interval_type=specs[1] (-2: dim, -1: min, 0: perfect, 1: Maj, 2: Aug )
            - is_descending=specs[2]
            - octave_offset=specs[3] 

        Returns
        -------
        None.

        """
        self.interval_order=specs[0]
        self.interval_type=specs[1]
        self.is_descending=specs[2]
        self.octave_offset=specs[3]
        
    def get_one_hot_specs_list(self):
        """Provides one-hot-encoding of the interval's order, type, and is decending. Octave offset is represented as an integer.
                    
        Returns
        -------
        dict, shape=(4)
            interval order (one-hot), interval type(one hot), is decending (boolean), octave offset (integer)
        """
        interval_order = [0] * 7
        interval_type = [0] * 5
        interval_order[self.interval_order - 1] = 1              #1 is subtracted to get the index; index starts at 0 while order starts at 1
        interval_type[self.interval_type + 2 ] = 1      #2 is added to get the index; index starts at 0 while type starts at -2
        return {'interval_order':interval_order, 'interval_type': interval_type, 'is_descending': self.is_descending, 'octave_offset': self.octave_offset}
        
    def set_one_hot_specs_list(self,interval_order,interval_type,is_descending,octave_offset):
        """Sets interval's characteristics.      

        Parameters
        ----------
        interval_order : array, dtype=int8, shape=(7)
            One-hot encoding representation of interval's order: 1st to 7th
        interval_type : array, dtype=int8, shape=(5)
            One-hot encoding representation of interval's type: 0: dim,-1: min, 2: perfect, 3: Maj, 4: Aug  
        is_descending : boolean
            true if interval is descending.
        octave_offset : int8
            octave offset of a compound interval, 0 if interval is not compund.

        Returns
        -------
        None.

        """
        self.interval_order=np.argmax(interval_order)+1 #1 is added to get the index; index starts at 0 while order starts at 1
        self.interval_type=np.argmax(interval_type)-2   #2 is subtracted to get the index; index starts at 0 while type starts at -2
        self.is_descending=is_descending
        self.octave_offset=octave_offset
    
    @staticmethod
    def get_silence_specs_list():
        """Representaion of a silence.

        Returns
        -------
        array, dtype=int8, shape=(interval.feature_dimensions)
            All zeros.

        """
        return [0]*interval().feature_dimensions
    
    def get_name(self, semitones=None):
        """Generates interval's name from inner representation.   

        Notes
        -----
        - Updates all `self parameters` if semitones is passed. 

        Parameters
        ----------
        semitones : int8, optional
            If passed, is used to generate the name. The default is None.

        Returns
        -------
        output : string
            Name of the interval.
        """
        if semitones is not None:
            self.semitones=semitones
            self.semitone2interval()
            
        if self.is_silence():
            return 'Silence'
        
        output=""
        if self.is_descending:
            output += "Descending "
        if self.interval_type == -2:
            output += "dim "
        elif self.interval_type == -1:
            output += "min "
        elif self.interval_type == 0:
            output += "perfect "
        elif self.interval_type == 1:
            output += "Maj "
        elif self.interval_type == 2:
            output += "Aug " 
        ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4]) #adopted from https://codegolf.stackexchange.com/questions/4707/outputting-ordinal-numbers-1st-2nd-3rd#answer-4712
        output += ordinal(self.interval_order + self.octave_offset * 7) 
        return output
    
    def __str__(self):
        return self.get_name()