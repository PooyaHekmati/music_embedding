from typing import Dict, List
import numpy as np


class interval:
    """
    A class representing musical intervals, offering functionality to handle
    interval characteristics, conversions, and descriptions within music theory.

    Attributes
    ----------
    interval_order : int
        The ordinal number of the interval, ranging from 1 (unison) to 7 (seventh).
    interval_type : int
        The quality of the interval, represented by integers:
        -2 (diminished), -1 (minor), 0 (perfect), 1 (major), 2 (augmented).
    octave_offset : int
        The octave offset for compound intervals; 0 if the interval is within a single octave.
    is_descending : int
        Indicates the direction of the interval: 0 for ascending, 1 for descending.
    semitones : int
        The number of semitones in the interval.

    Notes
    -----
    The class provides both numerical and one-hot-encoded methods for
    representing interval characteristics, and it includes methods for
    converting between semitone distances and interval qualities.
    """

    feature_dimensions = 4

    def __init__(
        self,
        interval_order: int = 1,
        interval_type: int = 0,
        octave_offset: int = 0,
        is_descending: int = 0,
        semitones: int = 0,
    ):
        self.interval_order: int = interval_order
        self.interval_type: int = interval_type
        self.octave_offset: int = octave_offset
        self.is_descending: int = is_descending
        self.semitones: int = semitones

    def semitone2interval(self, semitones: int | None = None) -> Dict[str, int]:
        """
        Calculates the interval characteristics based on their semitone distance. If the 'semitones' argument
        is provided, it updates the instance's 'semitones' attribute before calculating the interval.

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
        semitones : int | None, default=None
            The number of semitones in the interval. If provided, updates the instance's 'semitones' attribute.

        Returns
        -------
        dict
            A dictionary with the updated interval characteristics: 'interval_order', 'interval_type',
            'octave_offset', and 'is_descending'.
        """
        if semitones is not None:
            self.semitones = semitones

        self.is_descending = 0
        if self.semitones < 0:
            self.is_descending = 1
            self.semitones = -self.semitones

        self.octave_offset = self.semitones // 12  # becuase 12th semitone is the octave
        remainder_semitones = self.semitones % 12

        self.interval_order = 1
        self.interval_type = 0
        if remainder_semitones == 0:  # implementing Q-table
            self.interval_order = 1
            self.interval_type = 0
        elif remainder_semitones == 1:
            self.interval_order = 2
            self.interval_type = -1
        elif remainder_semitones == 2:
            self.interval_order = 2
            self.interval_type = 1
        elif remainder_semitones == 3:
            self.interval_order = 3
            self.interval_type = -1
        elif remainder_semitones == 4:
            self.interval_order = 3
            self.interval_type = 1
        elif remainder_semitones == 5:
            self.interval_order = 4
            self.interval_type = 0
        elif remainder_semitones == 6:
            self.interval_order = 5
            self.interval_type = -2
        elif remainder_semitones == 7:
            self.interval_order = 5
            self.interval_type = 0
        elif remainder_semitones == 8:
            self.interval_order = 6
            self.interval_type = -1
        elif remainder_semitones == 9:
            self.interval_order = 6
            self.interval_type = 1
        elif remainder_semitones == 10:
            self.interval_order = 7
            self.interval_type = -1
        elif remainder_semitones == 11:
            self.interval_order = 7
            self.interval_type = 1

        return {
            "interval_order": self.interval_order,
            "interval_type": self.interval_type,
            "octave_offset": self.octave_offset,
            "is_descending": self.is_descending,
        }

    def interval2semitone(self, specs: List[int] | None = None) -> int:
        """
        Returns the distance between the two notes of the interval in semitones.

        Notes
        -----
        - Updates interval parameters if `specs` is passed.
        - Faulty interval representation handling:
            * If the interval is 1st, 4th, or 5th and the interval type is set to minor (m) or Major (M),
            calculates the perfect (P) interval.
            * If the interval is 2nd, 3rd, 6th, or 7th and the interval type is set to perfect (P),
            calculates the Major (M) interval.

        Parameters
        ----------
        specs : List[int] | None, optional
            A list containing the interval characteristics in the following order:
            - interval_order (first to seventh)
            - interval_type (-2: dim, -1: min, 0: perfect, 1: Maj, 2: Aug)
            - is_descending (0 for ascending, 1 for descending)
            - octave_offset (octave offset of the interval, 0 if not compound)
            If None, uses the current interval's properties.

        Returns
        -------
        int
            Number of semitones in the interval.
        """

        if specs is not None:
            self.set_specs_list(specs)

        self.semitones = 0

        if self.interval_order == 1:
            if self.interval_type == -2:
                self.semitones = -1
            elif self.interval_type == -1:
                self.semitones = 0
            elif self.interval_type == 0:
                self.semitones = 0
            elif self.interval_type == 1:
                self.semitones = 0
            elif self.interval_type == 2:
                self.semitones = 1

        elif self.interval_order == 2:
            if self.interval_type == -2:
                self.semitones = 0
            elif self.interval_type == -1:
                self.semitones = 1
            elif self.interval_type == 0:
                self.semitones = 2
            elif self.interval_type == 1:
                self.semitones = 2
            elif self.interval_type == 2:
                self.semitones = 3

        elif self.interval_order == 3:
            if self.interval_type == -2:
                self.semitones = 2
            elif self.interval_type == -1:
                self.semitones = 3
            elif self.interval_type == 0:
                self.semitones = 4
            elif self.interval_type == 1:
                self.semitones = 4
            elif self.interval_type == 2:
                self.semitones = 5

        elif self.interval_order == 4:
            if self.interval_type == -2:
                self.semitones = 4
            elif self.interval_type == -1:
                self.semitones = 5
            elif self.interval_type == 0:
                self.semitones = 5
            elif self.interval_type == 1:
                self.semitones = 5
            elif self.interval_type == 2:
                self.semitones = 6

        elif self.interval_order == 5:
            if self.interval_type == -2:
                self.semitones = 6
            elif self.interval_type == -1:
                self.semitones = 7
            elif self.interval_type == 0:
                self.semitones = 7
            elif self.interval_type == 1:
                self.semitones = 7
            elif self.interval_type == 2:
                self.semitones = 8

        elif self.interval_order == 6:
            if self.interval_type == -2:
                self.semitones = 7
            elif self.interval_type == -1:
                self.semitones = 8
            elif self.interval_type == 0:
                self.semitones = 9
            elif self.interval_type == 1:
                self.semitones = 9
            elif self.interval_type == 2:
                self.semitones = 10

        elif self.interval_order == 7:
            if self.interval_type == -2:
                self.semitones = 9
            elif self.interval_type == -1:
                self.semitones = 10
            elif self.interval_type == 0:
                self.semitones = 11
            elif self.interval_type == 1:
                self.semitones = 11
            elif self.interval_type == 2:
                self.semitones = 12

        self.semitones += (
            self.octave_offset * 12
        )  # adds multiplies of 12 to semitones becuase octave is 12 semitones

        if self.is_descending == 1:
            self.semitones = -self.semitones

        return int(self.semitones)

    def is_silence(self) -> bool:
        """
        Determines if the interval represents silence, based on its specifications.

        Silence is represented by an interval with all attributes set to zero values.

        Returns
        -------
        bool
            True if the interval represents silence, False otherwise.
        """
        return np.array_equal(self.get_specs_list(), interval.get_silence_specs_list())

    def get_specs_list(self) -> List[int]:
        """
        Returns the interval's characteristics as a list of integers.

        Returns
        -------
        List[int]
            A list containing the interval's characteristics in the following order:
            [interval_order, interval_type, is_descending, octave_offset]

        """
        return [
            self.interval_order,
            self.interval_type,
            self.is_descending,
            self.octave_offset,
        ]

    def set_specs_list(self, specs: List[int] | Dict[str, int] | None) -> None:
        """
        Sets the interval's characteristics from a list or dictionary.

        Parameters
        ----------
        specs : List[int] | Dict[str, int] | None
            A list or dictionary containing the interval's characteristics, or None. The list or dictionary should
            contain the following elements in order: interval_order (int), interval_type (int), is_descending (int),
            and octave_offset (int).

        Raises
        ------
        ValueError
            If any of the provided values for interval_order, interval_type, is_descending, or octave_offset are out of
            their valid ranges.

        Notes
        -----
        The valid ranges for the attributes are as follows:
        - interval_order: between 0 and 7 (inclusive)
        - interval_type: between -2 and 2 (inclusive)
        - is_descending: either 0 or 1
        - octave_offset: between 0 and 9 (inclusive)

        """
        if isinstance(specs, dict):
            interval_order = specs["interval_order"]
            interval_type = specs["interval_type"]
            is_descending = specs["is_descending"]
            octave_offset = specs["octave_offset"]
        else:
            interval_order = specs[0]
            interval_type = specs[1]
            is_descending = specs[2]
            octave_offset = specs[3]

        if interval_order > 7 or interval_order < 0:
            raise ValueError("interval_order must be between 0 and 7 (inclusive).")
        if interval_type > 2 or interval_type < -2:
            raise ValueError("interval_type must be between -2 and 2 (inclusive).")
        if is_descending < 0 or is_descending > 1:
            raise ValueError("is_descending must be either 0 or 1.")
        if octave_offset < 0 or octave_offset > 9:
            raise ValueError("octave_offset must be between 0 and 9 (inclusive).")

        self.interval_order = interval_order
        self.interval_type = interval_type
        self.is_descending = is_descending
        self.octave_offset = octave_offset

    def get_one_hot_specs_list(self) -> Dict[str, List[int] | int | bool]:
        """
        Provides a one-hot encoding of the interval's order and type, and represents the descending status and
        octave offset as an integer and boolean, respectively.

        Returns
        -------
        Dict[str, List[int] | int, bool]]
            A dictionary containing one-hot encoded representations of the interval order and type, the descending
            status as a boolean, and the octave offset as an integer. Keys are 'interval_order', 'interval_type',
            'is_descending', and 'octave_offset'.
        """
        interval_order = [0] * 7
        interval_type = [0] * 5
        interval_order[
            self.interval_order - 1
        ] = 1  # 1 is subtracted to get the index; index starts at 0 while order starts at 1
        interval_type[
            self.interval_type + 2
        ] = 1  # 2 is added to get the index; index starts at 0 while type starts at -2
        return {
            "interval_order": interval_order,
            "interval_type": interval_type,
            "is_descending": self.is_descending,
            "octave_offset": self.octave_offset,
        }

    def set_one_hot_specs_list(
        self,
        interval_order: List[int],
        interval_type: List[int],
        is_descending: int,
        octave_offset: int,
    ) -> None:
        """
        Sets the interval's characteristics based on one-hot encoded representations and integer values.

        Parameters
        ----------
        interval_order : List[int]
            One-hot encoding representation of the interval's order: 1st to 7th. A list of 7 integers,
            where exactly one element is 1, and the others are 0, indicating the order of the interval.
        interval_type : List[int]
            One-hot encoding representation of the interval's type: -2 (diminished) to 2 (augmented).
            A list of 5 integers, where exactly one element is 1, and the others are 0, indicating the
            type of the interval.
        is_descending : int
            Indicates the direction of the interval: 0 for ascending, 1 for descending.
        octave_offset : int
            The octave offset for compound intervals; 0 if the interval is within a single octave.

        """
        interval_order = (
            np.argmax(interval_order) + 1
        )  # 1 is added to get the index; index starts at 0 while order starts at 1
        interval_type = (
            np.argmax(interval_type) - 2
        )  # 2 is subtracted to get the index; index starts at 0 while type starts at -2
        self.set_specs_list(
            [interval_order, interval_type, is_descending, octave_offset]
        )

    @staticmethod
    def get_silence_specs_list() -> List[int]:
        """
        Provides a representation of silence in the interval format.

        Silence is represented as a list of zeros with a length equal to the number of feature dimensions
        of the interval class.

        Returns
        -------
        List[int]
            A list of integers representing silence, with all elements set to zero.

        """
        return [0] * interval().feature_dimensions

    def get_name(self, semitones: int | None = None) -> str:
        """
        Generates the interval's name from its internal representation. If `semitones` is provided, the interval
        characteristics are updated accordingly before generating the name.

        Parameters
        ----------
        semitones : int | None, default=None
            If provided, the number of semitones is used to update the interval characteristics.

        Returns
        -------
        str
            The name of the interval, including its quality, ordinal number, and direction (ascending/descending).

        Notes
        -----
        Returns "Silence" if the interval represents silence. The name includes the interval's quality (diminished,
        minor, perfect, major, augmented), its ordinal number (1st, 2nd, etc.), and its direction
        (ascending or descending) if applicable.
        """
        if semitones is not None:
            self.semitones = semitones
            self.semitone2interval()

        if self.is_silence():
            return "Silence"

        output = ""
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
        ordinal = lambda n: "%d%s" % (
            n,
            "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10 :: 4],
        )  # adopted from https://codegolf.stackexchange.com/questions/4707/outputting-ordinal-numbers-1st-2nd-3rd#answer-4712
        output += ordinal(self.interval_order + self.octave_offset * 7)
        return output

    def __str__(self):
        return self.get_name()
