import numpy as np
from .interval import interval


class embedder:
    """
    A class for embedding musical data, providing functionalities to convert between pianoroll representations
    and interval-based representations.

    This class handles various operations related to musical data manipulation, including extracting notes from
    pianorolls, converting pianoroll data to melodic, harmonic, and barwise intervals, and vice versa. Additionally,
    it supports Run-Length Encoding (RLE) compression for intervals.

    Attributes
    ----------
    pianoroll : ndarray, dtype=uint8, shape=(?, 128), optional
        Pianoroll representation of musical data. The first dimension represents timesteps, and the second dimension
        has a fixed size of 128, corresponding to MIDI standards.
    intervals : ndarray, dtype=int8, shape=(?, interval.feature_dimensions), optional
        Interval representation of musical data. The first dimension represents timesteps, and the second dimension
        corresponds to interval features.
    default_velocity : int
        Default velocity used for notes in pianoroll representation. Defaults to 100.
    origin : int
        Reference note for melody, used as the starting note when decoding a melody. Defaults to 60 (Middle C in MIDI)
    pixels_per_bar : int
        Number of pixels representing each bar in a pianoroll, calculated as the time signature's numerator multiplied
        by the resolution per pixel. Defaults to 96.


    See Also
    --------
    interval : Class used for interval-related calculations.

    """

    def __init__(
        self,
        pianoroll=None,
        intervals=None,
        default_velocity=100,
        origin=60,
        pixels_per_bar=96,
    ):
        self.pianoroll = pianoroll
        self.intervals = intervals
        self.default_velocity = default_velocity
        self.origin = origin
        self.pixels_per_bar = pixels_per_bar

    def _get_none_error_message(self, var_name: str) -> str:
        return f"Both {var_name} argument and self.{var_name} are None."

    def _get_range_error_message(self) -> str:
        return "Attempted to assign an out of range value. MIDI accepts values in the range 0-127."

    def _get_incompatible_dimension_error_message(self, variable_name: str) -> str:
        if variable_name == "pianoroll":
            return "Wrong pianoroll shape, second dimension must be 128."
        if variable_name == "intervals":
            return (
                "Wrong intervals shape, second dimension must be interval.feature_dimensions "
                f"({interval().feature_dimensions})."
            )
        raise ValueError("Unrecognized variable name")

    def extract_highest_pitch_notes_from_pianoroll(
        self, preserve_pianoroll: bool = True
    ) -> np.ndarray:
        """
        Extracts the highest pitch note at each timestep from the pianoroll attribute.

        This method processes the `self.pianoroll` array to find the highest pitch note for each timestep.
        It can operate in either a non-destructive mode, preserving the original pianoroll, or a faster,
        destructive mode that alters the original data.

        **Example:** Given the pianoroll of an SATB choir, returns Soprano notes.

        Parameters
        ----------
        preserve_pianoroll : bool, optional
            Determines if `self.pianoroll` should be preserved.
            Setting it to False increases performance by avoiding data copying. Default is True.

        Raises
        ------
        TypeError
            If `self.pianoroll` is None.
        IndexError
            If `self.pianoroll` does not have the second dimension size of 128.

        Returns
        -------
        ndarray, dtype=int64, shape=(?)
            An array containing the highest pitch note at each timestep. Indicates silence with a value of 0.

        Notes
        -----
        The method operates on `self.pianoroll` and requires it to be filled before calling.
        The pianoroll format is expected to conform to MIDI standards with 128 pitches.
        """

        if self.pianoroll is None:
            raise TypeError("self.pianoroll is None.")
        if self.pianoroll.shape[1] != 128:
            raise IndexError(
                self._get_incompatible_dimension_error_message("pianoroll")
            )

        if preserve_pianoroll:
            pianoroll = np.copy(
                self.pianoroll
            )  # to make the process non-destructive and presereve the pianoroll
        else:
            pianoroll = (
                self.pianoroll
            )  # to make the process faster but in a destructive manner

        pianoroll = pianoroll.astype(np.uint8)  # to prevent overflowing

        np.clip(
            pianoroll, 0, 1, out=pianoroll
        )  # clipping is applied to ensure coef works as expected.

        coef = np.arange(
            1, 129, dtype=np.uint32
        )  # 128 is the number of notes in MIDI, arange's stop is exclusive so it has to be 129
        for i in range(pianoroll.shape[0]):
            pianoroll[i, :] *= coef
            # coef is a constantly growing series. Its multiplication is needed to ensure the note with
            # the highest pitch is selected in a chord.

        return np.argmax(pianoroll, axis=1)

    def get_melodic_intervals_from_pianoroll(
        self, pianoroll: np.ndarray | None = None
    ) -> np.ndarray:
        """
        Creates a sequence of melodic intervals from a pianoroll.

        This method calculates the melodic intervals of the highest pitch notes in the pianoroll.
        If a pianoroll is provided as an argument, it updates `self.pianoroll` with this new data.
        The resulting intervals are stored in `self.intervals`.

        **Example:** Given the pianoroll of an SATB choir, returns melodic intervals of Soprano.

        Parameters
        ----------
        pianoroll : ndarray, dtype=uint8, shape=(?, 128), optional
            Pianoroll to be processed. If not provided, the method uses `self.pianoroll`. The first dimension represents
            timesteps, and the second dimension is fixed to 128, corresponding to MIDI standards.

        Returns
        -------
        ndarray, dtype=int8, shape=(?, interval.feature_dimensions)
            Array of melodic intervals. The first dimension represents timesteps, and the second dimension corresponds
            to interval features.

        Raises
        ------
        TypeError
            If both the pianoroll argument and `self.pianoroll` are None.
        IndexError
            If the provided pianoroll (or `self.pianoroll` if pianoroll is None) does not have a second dimension of
            size 128.
        """
        if pianoroll is not None:
            self.pianoroll = pianoroll
        else:
            if self.pianoroll is None:
                raise TypeError(self._get_none_error_message("pianoroll"))
        if self.pianoroll.shape[1] != 128:
            raise IndexError(
                self._get_incompatible_dimension_error_message("pianoroll")
            )

        notes = (
            self.extract_highest_pitch_notes_from_pianoroll()
        )  # first get the notes of the melody

        self.intervals = np.zeros(
            (len(notes), interval.feature_dimensions), dtype=np.int8
        )  # create the placeholder of intervals.
        curser = interval()
        last_voice_index = 0

        silent_interval = interval.get_silence_specs_list()

        if (
            notes[0] == 0
        ):  # if the first pixel is silence there is no interval to calculate
            self.intervals[1] = silent_interval
            # The first melodic interval is always zeros. This is becuase melody is calcualted with
            # respect to the previous note.
        for i in range(1, len(notes)):
            if notes[i] == 0:  # it is silence and there is no interval to calculate
                self.intervals[i] = silent_interval
            else:
                curser.semitones = notes[i] - notes[last_voice_index]
                curser.semitone2interval()
                self.intervals[i] = curser.get_specs_list()
                last_voice_index = i
        return self.intervals

    def get_pianoroll_from_melodic_intervals(
        self,
        intervals: np.ndarray | None = None,
        origin: int | None = None,
        velocity: int | None = None,
        leading_silence: int = 0,
    ) -> np.ndarray:
        """
        Creates a pianoroll from a sequence of melodic intervals.

        This method generates a pianoroll representation of a melody based on the provided sequence of melodic
        intervals. The origin note is used as the starting point for the melody, and the specified velocity is
        applied to the notes.

        Parameters
        ----------
        intervals : ndarray, dtype=int8, shape=(?, interval.feature_dimensions), optional
            Sequence of melodic intervals. If None, the method uses self.intervals.
            Each row represents interval features for a timestep.
        origin : int, optional
            The reference note of the melody; used as the starting note for decoding the melody.
            Defaults to self.origin if None.
        velocity : int, optional
            Velocity used for notes in the pianoroll. Defaults to self.default_velocity if None.
        leading_silence : int, optional
            Number of silent pixels at the beginning of the melody. Defaults to 0.

        Raises
        ------
        TypeError
            If both intervals argument and self.intervals are None.
        IndexError
            If intervals.shape[1] != interval.feature_dimensions or if the sequence of given intervals leads to a
            note outside the MIDI range (0-127).
        ValueError
            If leading_silence is greater than or equal to the number of intervals.

        Returns
        -------
        ndarray, dtype=uint8, shape=(?, 128)
            Pianoroll representation of the melody. The first dimension represents timesteps, and the second dimension
            is fixed to 128, corresponding to MIDI standards.
        """

        if intervals is not None:
            self.intervals = intervals
        else:
            if self.intervals is None:
                raise TypeError(self._get_none_error_message("intervals"))
        if self.intervals.shape[1] != interval().feature_dimensions:
            raise IndexError(
                self._get_incompatible_dimension_error_message("intervals")
            )

        if leading_silence >= len(self.intervals):
            raise ValueError("Leading silences must be less than intervals.")

        if origin is None:
            origin = self.origin
        if origin > 127 or origin < 0:
            raise IndexError(self._get_range_error_message())

        if velocity is None:
            velocity = self.default_velocity
        if velocity > 127 or velocity < 0:
            raise IndexError(self._get_range_error_message())

        self.intervals = self.intervals[
            1:, :
        ]  # removing the first row of zeros. This is becuase melody is calcualted with respect to the previous note.

        self.pianoroll = np.zeros(
            (len(self.intervals) + 1, 128), dtype=np.uint8
        )  # 128 is the number of notes in MIDI
        self.pianoroll[leading_silence, origin] = velocity

        curser = interval()
        curser.set_specs_list(self.intervals[leading_silence])
        if not curser.is_silence():
            origin += curser.interval2semitone()
            if origin > 127 or origin < 0:
                raise IndexError(self._get_range_error_message())
            self.pianoroll[leading_silence + 1, origin] = velocity

        semitones = 0
        for i in range(leading_silence + 1, len(self.intervals)):
            curser.set_specs_list(self.intervals[i])
            if not curser.is_silence():
                if not np.array_equal(
                    self.intervals[i], self.intervals[i - 1]
                ):  # if they are different calculate semitones, otherwise use prev value
                    semitones = curser.interval2semitone()
                origin += semitones
                if origin > 127 or origin < 0:
                    raise IndexError(self._get_range_error_message())
                self.pianoroll[i + 1, origin] = velocity

        return self.pianoroll

    def get_harmonic_intervals_from_pianoroll(self, ref_pianoroll, pianoroll=None):
        """Creates sequence of harmonic intervals from pianoroll.

        Calculates the harmonic intervals of the highest pitch notes in self.pianoroll with respect to ref_pianoroll.

        Notes
        -----
        - Works on `self.pianoroll`.
        - Updates `self.pianoroll` if pianoroll argument is passed.
        - Updates `self.intervals`.

        Parameters
        ----------
        pianoroll : ndarray, dtype=uint8, shape=(?, 128), optional
            If None, the function expects self.pianoroll to have value; else, it overwrites self.pianoroll. First dimension is timesteps and second dimension is fixed 128 per MIDI standard.

        ref_pianoroll : ndarray, dtype=uint8, shape=(?, 128)
            Harmonic intervals are calculated with reference to this pianoroll.

        Raises
        --------
        Type Error: if both pianoroll argument and self.pianoroll are None.
        Index Error: if pianoroll.shape[1] != 128 [if pianoroll=None then raises if self.pianoroll.shape[1] != 128]
        Index Error: if ref_pianoroll.shape[1] != 128

        Returns
        -------
        ndarray, dtype=int8, shape=(?, interval.feature_dimensions)
            First dimension is timesteps and second dimension is interval features.
        """
        if pianoroll is not None:
            self.pianoroll = pianoroll
        else:
            if self.pianoroll is None:
                raise TypeError(self._get_none_error_message("pianoroll"))
        if self.pianoroll.shape[1] != 128:
            raise IndexError(
                self._get_incompatible_dimension_error_message("pianoroll")
            )

        if ref_pianoroll.shape[1] != 128:
            raise IndexError(
                self._get_incompatible_dimension_error_message("pianoroll")
            )

        notes = self.extract_highest_pitch_notes_from_pianoroll()
        self.intervals = np.zeros(
            (len(notes), interval.feature_dimensions), dtype=np.int8
        )
        curser = interval()

        silent_interval = interval.get_silence_specs_list()

        # for i in range(len(notes)):
        for i, note in enumerate(notes):
            if note == 0:  # it is silence
                self.intervals[i] = silent_interval
            else:
                ref_note = note - 1
                while ref_note >= 0 and ref_pianoroll[i, ref_note] == 0:
                    ref_note -= 1
                if ref_note >= 0:
                    curser.semitones = note - ref_note
                    curser.semitone2interval()
                    self.intervals[i] = curser.get_specs_list()
                else:
                    self.intervals[i] = silent_interval

        return self.intervals

    def get_pianoroll_from_harmonic_intervals(
        self, pianoroll=None, intervals=None, velocity=None
    ):
        """Creates pianoroll from sequence of harmonic intervals.

        Extracts highest pitch notes from pianoroll first, then builds a new pianoroll based on the extracted notes and self.intervals(harmonic).

        **Example:** Given ATB choir pianoroll and Soprano's harmonic intervals with respect to Alto, returns Soprano's pianoroll.

        Notes
        -----
        - Works on `self.intervals`.
        - Updates `self.intervals` if intervals argument is passed.
        - Updates `self.pianoroll`.

        Parameters
        ----------
        pianoroll : ndarray, dtype=uint8, shape=(?, 128), optional
            If None, the function expects self.pianoroll to have value; else, it overwrites self.pianoroll. First dimension is timesteps and second dimension is fixed 128 per MIDI standard.

        intervals : ndarray, dtype=int8, shape=(?, interval.feature_dimensions), optional
            If None, the function expects self.intervals to have value; else, it overwrites self.intervals. First dimension is timesteps and second dimension is interval features.

        velocity : int, optional
           When creating pianorolls this value is used for notes' velocities. The default is self.default_velocity.

        Raises
        --------
        Type Error: if both intervals argument and self.intervals are None.
        Index Error: if intervals.shape[1] != interval.feature_dimensions [if intervals=None then raises if self.intervals.shape[1] != interval.feature_dimensions]
        Type Error: if both pianoroll argument and self.pianoroll are None.
        Index Error: if pianoroll.shape[1] != 128 [if pianoroll=None then raises if self.pianoroll.shape[1] != 128]
        Index Error: if velocity > 127 or velocity < 0. If velocity is None then self.default_velocity is substituted.
        Index Error: if adding the interval to the pianoroll leads to to a note which is out of MIDI range (0-127).

        Returns
        -------
        ndarray, dtype=uint8, shape=(?, 128)
            First dimension is timesteps and second dimension is fixed 128 per MIDI standard.

        """
        if pianoroll is not None:
            self.pianoroll = pianoroll
        else:
            if self.pianoroll is None:
                raise TypeError(self._get_none_error_message("pianoroll"))
        if self.pianoroll.shape[1] != 128:
            raise IndexError(
                self._get_incompatible_dimension_error_message("pianoroll")
            )

        if intervals is not None:
            self.intervals = intervals
        else:
            if self.intervals is None:
                raise TypeError(self._get_none_error_message("intervals"))
        if self.intervals.shape[1] != interval().feature_dimensions:
            raise IndexError(
                self._get_incompatible_dimension_error_message("intervals")
            )

        if velocity is None:
            velocity = self.default_velocity
        if velocity > 127 or velocity < 0:
            raise IndexError(self._get_range_error_message())

        ref_notes = self.extract_highest_pitch_notes_from_pianoroll()
        self.pianoroll = np.zeros(
            (len(self.intervals), 128), dtype=np.uint8
        )  # 128 is the number of notes in MIDI
        curser = interval()
        # for i in range (len(ref_notes)):
        for i, ref_note in enumerate(ref_notes):
            if ref_note != 0:  # if it is not silence
                curser.set_specs_list(self.intervals[i])
                note = curser.interval2semitone()
                if ref_note + note > 127 or ref_note + note < 0:
                    raise IndexError(self._get_range_error_message())
                self.pianoroll[i, ref_note + note] = velocity
        return self.pianoroll

    def get_barwise_intervals_from_pianoroll(self, pianoroll=None, pixels_per_bar=None):
        """Creates sequence of barwise intervals from pianoroll.

        Calculates intervals with respect to the first note of the current bar. For first notes of bars, the interval is calculated with respect to the first note of the last bar.

        Notes
        -----
        - Works on highest pitch notes in `self.pianoroll`.
        - Updates `self.pianoroll` if pianoroll argument is passed.
        - Updates `self.intervals`.

        Parameters
        ----------
        pianoroll : ndarray, dtype=uint8, shape=(?, 128), optional
            If None, the function expects self.pianoroll to have value; else, it overwrites self.pianoroll. First dimension is timesteps and second dimension is fixed 128 per MIDI standard.

        pixels_per_bar: int, optional
            Number of pixels in each bar. Equals time signature's numarator multiplied by resolution per pixel. The default is self.pixels_per_bar.

        Raises
        --------
        Type Error: if both pianoroll argument and self.pianoroll are None.
        Index Error: if pianoroll.shape[1] != 128 [if pianoroll=None then raises if self.pianoroll.shape[1] != 128]
        Value Error: if pixels_per_bar < 1. If pixels_per_bar is None then self.pixels_per_bar is substituted.

        Returns
        -------
        ndarray, dtype=int8, shape=(?, interval.feature_dimensions)
            First dimension is timesteps and second dimension is interval features.

        """
        if pianoroll is not None:
            self.pianoroll = pianoroll
        else:
            if self.pianoroll is None:
                raise TypeError(self._get_none_error_message("pianoroll"))
        if self.pianoroll.shape[1] != 128:
            raise IndexError(
                self._get_incompatible_dimension_error_message("pianoroll")
            )

        if pixels_per_bar is None:
            pixels_per_bar = self.pixels_per_bar
        if pixels_per_bar < 1:
            raise ValueError("Number of pixels in bar must be a positive integer.")

        notes = (
            self.extract_highest_pitch_notes_from_pianoroll()
        )  # get the notes of the melody
        self.intervals = np.zeros(
            (len(notes), interval.feature_dimensions), dtype=np.int8
        )  # create the placeholder of intervals.

        last_bar_ref_note = -1  # init with an impossible value
        for note in notes:  # find first note
            if note != 0:
                last_bar_ref_note = note
                break
        if (
            last_bar_ref_note == -1
        ):  # this means all notes are 0; there is nothing to process
            return self.intervals

        curser = interval()
        silent_interval = interval.get_silence_specs_list()

        for bar_number in range(int(len(notes) / pixels_per_bar)):  # traversing bars
            if (
                np.sum(
                    notes[
                        bar_number * pixels_per_bar : (bar_number + 1) * pixels_per_bar
                    ]
                )
                == 0
            ):  # bar is empty
                continue

            i = (
                bar_number * pixels_per_bar
            )  # init counter i with the first pixel of the bar
            while (
                i < (bar_number + 1) * pixels_per_bar and notes[i] == 0
            ):  # finding the first note of the bar
                self.intervals[i] = silent_interval
                i += 1

            if i < len(
                notes
            ):  # this ensures i does not exceed array boundaries which might happen at the last pixel of the last bar.
                ref_note = notes[i]
            else:
                break

            curser.semitones = (
                ref_note - last_bar_ref_note
            )  # finding the interval of the first note of the current bar with respect to the first note of the last bar
            curser.semitone2interval()

            self.intervals[i] = curser.get_specs_list()
            last_bar_ref_note = ref_note

            for i in range(i + 1, (bar_number + 1) * pixels_per_bar):
                if notes[i] == 0:
                    self.intervals[i] = silent_interval
                else:
                    curser.semitones = notes[i] - ref_note
                    curser.semitone2interval()
                    self.intervals[i] = curser.get_specs_list()

        return self.intervals

    def get_pianoroll_from_barwise_intervals(
        self,
        intervals=None,
        origin=None,
        velocity=None,
        leading_silence=0,
        pixels_per_bar=None,
    ):
        """Creates pianoroll from sequence of barwise intervals.

        Notes
        -----
        - Works on `self.intervals`.
        - Updates `self.intervals` if intervals argument is passed.
        - Updates `self.pianoroll`.

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

        Raises
        --------
        Type Error: if both intervals argument and self.intervals are None.
        Index Error: if intervals.shape[1] != interval.feature_dimensions [if intervals=None then raises if self.intervals.shape[1] != interval.feature_dimensions]
        Value Error: if leading_silence >= len(intervals) [if intervals=None then raises if leading_silence >= len(self.intervals)]
        Value Error: if pixels_per_bar < 1. If pixels_per_bar is None then self.pixels_per_bar is substituted.
        Index Error: if origin > 127 or origin < 0. If origin is None then self.origin is substituted.
        Index Error: if velocity > 127 or velocity < 0. If velocity is None then self.default_velocity is substituted.
        Index Error: if the sequence of the given intervals leads to to a note which is out of MIDI range (0-127).

        Returns
        -------
        ndarray, dtype=uint8, shape=(?, 128)
            First dimension is timesteps and second dimension is fixed 128 per MIDI standard.

        """
        if pixels_per_bar is None:
            pixels_per_bar = self.pixels_per_bar
        if pixels_per_bar < 1:
            raise ValueError("Number of pixels in bar must be a positive integer.")

        if intervals is not None:
            self.intervals = intervals
        else:
            if self.intervals is None:
                raise TypeError(self._get_none_error_message("intervals"))
        if self.intervals.shape[1] != interval().feature_dimensions:
            raise IndexError(
                self._get_incompatible_dimension_error_message("intervals")
            )

        if leading_silence >= len(self.intervals):
            raise ValueError("Leading silences must be less than intervals.")

        if origin is None:
            origin = self.origin
        if origin > 127 or origin < 0:
            raise IndexError(self._get_range_error_message())

        if velocity is None:
            velocity = self.default_velocity
        if velocity > 127 or velocity < 0:
            raise IndexError(self._get_range_error_message())

        self.pianoroll = np.zeros(
            (len(self.intervals), 128), dtype=np.uint8
        )  # 128 is the number of notes in MIDI
        if origin > 127 or origin < 0:
            raise IndexError(self._get_range_error_message())
        self.pianoroll[leading_silence, origin] = velocity

        curser = interval()
        last_known_origin = origin
        origin_is_unkown = True
        for i in range(leading_silence, len(self.intervals)):
            if (
                i % pixels_per_bar == 0
            ):  # a new bar has started, we need to find its first note
                origin_is_unkown = True

            if origin_is_unkown:
                curser.set_specs_list(
                    self.intervals[i]
                )  # this is the interval of the first note of the current bar with respect to the first note of the last bar
                if not curser.is_silence():  # skip silences
                    origin = (
                        last_known_origin + curser.interval2semitone()
                    )  # finding the first note of the current bar
                    last_known_origin = origin
                    if origin > 127 or origin < 0:
                        raise IndexError(self._get_range_error_message())
                    self.pianoroll[i, origin] = velocity
                    origin_is_unkown = False
            else:
                curser.set_specs_list(self.intervals[i])
                if not curser.is_silence():  # skip silences
                    note = origin + curser.interval2semitone()
                    if note > 127 or note < 0:
                        raise IndexError(self._get_range_error_message())
                    self.pianoroll[i, note] = velocity
        return self.pianoroll

    def chunk_sequence_of_intervals(self, intervals=None, pixels_per_chunk=None):
        """Breaks a long sequence of intervals into chunks.

        Notes
        -----
        - Works on `self.intervals`.
        - Updates `self.intervals` if intervals argument is passed.

        Parameters
        ----------
        intervals : ndarray, dtype=int8, shape=(?, interval.feature_dimensions), optional
            If None, the function expects self.intervals to have value; else, it overwrites self.intervals. First dimension is timesteps and second dimension is interval features.

        pixels_per_chunk: int, optional
            Number of pixels in each chunk. Set it to time signature's numarator multiplied by resolution per pixel to get chunk_per-bar. The default is self.pixels_per_bar.

        Raises
        --------
        Type Error: if both intervals argument and self.intervals are None.
        Index Error: if intervals.shape[1] != interval.feature_dimensions [if intervals=None then raises if self.intervals.shape[1] != interval.feature_dimensions]
        Value Error: if pixels_per_chunk < 1. If pixels_per_chunk is None then self.pixels_per_bar is substituted.

        Returns
        -------
        ndarray, dtype=int8, shape=(?, pixels_per_chunk, interval.feature_dimensions)
            First dimension is bars, second dimension is pixels in each chunk and, third dimension is interval features.

        """
        if intervals is not None:
            self.intervals = intervals
        else:
            if self.intervals is None:
                raise TypeError(self._get_none_error_message("intervals"))
        if self.intervals.shape[1] != interval().feature_dimensions:
            raise IndexError(
                self._get_incompatible_dimension_error_message("intervals")
            )

        if pixels_per_chunk is None:
            pixels_per_chunk = self.pixels_per_bar
        if pixels_per_chunk < 1:
            raise ValueError("Number of pixels in chunk must be a positive integer.")

        return np.reshape(
            self.intervals,
            (
                self.intervals.shape[0] // pixels_per_chunk,
                pixels_per_chunk,
                self.intervals.shape[1],
            ),
        )

    def merge_chunked_intervals(self, chunked_intervals):
        """Merges chunks of interval sequence.

        Notes
        -----
        - Updates `self.intervals`.

        Parameters
        ----------
        chunked_intervals : ndarray, dtype=int8, shape=(?, ?, interval.feature_dimensions)
            Merging happens along the first dimension and removes the second dimension.

        Returns
        -------
        ndarray, dtype=int8, shape=(?, interval.feature_dimensions)
            First dimension is timesteps and second dimension is interval features.

        """
        self.intervals = np.reshape(
            chunked_intervals,
            (
                chunked_intervals.shape[0] * chunked_intervals.shape[1],
                chunked_intervals.shape[2],
            ),
        )
        return self.intervals

    def get_RLE_from_intervals(self, intervals=None):
        """Compresses sequence of intervals using Run-Length Encoding.

        Notes
        -----
        - Works on `self.intervals`.
        - Updates `self.intervals` if `intervals` argument is passed.

        Parameters
        ----------
        intervals : ndarray, dtype=int8, shape=(?, interval.feature_dimensions), optional
            If None, the function expects self.intervals to have value; else, it overwrites self.intervals. First dimension is timesteps and second dimension is interval features.

        Raises
        --------
        Type Error: if both intervals argument and self.intervals are None.
        Index Error: if intervals.shape[1] != interval.feature_dimensions [if intervals=None then raises if self.intervals.shape[1] != interval.feature_dimensions]

        Returns
        -------
        ndarray, dtype=int32, shape=(?, interval.feature_dimensions + 1)
            First dimension is compressed timesteps. The last element in the second dimension indicates number of repeatitions for the rest of the elements in the second dimension.

        """
        if intervals is not None:
            self.intervals = intervals
        else:
            if self.intervals is None:
                raise TypeError(self._get_none_error_message("intervals"))
        if self.intervals.shape[1] != interval().feature_dimensions:
            raise IndexError(
                self._get_incompatible_dimension_error_message("intervals")
            )

        RLE = np.zeros(
            (self.intervals.shape[0], self.intervals.shape[1] + 1), dtype=int
        )

        RLE[0, : self.intervals.shape[1]] = self.intervals[0]
        RLE[0, -1] = 1
        index = 0
        for i in range(1, self.intervals.shape[0]):
            if np.array_equal(self.intervals[i], self.intervals[i - 1]):
                RLE[index, -1] += 1
            else:
                index += 1
                RLE[index, : self.intervals.shape[1]] = self.intervals[i]
                RLE[index, -1] = 1

        return RLE[: index + 1, :]

    def get_intervals_from_RLE(self, RLE_data):
        """Uncompresses Run-Length Encoded intervals data.

        Notes
        -----
        - Updates `self.intervals`.

        Parameters
        ----------
        RLE_data : ndarray, dtype=int32, shape=(?, interval.feature_dimensions + 1)
            First dimension is compressed timesteps. The last element in the second dimension indicates number of repeatitions for the rest of the elements in the second dimension.

        Returns
        -------
        ndarray, dtype=int8, shape=(?, interval.feature_dimensions)
            First dimension is timesteps and second dimension is interval features.

        """
        s = np.sum(RLE_data, axis=0)
        self.intervals = np.zeros((s[-1], len(s) - 1), dtype=np.int8)
        index = 0
        for i in range(RLE_data.shape[0]):
            replacement = np.repeat(
                RLE_data[i, : self.intervals.shape[1]], repeats=RLE_data[i, -1]
            )
            replacement = np.reshape(
                replacement, (RLE_data[i, -1], self.intervals.shape[1]), order="F"
            )
            self.intervals[
                index : index + RLE_data[i, -1], : self.intervals.shape[1]
            ] = replacement
            index += RLE_data[i, -1]
        return self.intervals

    def get_RLE_from_intervals_bulk(self, bulk_intervals):
        """Bulk version of :func:`get_RLE_from_intervals`.

        Parameters
        ----------
        bulk_intervals : ndarray, dtype=int8, shape=(?, pixels_per_chunk, interval.feature_dimensions)
            First dimension is chunks, second dimension is pixels in each chunk and, third dimension is interval features.

        Returns
        -------
        list
            List of RLE_compressed data, see :func:`get_intervals_from_RLE`.

        """

        RLE_bulk = []

        for intervals in bulk_intervals:
            RLE_bulk.append(self.get_RLE_from_intervals(intervals))

        return RLE_bulk

    def get_intervals_from_RLE_bulk(self, bulk_RLE_data):
        """Bulk version of :func:`get_intervals_from_RLE`.

        Notes
        -----
        - Infers output size from the first chunk.

        Parameters
        ----------
        bulk_RLE_data : list
            List of RLE_compressed data, see self.get_intervals_from_RLE.

        Returns
        -------
        ndarray, dtype=int8, shape=(?, pixels_per_chunk, interval.feature_dimensions)
            First dimension is chunks, second dimension is pixels in each chunk and, third dimension is interval features.

        """
        tmp = self.get_intervals_from_RLE(
            bulk_RLE_data[0]
        )  # just to identify the shape
        bulk_intervals = np.zeros((len(bulk_RLE_data), tmp.shape[0], tmp.shape[1]))

        # for i in range(len(bulk_RLE_data)):
        for i, RLE_data in enumerate(bulk_RLE_data):
            bulk_intervals[i] = self.get_intervals_from_RLE(RLE_data)

        return bulk_intervals
