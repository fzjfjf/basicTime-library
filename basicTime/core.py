import math
import time  #need this for counting seconds
from datetime import datetime   #need this for syncing with pc clock
from . import settings
import atexit

class Clock:
    """
    This module/class logs all function calls using self._log(info: str).
    Each function automatically logs when it starts, when exceptions occur, and when it returns.
    """
    _CONSTS = [60, 60, 24, 365]
    _MONTH_OFFSETS = {
        1: 0,
        2: 31,
        3: 59,
        4: 90,
        5: 120,
        6: 151,
        7: 181,
        8: 212,
        9: 243,
        10: 273,
        11: 304,
        12: 334,
        13: 366,
    }
    _KEYS = ["seconds", "minutes", "hours", "day_in_year", "years"]

    def __init__(self):
        # These are defaults for the clock
        self.starting_time = time.monotonic_ns()
        self._current_time = {
            "seconds": 0,
            "minutes": 0,
            "hours": 0,
            "day_in_month": 0,
            "day_in_year": 0,
            "month": 0,
            "years": 0,
        }
        self._SETTINGS_DICT = {
            'default_time': {
                "seconds": 0,
                "minutes": 0,
                "hours": 0,
                "day_in_month": 0,
                "day_in_year": 0,
                "years": 0,
            },
            'sync_on_start': False,
            'show_test_output': False,
            'do_unit_tests': False,
            'start_counting': False
        }
        self._log_buffer = []
        atexit.register(self._flush_log_buffer)

    def _flush_log_buffer(self) -> None:
        """
        If program exits without _log_buffer being flushed, this function will flush it.
        """
        if len(self._log_buffer) != 0:
            with open("log.txt", "a") as f:
                f.writelines(self._log_buffer)
        return None

    def _calculate_time(self):
        new_time = time.monotonic_ns()
        elapsed = new_time - self.starting_time
        if elapsed >= 1_000_000_000:
            seconds_to_add = math.floor(elapsed // 1_000_000_000)
        else:
            seconds_to_add = 0
        self.increase_time("seconds", seconds_to_add)
        self.starting_time += seconds_to_add * 1_000_000_000

    def _log(self, info: str) -> None:
        """
        Function provides info to _log, and _log writes it into a file

        Parameters:
              info (str): Information to put into log

        Notes:
            - When called, puts info in _log_buffer. Once length of _log_buffer is bigger than 10,
              it writes the strings into the log file.
            - Formats time to put into the log by itself.
        """
        time_to_put_into_log = f"{self.return_clk_style()}  "
        # Put the info into log with the time
        self._log_buffer.append(time_to_put_into_log + info + "\n")
        length_of_buffer = len(self._log_buffer)
        if length_of_buffer > 10:
            with open("log.txt", "a") as log_file:
                log_file.writelines(self._log_buffer)
            self._log_buffer = []
        return None

    def increase_time(self, unit_type: str, amount: int) -> None:
        """
        Adds amount to the unit specified by unit_type

        Notes:
             - amount can not be below zero, otherwise a ValueError is raised
             - If unit_type does not exist, a KeyError will be raised
             - Runs normalize at the end
        """
        if amount < 0:
            raise ValueError("The value has to be bigger than zero")
        if unit_type not in self._KEYS:
            raise KeyError(f"{unit_type} is an invalid unit of time for increasing time")
        self._current_time[unit_type] += amount
        self._normalize()
        return None

    def _normalize(self) -> None:
        """
        Takes _current_time and normalizes it

        Notes:
             - Does not work with negative values
        """
        for i in range(0, 4):
            while self._current_time[self._KEYS[i]] >= self._CONSTS[i]:
                self._current_time[self._KEYS[i]] -= self._CONSTS[i]
                self._current_time[self._KEYS[i+1]] += 1
        self._current_time["day_in_month"] = self._get_day()
        self._current_time["month"] = self._get_month()
        return None

    def sync_time(self) -> None:
        """
        Uses datetime to sync with system clock

        Notes:
            - This is the only time datetime module is used
        """
        self._log("Executing: syncTime")
        now = datetime.now()
        self._current_time["seconds"] = now.second
        self._current_time["minutes"] = now.minute
        self._current_time["hours"] = now.hour
        self._current_time["day_in_year"] = now.day + self._MONTH_OFFSETS[now.month]
        self._current_time["years"] = now.year
        self._current_time["day_in_month"] = now.day
        self._current_time["month"] = now.month
        self._log("sync_time returned: None")
        return None

    def initializer(self) -> None:
        """
        Takes the settings dictionary from settings.py and sets _SETTINGS_DICT equal to itself.

        Parameters:
            No parameters
        """
        self._log("Executing: initializer")
        self._SETTINGS_DICT = settings.settings_dict
        if self._SETTINGS_DICT["sync_on_start"]:
            self.sync_time()
        self._log("initializer returned: None")
        return None

    def get_time(self, requested_time_unit: str) -> int | list:
        """
        The default way to get time

        Parameters:
             requested_time_unit (str):
        """
        # The main way of getting time from the library.
        if requested_time_unit == "all":
            self._calculate_time()
            requested_time = self._current_time.copy()
        elif requested_time_unit == "dom":
            requested_time = self._get_day()
        elif requested_time_unit == "month":
            requested_time = self._get_month()
        else:
            try:
                requested_time = self._current_time[requested_time_unit]
            except KeyError:
                raise KeyError(f"{requested_time_unit} is not a valid unit of time")
        return requested_time

    def set_time(self, new_time: dict[int]) -> None:
        """
        Gives the developer an easy way to set a custom time while the program is running

        Parameters:
            new_time (dict[int]): a dict with the new time

        Notes:
            - New time is automatically normalized
        """
        self._log("Executing: set_time")
        #TODO: ADD CHECKING OF NEW TIME

        self._current_time = new_time
        self._normalize()
        self._log("set_time returned: None")
        return None

    def convert(self, value: int, fromType: str, toType: str) -> float:
        """
        Returns converted value from one unit to the other one

        Parameters:
             value (int): Value to be converted
             fromType (str): Unit type the value provided is in
             toType (str): Unit type to convert the value to

        Notes:
            - If one or both units are not supported, a KeyError will be raised
            - Supported units include: "seconds", "minutes", "hours", "days", "years".
        """
        _a_dict = {
            "seconds": 0,
            "minutes": 1,
            "hours": 2,
            "days": 3,
            "years": 4,
        }
        self._log("Executing: convert")
        try:
            converted = value
            if _a_dict[fromType] > _a_dict[toType]:
                for i in range(_a_dict[fromType], _a_dict[toType]):
                    converted *= self._CONSTS[_a_dict[toType]]
            elif _a_dict[fromType] < _a_dict[toType]:
                for i in range(_a_dict[fromType], _a_dict[toType]):
                    converted /= self._CONSTS[_a_dict[toType]]
            elif fromType == toType:
                self._log(f"converted returned: {value}")
                return value
        except KeyError:
            self._log(f"KeyError in convert, convertFrom = {value}  fromType = {fromType}  convertTo = {toType}")
            raise KeyError(f"Either '{fromType}' or '{toType}' is an invalid time unit")
        self._log(f"convert returned: {converted}")
        return converted

    def _get_day(self) -> int:
        """
        Returns day in the current month
        """
        month = self._get_month()
        day = self._current_time["day_in_year"] - self._MONTH_OFFSETS[month]
        return day

    def _get_month(self) -> int:
        """
        Returns the month based on how many days passed in this year

        Parameters:
             No parameters

        Notes:
            - If values in _current_time are outside their respective bounds,
              a ValueError will be raised, and state of _current_time will be dumped to the log file
        """
        month = 13
        if self._current_time["day_in_year"] < 0 or self._current_time["day_in_year"] > 366:
            raise ValueError("Internal error happened")
        for k in range(1, 13):
            if (self._MONTH_OFFSETS[k] < self._current_time["day_in_year"] and
                    self._current_time["day_in_year"] <= self._MONTH_OFFSETS[k + 1]):
                month = k
        return month

    def decrease_time(self, unit_type: str, amount: int) -> None:
        """
        Decrease the current time by a given amount of a specified unit.

        Parameters:
            unit_type (str): The type of time unit (e.g., 'sec', 'min', 'hour').
            amount (int): The amount to subtract from the current time.

        Notes:
            - The amount is converted to seconds internally.
            - _current_time is updated by subtracting the amount in seconds.
            - If _current_time becomes negative, it is normalized by
              rolling over from the higher unit and adjusting accordingly.
            - If amount to subtract is larger than total amount in _current_time,
              years will become negative
        """
        self._log("Executing: decrease_time")
        amount = self.convert(amount, unit_type, "seconds")     # Convert to seconds, it is easier to work with them
        self._current_time["seconds"] -= amount
        # Now we need to normalize time
        for i in range(0, 4):
            while self._current_time[i] < 0:
                self._current_time[i] += self._CONSTS[i]
                self._current_time[i+1] -= 1
        self._log("decrease_time returned: None")
        return None

    def return_clk_style(self) -> str:
        """
        Return a clock-style string

        Parameters:
             No parameters

        Notes:
            - Returns a string that contains time formatted like this:
              21:44:2, 19/1/2026
            - The string is not zero-padded
        """
        new_time = self.get_time("all")
        time_now = f"{new_time['hours']}:{new_time['minutes']}:{new_time['seconds']}, {new_time['day_in_month']}/{new_time['month']}/{new_time['years']}"
        return time_now

    def change_settings(self, name: str, value: bool | float) -> None:
        """
        Allows the developer to change startup settings

        Parameters:
             name (str): The name of the setting
             value (bool or float): The value that the setting will be set to

        Notes:
            - If the setting does not exist, a KeyError will be raised
            - Disclaimer: if the write operation goes wrong, settings may become corrupted
        """
        self._log("Executing: change_settings")
        try:
            some_value = self._SETTINGS_DICT[name]
        except KeyError:
            self._log(f"KeyError in change_settings, name = {name}  value = {value}")
            raise KeyError(f"{name} does not exists as a settings")
        self._SETTINGS_DICT[name] = value
        with open("settings.py", "w") as f:
            f.write("settingsDict = " + str(self._SETTINGS_DICT))
        self._log("change_settings returned: None")
        return None