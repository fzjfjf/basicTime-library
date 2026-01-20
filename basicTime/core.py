import time  #need this for counting seconds
import threading
from datetime import datetime   #need this for syncing with pc clock
import settings

FUNCTION_RAN = 1            # Used for _log() instead of magic numbers
FUNCTION_RETURNED = 0
FUNCTION_RAISED = -1
_KEYS = {           # Contains index positions of the units. Made for easier use of current_time.
    "sec": 0,   
    "min": 1,   
    "hour": 2,  
    "day": 3,
    "year": 4,
}
_current_time = [0, 0, 0, 0, 0]     # Heart of the library. Units are in this order: [sec, min, hour, day of year, year].
_CONSTS = [60, 60, 24, 365]         # Lenght of every unit until rollover to the next.
_MONTH_OFFSETS = {                  # Amount of days that have passed in a year before the month in the key
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
_SETTINGS_DICT = {                  # Contains setting names, this is a fallback if initializer() is not run.
    "default_time": [0, 0, 0, 0, 0],# Same settings are stored in the file named settings.py. Those settings need to be
    "tickInterval": 1,              # stored externally to not reset everytime.
    "syncOnStart": False,
    "showTestOutput": False,
    "doUnitTests": False,
    "startCounting": False
}
_isTicking = False

def initializer() -> None:
    # Takes the settings dictionary from settings.py and sets _SETTINGS_DICT equal to itself.
    # Also checks for startCounting setting and syncOnStart settings and does the action needed for them
    # IMPORTANT! Must not be run more than once because it starts a background thread, and if the thread is already
    # running, it WILL give a RuntimeError
    _log(FUNCTION_RAN, "initializer")
    global _SETTINGS_DICT
    _SETTINGS_DICT = settings.settingsDict
    _ticking_thread.start()
    if _SETTINGS_DICT["startCounting"]:
        start_ticking()
    if _SETTINGS_DICT["syncOnStart"]:
        sync_time()
    _log(FUNCTION_RETURNED, "None")
    return None

def sync_time() -> None:
    # Uses datetime.now() to sync to the current time. This is the only place datetime is used
    _log(FUNCTION_RAN, "syncTime")
    global _current_time
    now = datetime.now()
    _current_time[0] = now.second
    _current_time[1] = now.minute
    _current_time[2] = now.hour
    _current_time[3] = now.day + _MONTH_OFFSETS[now.month]
    _current_time[4] = now.year
    _log(FUNCTION_RETURNED, "None")
    return None

def get_time(requested_time_unit: str) -> int or list:
    # The main way of getting time from the library.
    _log(FUNCTION_RAN, "getTime")
    if requested_time_unit == "all":
        requested_time = _current_time.copy()
    elif requested_time_unit == "dom":
        requested_time = _get_day()
    elif requested_time_unit == "month":
        requested_time = _get_month()
    else:
        try:
            requested_time = _current_time[_KEYS[requested_time_unit]]
        except KeyError:
            _log(FUNCTION_RAISED, "KeyError in get_time")
            raise KeyError(f"{requested_time_unit} is not a valid unit of time")
    _log(FUNCTION_RETURNED, str(requested_time))
    return requested_time

def set_time(newTime: list[int]) -> None:
    # Gives the developer ability to set a custom time if needed.
    _log(FUNCTION_RAN, "setTime")
    global _current_time
    if len(newTime) != 5:
        _log(FUNCTION_RAISED, "Exception in set_time")
        raise Exception("List provided is too big (bigger than 5)")
    _current_time = newTime
    _log(FUNCTION_RETURNED, "None")
    return None

def _tick():
    global _tickInterval
    while True:
        time.sleep(_SETTINGS_DICT["tickInterval"])
        if _isTicking:
            increase_time("sec", 1)
_ticking_thread = threading.Thread(target=_tick, daemon=True)

def increase_time(unit_type: str, amount: int) -> None:
    # Gives the developer ability to increase time easily.
    # Overflow is automatically converted.
    # Negative amounts are not allowed.
    _log(FUNCTION_RAN, "increaseTime")
    if amount < 0:
        _log(FUNCTION_RAISED, f"ValueError in increase_time, amount = {amount}  unit_type = {unit_type}")
        raise ValueError("The value has to be bigger than zero")
    try:
        _current_time[_KEYS[unit_type]] += amount
    except KeyError:
        _log(FUNCTION_RAISED, f"KeyError in increase_time, unit_type = {unit_type}  amount = {amount}")
        raise KeyError(f"{unit_type} is an invalid unit of time")
    _normalize()
    _log(FUNCTION_RETURNED, "None")
    return None

def start_ticking() -> None:
    # Gives the dev an easy way to start ticking the clock.
    _log(FUNCTION_RAN, "startTicking")
    global _isTicking
    _isTicking = True
    _log(FUNCTION_RETURNED, "None")
    return None

def stop_ticking() -> None:
    # Gives the dev an easy way to stop ticking the clock.
    _log(FUNCTION_RAN, "stopTicking")
    global _isTicking
    _isTicking = False
    _log(FUNCTION_RETURNED, "None")
    return None

def convert(convertFrom: int, fromType: str, convertTo: str) -> int:
    #
    _log(FUNCTION_RAN, "convert")
    try:
        converted = convertFrom
        if _KEYS[fromType] < _KEYS[convertTo]:
            for i in range(_KEYS[fromType], _KEYS[convertTo]):
                converted /= _CONSTS[i]
        elif _KEYS[fromType] > _KEYS[convertTo]:
            for i in range(_KEYS[convertTo], _KEYS[fromType]):
                converted *= _CONSTS[i]
        elif _KEYS[fromType] == _KEYS[convertTo]:
            _log(FUNCTION_RETURNED, str(converted))
            return convertFrom
    except KeyError:
        _log(FUNCTION_RAISED, f"KeyError in convert, convertFrom = {convertFrom}  fromType = {fromType}  convertTo = {convertTo}")
        raise KeyError(f"Either '{fromType}' or '{convertTo}' is an invalid time unit")
    _log(FUNCTION_RETURNED, str(converted))
    return converted

def _get_day() -> int:
    _log(FUNCTION_RAN, "_getDay")
    month = _get_month()
    day = _current_time[3] - _MONTH_OFFSETS[month]
    _log(FUNCTION_RETURNED, str(day))
    return day

def _log(code: int, additional_info: str) -> None:
    # Get the time to put into the log
    seconds = _current_time[0]
    minutes = _current_time[1]
    hours = _current_time[2]
    month = -1
    for a in range(1, 13):
        if _MONTH_OFFSETS[a] < _current_time[3] and _current_time[3] <= _MONTH_OFFSETS[a + 1]:
            month = a
    if month != -1:
        day = _current_time[3] - _MONTH_OFFSETS[month]
    else:
        day = -1
    year = _current_time[4]
    # Use with to automatically close the file
    with open("log.txt", "a") as log_file:
        if code == 1:           # 1 means a function is called
            log_file.write(f"{hours}:{minutes}:{seconds}, {day}/{month}/{year}, " + f"Executing {additional_info}\n")
        elif code == 0:         # 0 means the function finished correctly and returned a value
            log_file.write(f"{hours}:{minutes}:{seconds}, {day}/{month}/{year}, " + f"Function returned: {additional_info}\n")
        elif code == -1:        # -1 means that an error was raised
            log_file.write(f"{hours}:{minutes}:{seconds}, {day}/{month}/{year}, " + f"Function raised: {additional_info}\n")
    return None

def _get_month() -> int:
    _log(FUNCTION_RAN, "_getMonth")
    month = 13
    if _current_time[3] < 0 or _current_time[3] > 366:
        _log(FUNCTION_RAISED, f"ValueError in _get_month, _current_time = {_current_time}")
        raise ValueError("Internal error happened")
    for k in range(1, 13):
        if _MONTH_OFFSETS[k] < _current_time[3] and _current_time[3] <= _MONTH_OFFSETS[k + 1]:
            month = k
    _log(FUNCTION_RETURNED, str(month))
    return month

def __decrease_time(unit_type: str, amount: int) -> None:
    _log(FUNCTION_RAN, "__decrease_time")
    # Not finished. Should not be used.
    # TODO: fix
    try:
        _current_time[_KEYS[unit_type]] -= amount
        while _current_time[_KEYS[unit_type]] < 0:
            _current_time[_KEYS[unit_type] + 1] -= 1
            _current_time[_KEYS[unit_type]] += _CONSTS[_KEYS[unit_type]]
        while _current_time[_KEYS[unit_type] + 1] < 0:
            _current_time[_KEYS[unit_type] + 2] -= 1
            _current_time[_KEYS[unit_type] + 1] += _CONSTS[_KEYS[unit_type] + 1]
        while _current_time[_KEYS[unit_type] + 2] < 0:
            _current_time[_KEYS[unit_type] + 3] -= 1
            _current_time[_KEYS[unit_type] + 2] += _CONSTS[_KEYS[unit_type] + 2]

    except KeyError:
        _log(FUNCTION_RAISED, f"KeyError in __decrease_time, unit_type = {unit_type}")
        raise KeyError(f"{unit_type} is not a supported unit of time")
    except IndexError:
        _log(FUNCTION_RAISED, f"IndexError in __decrease_time, unit_time = {unit_type}")
        raise IndexError("Only minutes, seconds and hours allowed")
    _normalize()
    _log(FUNCTION_RETURNED, "None")
    return None

def print_nicely() -> None:
    _log(FUNCTION_RAN, "print_nicely")
    print("Seconds: " + str(_current_time[0]) +
          ", Minutes: " + str(_current_time[1]) +
          ", Hours: " + str(_current_time[2]) +
          ", Days: " + str(_current_time[3]) +
          ", Years: " + str(_current_time[4])
          )
    _log(FUNCTION_RETURNED, "None")
    return None

def return_clk_style() -> str:
    _log(FUNCTION_RAN, "return_clk_style")
    day = _get_day()
    month = _get_month()
    timeNow = (str(_current_time[_KEYS["hour"]]) + ":" +
               str(_current_time[_KEYS["min"]]) + ":" +
               str(_current_time[_KEYS["sec"]]) + ", " +
               str(day) + "/" +
               str(month) + "/" +
               str(_current_time[_KEYS["year"]]))
    _log(FUNCTION_RETURNED, timeNow)
    return timeNow

def _normalize() -> None:
    for i in range(0, 4):
        if _current_time[i] >= _CONSTS[i]:
            _current_time[i] -= _CONSTS[i]
            _current_time[i + 1] += 1
            _normalize()
    _log(FUNCTION_RETURNED, "_initializer returned None")
    return None

def change_settings(name: str, value) -> None:
    _log(FUNCTION_RAN, "changeSettings")
    try:
        _SETTINGS_DICT[name] = value
    except KeyError:
        _log(FUNCTION_RAISED, f"KeyError in change_settings, name = {name}  value = {value}")
        raise KeyError(f"{name} does not exists as a settings")
    with open("settings.py", "w") as f:
        f.write("settingsDict = " + str(_SETTINGS_DICT))
    _log(FUNCTION_RETURNED, "None")
    return None


# This is a basic CLI built into the library itself - used for quick tests
if __name__ == "__main__":
    initializer()
    if _SETTINGS_DICT["doUnitTests"] == True:
        overall_pass = True
        passed1 = True
        for i in range(0, 1250):
            increase_time("sec", 1000)
        for a in range(0, 4):
            if _current_time[a] < _CONSTS[a] and _current_time[a] >= 0:
                pass
            else:
                passed1, overall_pass = False, False
        passed2 = True
        i = 0
        for i in range(0, 1200):
            __decrease_time("sec", 1)
        for a in range(0, 4):
            if _current_time[a] < _CONSTS[a] and _current_time[a] >= 0:
                pass
            else:
                passed2, overall_pass = False, False

        passed3 = True
        _current_time[3] = -1
        month = _get_month()
        if month != None:
            passed3, overall_pass = False, False

        passed4 = True
        _current_time[3] = 370
        month = _get_month()
        if month != None:
            passed4, overall_pass = False, False

        passed5 = True
        _current_time[3] = 200
        day = _get_day()
        if day != 19:
            passed5, overall_pass = False, False

        passed6 = True
        var2 = convert(1, "day", "sec")
        if var2 != 86400:
            passed6, overall_pass = False, False

        passed7 = True
        var2 = convert(86400, "sec", "day")
        if var2 != 1:
            passed7, overall_pass = False, False

        passed8 = True
        var2 = convert(12, "sec", "sec")
        if var2 != 12:
            passed8, overall_pass = False, False

        passed9 = False
        try:
            var2 = convert(10, "key", "another")
        except KeyError:
            passed9 = True
        if not passed9:
            overall_pass = False

        if _SETTINGS_DICT["showTestOutput"] == True:
            print("*** START OF UNIT TESTS ***")

            print("Test 1 passed") if passed1 == True else print("Test 1 failed")
            print("Test 2 passed") if passed2 == True else print("Test 2 failed")
            print("Test 3 passed") if passed3 == True else print("Test 3 failed")
            print("Test 4 passed") if passed4 == True else print("Test 4 failed")
            print("Test 5 passed") if passed5 == True else print("Test 5 failed")
            print("Test 6 passed") if passed6 == True else print("Test 6 failed")
            print("Test 7 passed") if passed7 == True else print("Test 7 failed")
            print("Test 8 passed") if passed8 == True else print("Test 8 failed")
            print("Test 9 passed") if passed9 == True else print("Test 9 failed")
            print("All tests passed") if overall_pass == True else print("A test/s failed, terminating program...")

            print("*** END OF UNIT TESTS ***")

    if _SETTINGS_DICT["doUnitTests"] == False:
        overall_pass = True

    if _SETTINGS_DICT["syncOnStart"] == True:
        sync_time()

    while overall_pass == True:
        try:
            ui = input("> ")
        except KeyboardInterrupt:
            print("""
    Terminating program...""")
            break
        if ui == "print":
            print_nicely()
        elif ui == "increaseTime":
            increase_time(input("type: "), int(input("amount: ")))
        elif ui == "decreaseTime":
            __decrease_time(input("type: "), int(input("amount: ")))
        elif ui == "exit":
            break
        elif ui == "":
            pass
        elif ui == "sync":
            sync_time()
        elif ui == "clk":
            print(return_clk_style())
        elif ui == "startt":
            start_ticking()
        elif ui == "stopt":
            stop_ticking()
        elif ui == "convert":
            var3 = convert(int(input("enter value ")), input("from "), input("to "))
            print("result:", var3)
        elif ui == "change":
            change_settings(input(), input())
        else:
            print("Not a command")