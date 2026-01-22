import time  #need this for counting seconds
import threading
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
    _KEYS = {  # Contains index positions of the units. Made for easier use of current_time.
        "sec": 0,
        "min": 1,
        "hour": 2,
        "day": 3,
        "year": 4,
    }

    def __init__(self):
        # These are defaults for the clock
        self._current_time = [0, 0, 0, 0, 0]
        self._SETTINGS_DICT = {
            'default_time': [0, 0, 0, 0, 0],
            'tick_interval': 1,
            'sync_on_start': False,
            'show_test_output': False,
            'do_unit_tests': False,
            'start_counting': False
        }
        self._ticking_thread = threading.Thread(
            target=self._tick,
            daemon=True
        )
        self._ticking_thread.start()
        self._isTicking = False
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

    def _tick(self):
        while True:
            time.sleep(self._SETTINGS_DICT["tick_interval"])
            if self._isTicking:
                self.increase_time("sec", 1)

    def _log(self, info: str) -> None:
        """
        Function provides info to _log, and _log writes it into a file

        Parameters:
              info (str): Information to put into log

        Notes:
            - When called, puts info in _log_buffer. Once length of _log_buffer is bigger than 10,
              it writes the strings into the log file.
        """
        # Get the time to put into the log, can not use any other function,
        # because every other function calls _log, and then you would get
        # an infinite recursion.
        seconds = self._current_time[self._KEYS["sec"]]
        minutes = self._current_time[self._KEYS["min"]]
        hours = self._current_time[self._KEYS["hour"]]
        month = -1
        for a in range(1, 13):
            if (self._MONTH_OFFSETS[a] < self._current_time[self._KEYS["day"]] and
                self._current_time[self._KEYS["day"]] <= self._MONTH_OFFSETS[a + 1]):
                month = a
        if month != -1:
            day = self._current_time[self._KEYS["day"]] - self._MONTH_OFFSETS[month]
        else:
            day = -1
        year = self._current_time[self._KEYS["year"]]
        time_to_put_into_log = f"{hours}:{minutes}:{seconds}, {day}/{month}/{year}  "
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
        self._log("Executing increase_time")
        if amount < 0:
            self._log(f"ValueError in increase_time, amount = {amount}  unit_type = {unit_type}")
            raise ValueError("The value has to be bigger than zero")
        try:
            self._current_time[self._KEYS[unit_type]] += amount
        except KeyError:
            self._log(f"KeyError in increase_time, unit_type = {unit_type}  amount = {amount}")
            raise KeyError(f"{unit_type} is an invalid unit of time")
        self._normalize()
        self._log("increase_time returned: None")
        return None

    def _normalize(self) -> None:
        """
        Takes _current_time and normalizes it

        Notes:
             - Does not work with negative values
        """
        self._log("Executing: _normalize")
        for i in range(0, 4):
            while self._current_time[i] >= self._CONSTS[i]:
                self._current_time[i] -= self._CONSTS[i]
                self._current_time[i+1] += 1
        self._log("_normalize returned: None")
        return None

    def sync_time(self) -> None:
        """
        Uses datetime to sync with system clock

        Notes:
            - This is the only time datetime module is used
        """
        self._log("Executing: syncTime")
        now = datetime.now()
        self._current_time[0] = now.second
        self._current_time[1] = now.minute
        self._current_time[2] = now.hour
        self._current_time[3] = now.day + self._MONTH_OFFSETS[now.month]
        self._current_time[4] = now.year
        self._log("sync_time returned: None")
        return None

    def initializer(self) -> None:
        """
        Takes the settings dictionary from settings.py and sets _SETTINGS_DICT equal to itself.

        Parameters:
            No parameters

        Notes:
            - If ran more than once, logs will show a RuntimeError, but it will not be raised
        """
        self._log("Executing: initializer")
        self._SETTINGS_DICT = settings.settings_dict
        try:
            self._ticking_thread.start()
        except RuntimeError:
            self._log("RuntimeError in initializer")
        if self._SETTINGS_DICT["start_counting"]:
            self.start_ticking()
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
        self._log("Executing: get_time")
        if requested_time_unit == "all":
            requested_time = self._current_time.copy()
        elif requested_time_unit == "dom":
            requested_time = self._get_day()
        elif requested_time_unit == "month":
            requested_time = self._get_month()
        else:
            try:
                requested_time = self._current_time[self._KEYS[requested_time_unit]]
            except KeyError:
                self._log(f"KeyError in get_time, requested_time_unit = {requested_time_unit}")
                raise KeyError(f"{requested_time_unit} is not a valid unit of time")
        self._log(f"get_time returned: {requested_time}")
        return requested_time

    def set_time(self, new_time: list[int]) -> None:
        """
        Gives the developer an easy way to set a custom time while the program is runnning

        Parameters:
            new_time (list[int]): a list of 5 integers with the new time

        Notes:
            - Exception will be raised if the length of the list is not five
            - New time is automatically normalized
            - Negative values are not supported
        """
        # Gives the developer ability to set a custom time if needed.
        self._log("Executing: set_time")
        for i in range(0, 5):
            if new_time[i] < 0:
                self._log(f"ValueError in set_time, newTime = {new_time}")
                raise ValueError("The new time provided contains a negative value")
        if len(new_time) != 5:
            self._log(f"Exception in set_time, new_time = {new_time}")
            raise Exception("List provided is not the right size (5)")
        self._current_time = new_time
        self._normalize()
        self._log("set_time returned: None")
        return None

    def start_ticking(self) -> None:
        """
        Easy way to start ticking the clock
        """
        # Gives the dev an easy way to start ticking the clock.
        self._log("Executing: start_ticking")
        self._isTicking = True
        self._log("start_ticking returned: None")
        return None

    def stop_ticking(self) -> None:
        """
        Easy way to stop the clock
        """
        # Gives the dev an easy way to stop ticking the clock.
        self._log("Executiong: stop_ticking")
        self._isTicking = False
        self._log("stop_ticking returned: None")
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
            - Supported units include: "sec", "min", "hour", "day", "year".
            - "day" refers to the days that have passed in the current year
        """
        self._log("Executing: convert")
        try:
            converted = value
            if self._KEYS[fromType] < self._KEYS[toType]:
                for i in range(self._KEYS[fromType], self._KEYS[toType]):
                    converted /= self._CONSTS[i]
            elif self._KEYS[fromType] > self._KEYS[toType]:
                for i in range(self._KEYS[toType], self._KEYS[fromType]):
                    converted *= self._CONSTS[i]
            elif self._KEYS[fromType] == self._KEYS[toType]:
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
        self._log("Executing: _get_day")
        month = self._get_month()
        day = self._current_time[3] - self._MONTH_OFFSETS[month]
        self._log(f"_get_day returned: {day}")
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
        self._log("Executing: _get_month")
        month = 13
        if self._current_time[3] < 0 or self._current_time[3] > 366:
            self._log(f"ValueError in _get_month, _current_time = {self._current_time}")
            raise ValueError("Internal error happened")
        for k in range(1, 13):
            if (self._MONTH_OFFSETS[k] < self._current_time[3] and
                    self._current_time[3] <= self._MONTH_OFFSETS[k + 1]):
                month = k
        self._log(f"_get_month returned: {month}")
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
        amount = self.convert(amount, unit_type, "sec")     # Convert to seconds, it is easier to work with them
        self._current_time[self._KEYS["sec"]] -= amount
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
        self._log("Executing: return_clk_style")
        day = self._get_day()
        month = self._get_month()
        timeNow = (str(self._current_time[self._KEYS["hour"]]) + ":" +
                   str(self._current_time[self._KEYS["min"]]) + ":" +
                   str(self._current_time[self._KEYS["sec"]]) + ", " +
                   str(day) + "/" +
                   str(month) + "/" +
                   str(self._current_time[self._KEYS["year"]]))
        self._log(f"return_clk_style returned: {timeNow}")
        return timeNow

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