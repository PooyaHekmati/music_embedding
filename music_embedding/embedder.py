from typing import List
import numpy as np
from .interval import interval

NOTES_IN_MIDI = 128


class embedder:
    """
    A class for embedding musical data, providing functionalities to convert between pianoroll representations
    and interval-based representations.

    This class handles various operations related to musical data manipulation, including extracting notes from
    pianorolls, converting pianoroll data to melodic, harmonic, and barwise intervals, and vice versa. Additionally,
    it supports Run-Length Encoding (RLE) compression for intervals.

    The constant `NOTES_IN_MIDI` is set to 128, reflecting the total number of MIDI notes in the standard MIDI range.
    This constant is used throughout the class to standardize the size of the second dimension in pianoroll arrays,
    ensuring they conform to MIDI standards. The pianoroll arrays are therefore structured with a shape of (?, 128),
    where each column represents a possible MIDI note, allowing for a consistent representation of musical data.

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
        if self.pianoroll.shape[1] != NOTES_IN_MIDI:
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

        coef = np.arange(1, NOTES_IN_MIDI + 1, dtype=np.uint32)
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
        if self.pianoroll.shape[1] != NOTES_IN_MIDI:
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
            (len(self.intervals) + 1, NOTES_IN_MIDI), dtype=np.uint8
        )
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

    def get_harmonic_intervals_from_pianoroll(
        self, ref_pianoroll: np.ndarray, pianoroll: np.ndarray | None = None
    ) -> np.ndarray:
        """
        Creates a sequence of harmonic intervals from the pianoroll relative to a reference pianoroll.

        This method computes harmonic intervals of the highest pitch notes in `self.pianoroll` with
        respect to `ref_pianoroll`. It updates `self.pianoroll` if `pianoroll` argument is passed
        and also updates `self.intervals`.

        Parameters
        ----------
        ref_pianoroll : ndarray, dtype=uint8, shape=(?, 128)
            Reference pianoroll to which harmonic intervals are calculated.
        pianoroll : ndarray, dtype=uint8, shape=(?, 128) | None, default=None
            Pianoroll for which to calculate harmonic intervals. If None, uses `self.pianoroll`.

        Returns
        -------
        ndarray, dtype=int8, shape=(?, interval.feature_dimensions)
            Array of harmonic intervals. First dimension represents timesteps, and the second
            dimension corresponds to interval features.

        Raises
        ------
        TypeError
            If both `pianoroll` argument and `self.pianoroll` are None.
        IndexError
            If `pianoroll.shape[1]` is not 128 or if `ref_pianoroll.shape[1]` is not 128.

        """
        if pianoroll is not None:
            self.pianoroll = pianoroll
        else:
            if self.pianoroll is None:
                raise TypeError(self._get_none_error_message("pianoroll"))
        if self.pianoroll.shape[1] != NOTES_IN_MIDI:
            raise IndexError(
                self._get_incompatible_dimension_error_message("pianoroll")
            )

        if ref_pianoroll.shape[1] != NOTES_IN_MIDI:
            raise IndexError(
                self._get_incompatible_dimension_error_message("pianoroll")
            )

        notes = self.extract_highest_pitch_notes_from_pianoroll()
        self.intervals = np.zeros(
            (len(notes), interval.feature_dimensions), dtype=np.int8
        )
        curser = interval()

        silent_interval = interval.get_silence_specs_list()

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
        self,
        pianoroll: np.ndarray | None = None,
        intervals: np.ndarray | None = None,
        velocity: int | None = None,
    ) -> np.ndarray:
        """
        Creates a pianoroll from a sequence of harmonic intervals.

        This method builds a new pianoroll based on the highest pitch notes extracted from the provided or
        class's pianoroll and the harmonic intervals stored in the class's intervals.

        **Example:** Given ATB choir pianoroll and Soprano's harmonic intervals with respect to Alto,
        returns Soprano's pianoroll.

        Parameters
        ----------
        pianoroll : ndarray, dtype=uint8, shape=(?, 128) | None, optional
            Pianoroll representation of musical data to be used. If None, the method uses self.pianoroll.
        intervals : ndarray, dtype=int8, shape=(?, interval.feature_dimensions) | None, optional
            Sequence of harmonic intervals. If None, the method uses self.intervals.
        velocity : int | None, optional
            Velocity for notes in the pianoroll. If None, self.default_velocity is used.

        Raises
        ------
        TypeError
            If both pianoroll argument and self.pianoroll are None.
        IndexError
            If pianoroll.shape[1] != 128, or if intervals.shape[1] != interval.feature_dimensions,
            or if adding the interval to the pianoroll leads to a note out of MIDI range (0-127),
            or if velocity is out of MIDI range (0-127).

        Returns
        -------
        ndarray, dtype=uint8, shape=(?, 128)
            The generated pianoroll, where the first dimension is timesteps and the second dimension
            is fixed to 128 per MIDI standard.

        """

        if pianoroll is not None:
            self.pianoroll = pianoroll
        else:
            if self.pianoroll is None:
                raise TypeError(self._get_none_error_message("pianoroll"))
        if self.pianoroll.shape[1] != NOTES_IN_MIDI:
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
        self.pianoroll = np.zeros((len(self.intervals), NOTES_IN_MIDI), dtype=np.uint8)
        curser = interval()
        for i, ref_note in enumerate(ref_notes):
            if ref_note != 0:  # if it is not silence
                curser.set_specs_list(self.intervals[i])
                note = curser.interval2semitone()
                if ref_note + note > 127 or ref_note + note < 0:
                    raise IndexError(self._get_range_error_message())
                self.pianoroll[i, ref_note + note] = velocity
        return self.pianoroll

    def get_barwise_intervals_from_pianoroll(
        self, pianoroll: np.ndarray | None = None, pixels_per_bar: int | None = None
    ) -> np.ndarray:
        """
        Creates a sequence of barwise intervals from a pianoroll, calculating intervals with respect to the first note
        of each bar. For the first notes of bars, intervals are calculated with respect to the first note of the
        previous bar.

        Parameters
        ----------
        pianoroll : ndarray, dtype=uint8, shape=(?, 128) | None, optional
            Pianoroll representation of musical data. If not provided, `self.pianoroll` is used. The first dimension
            represents timesteps, and the second dimension has a fixed size of 128, corresponding to MIDI standards.
        pixels_per_bar : int | None, optional
            Number of pixels in each bar, equal to the time signature's numerator multiplied by the resolution per
            pixel. If not provided, `self.pixels_per_bar` is used.

        Returns
        -------
        ndarray, dtype=int8, shape=(?, interval.feature_dimensions)
            Interval representation of musical data. The first dimension represents timesteps, and the second dimension
            corresponds to interval features.

        Raises
        ------
        TypeError
            If both `pianoroll` argument and `self.pianoroll` are None.
        IndexError
            If `pianoroll.shape[1]` != 128.
        ValueError
            If `pixels_per_bar` < 1 or if `pixels_per_bar` is None and `self.pixels_per_bar` < 1.

        """

        if pianoroll is not None:
            self.pianoroll = pianoroll
        else:
            if self.pianoroll is None:
                raise TypeError(self._get_none_error_message("pianoroll"))
        if self.pianoroll.shape[1] != NOTES_IN_MIDI:
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
        intervals: np.ndarray | None = None,
        origin: int | None = None,
        velocity: int | None = None,
        leading_silence: int = 0,
        pixels_per_bar: int | None = None,
    ) -> np.ndarray:
        """
        Creates a pianoroll from a sequence of barwise intervals.

        This method decodes barwise interval data into a pianoroll representation, considering each bar's
        first note and the intervals following it. It supports specifying the origin note, velocity, leading
        silence, and pixels per bar.

        Parameters
        ----------
        intervals : ndarray, dtype=int8, shape=(?, interval.feature_dimensions), default=None
            Sequence of barwise intervals. Uses `self.intervals` if None.
        origin : int, default=None
            Reference note for the melody (MIDI value). Uses `self.origin` if None.
        velocity : int, default=None
            Velocity for notes in the pianoroll. Uses `self.default_velocity` if None.
        leading_silence : int, default=0
            Number of silent pixels at the beginning of the melody.
        pixels_per_bar : int, default=None
            Number of pixels in each bar. Uses `self.pixels_per_bar` if None.

        Raises
        ------
        ValueError
            If `pixels_per_bar` is less than 1 or `leading_silence` is greater than or equal to the
            length of intervals.
        IndexError
            If `origin` or `velocity` is out of MIDI range (0-127), or if note calculations lead to
            values outside this range.

        Returns
        -------
        ndarray, dtype=uint8, shape=(?, 128)
            Pianoroll representation with each timestep and MIDI note.

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

        self.pianoroll = np.zeros((len(self.intervals), NOTES_IN_MIDI), dtype=np.uint8)
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
                # this is first note's interval of the current bar with respect to the first note of the last bar
                curser.set_specs_list(self.intervals[i])
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

    def chunk_sequence_of_intervals(
        self, intervals: np.ndarray | None = None, pixels_per_chunk: int | None = None
    ) -> np.ndarray:
        """
        Breaks a long sequence of intervals into chunks of a specified length.

        This method divides a sequence of intervals into smaller, equally-sized chunks, which can be useful for
        processing or analyzing data in segments. If `intervals` is None, the method works on `self.intervals`.

        Parameters
        ----------
        intervals : ndarray, dtype=int8, shape=(?, interval.feature_dimensions)
            Sequence of intervals to be chunked. If None, uses `self.intervals`.
        pixels_per_chunk : int
            Number of pixels in each chunk. Defaults to `self.pixels_per_bar` if None.

        Returns
        -------
        ndarray, dtype=int8
            Array of chunked intervals. Shape is (?, pixels_per_chunk, interval.feature_dimensions),
            where ? is the number of chunks.

        Raises
        ------
        TypeError
            If both `intervals` argument and `self.intervals` are None.
        IndexError
            If `intervals` shape's second dimension is not equal to `interval.feature_dimensions`.
        ValueError
            If `pixels_per_chunk` is less than 1 or if it's None and `self.pixels_per_bar` is less than 1.
        """
        if intervals is None:
            intervals = self.intervals
        if intervals is None:
            raise TypeError(self._get_none_error_message("intervals"))
        if intervals.shape[1] != interval().feature_dimensions:
            raise IndexError(
                self._get_incompatible_dimension_error_message("intervals")
            )

        if pixels_per_chunk is None:
            pixels_per_chunk = self.pixels_per_bar
        if pixels_per_chunk < 1:
            raise ValueError("Number of pixels in chunk must be a positive integer.")

        return np.reshape(
            intervals,
            (
                intervals.shape[0] // pixels_per_chunk,
                pixels_per_chunk,
                intervals.shape[1],
            ),
        )

    def merge_chunked_intervals(self, chunked_intervals: np.ndarray) -> np.ndarray:
        """
        Merges chunks of interval sequences into a single sequence.

        This method flattens a 3D array of chunked intervals into a 2D array, where the first dimension represents
        the total timesteps and the second dimension represents interval features. It is useful for reassembling
        interval data that was previously divided into chunks.

        Parameters
        ----------
        chunked_intervals : ndarray
            A 3D array of chunked intervals, with shape (num_chunks, chunk_size, interval.feature_dimensions).
            Each chunk represents a portion of the interval sequence.

        Returns
        -------
        ndarray
            A 2D array of merged intervals, with shape (num_timesteps, interval.feature_dimensions). Represents the
            entire sequence of intervals as a single continuous array.

        """
        self.intervals = np.reshape(
            chunked_intervals,
            (
                chunked_intervals.shape[0] * chunked_intervals.shape[1],
                chunked_intervals.shape[2],
            ),
        )
        return self.intervals

    def get_RLE_from_intervals(self, intervals: np.ndarray | None = None) -> np.ndarray:
        """
        Compresses a sequence of intervals using Run-Length Encoding (RLE).

        This method takes a sequence of intervals and compresses it using RLE, which is useful
        for reducing the size of repetitive data. The output is an array where each row represents
        a compressed sequence of intervals, and the last column in each row indicates the number
        of repetitions.

        Parameters
        ----------
        intervals : ndarray, dtype=int8, shape=(?, interval.feature_dimensions) | None, optional
            The sequence of intervals to be compressed. If None, uses self.intervals.

        Returns
        -------
        ndarray, dtype=int32, shape=(?, interval.feature_dimensions + 1)
            The RLE compressed intervals. Each row contains the compressed interval data with
            the last element indicating the count of repetitions.

        Raises
        ------
        TypeError
            If both intervals argument and self.intervals are None.
        IndexError
            If intervals.shape[1] != interval.feature_dimensions (if intervals is None,
            then self.intervals.shape[1] is checked).

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

    def get_intervals_from_RLE(self, RLE_data: np.ndarray) -> np.ndarray:
        """
        Uncompresses a Run-Length Encoded sequence of intervals.

        This method takes a Run-Length Encoded (RLE) array representing a sequence of intervals and
        decompresses it to obtain the original sequence of intervals.

        Parameters
        ----------
        RLE_data : ndarray, dtype=int32, shape=(?, interval.feature_dimensions + 1)
            Compressed intervals using Run-Length Encoding. The last element in each row indicates
            the number of repetitions for the interval.

        Returns
        -------
        ndarray, dtype=int8, shape=(?, interval.feature_dimensions)
            Decompressed sequence of intervals. The first dimension represents timesteps, and the
            second dimension corresponds to interval features.

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

    def get_RLE_from_intervals_bulk(
        self, bulk_intervals: np.ndarray
    ) -> List[np.ndarray]:
        """
        Bulk compresses a sequence of intervals using Run-Length Encoding (RLE).

        This method processes multiple sequences of intervals simultaneously, applying RLE compression to each
        sequence in the bulk data. It is useful for handling large datasets where individual processing would be
        inefficient.

        Parameters
        ----------
        bulk_intervals : ndarray
            An array containing multiple sequences of intervals, with shape (n_chunks, chunk_size,
            interval.feature_dimensions). Each sequence (chunk) in the first dimension will be compressed using RLE.

        Returns
        -------
        List[ndarray]
            A list of RLE-compressed interval sequences, where each element in the list corresponds to the RLE
            representation of a chunk in `bulk_intervals`. Each ndarray in the list has shape (?,
            interval.feature_dimensions + 1), where the last dimension includes the run lengths.

        See Also
        --------
        get_RLE_from_intervals : Compresses a single sequence of intervals using Run-Length Encoding.
        get_intervals_from_RLE_bulk : Bulk decompresses Run-Length Encoded interval sequences.

        """

        RLE_bulk = []

        for intervals in bulk_intervals:
            RLE_bulk.append(self.get_RLE_from_intervals(intervals))

        return RLE_bulk

    def get_intervals_from_RLE_bulk(
        self, bulk_RLE_data: List[np.ndarray]
    ) -> np.ndarray:
        """
        Bulk uncompresses a sequence of Run-Length Encoded intervals.

        This method uncompresses multiple sequences of intervals that have been compressed using
        Run-Length Encoding (RLE). It processes a list of RLE-compressed data and returns the
        uncompressed intervals in bulk.

        Parameters
        ----------
        bulk_RLE_data : List[np.ndarray]
            A list of RLE-compressed data, where each element is an ndarray with the shape
            (?, interval.feature_dimensions + 1). The last element in each row indicates the number
            of repetitions for the rest of the elements in the row.

        Returns
        -------
        np.ndarray
            An ndarray of uncompressed intervals. The shape of the output array is
            (?, pixels_per_chunk, interval.feature_dimensions), where the first dimension represents
            chunks, the second dimension represents pixels in each chunk, and the third dimension
            represents interval features.

        Notes
        -----
        The output size is inferred from the first chunk in the bulk RLE data.

        """
        tmp = self.get_intervals_from_RLE(
            bulk_RLE_data[0]
        )  # just to identify the shape
        bulk_intervals = np.zeros((len(bulk_RLE_data), tmp.shape[0], tmp.shape[1]))

        for i, RLE_data in enumerate(bulk_RLE_data):
            bulk_intervals[i] = self.get_intervals_from_RLE(RLE_data)

        return bulk_intervals
