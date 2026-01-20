import time  #need this for counting seconds
import threading
from datetime import datetime   #need this for syncing with pc clock
import settings

_KEYS = {
    "sec": 0,   
    "min": 1,   
    "hour": 2,  
    "day": 3,
    "year": 4,
}
_current_time = [0, 0, 0, 0, 0]
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
_SETTINGS_DICT = {
    "default_time": [0, 0, 0, 0, 0],
    "tickInterval": 1,
    "syncOnStart": False,
    "showTestOutput": False,
    "doUnitTests": False,
    "startCounting": False
}
_isTicking = False

def initializer() -> None:
    global _SETTINGS_DICT
    _SETTINGS_DICT = settings.settingsDict
    _ticking_thread.start()
    if _SETTINGS_DICT["startCounting"]:
        start_ticking()
    if _SETTINGS_DICT["syncOnStart"]:
        sync_time()
    _log(0, "None")
    return None

def sync_time() -> None:
    _log(1, "syncTime")
    global _current_time
    now = datetime.now()
    _current_time[0] = now.second
    _current_time[1] = now.minute
    _current_time[2] = now.hour
    _current_time[3] = now.day + _MONTH_OFFSETS[now.month]
    _current_time[4] = now.year
    _log(0, "None")
    return None

def get_time(tip: str) -> int or list:
    _log(1, "getTime")
    if tip == "all":
        _log(0, str(_current_time.copy))
        return _current_time.copy()
    elif tip == "dom":
        var17 = _get_day()
        _log(0, str(var17))
        return var17
    elif tip == "month":
        var18 = _get_month()
        _log(0, str(var18))
        return var18
    else:
        try:
            _log(0, str(_current_time[_KEYS[tip]]))
            return _current_time[_KEYS[tip]]
        except KeyError:
            _log(-1, "KeyError in get_time")
            raise KeyError(f"{tip} is not a valid unit of time")

def set_time(newTime: list[int]) -> None:
    _log(1, "setTime")
    global _current_time
    if len(newTime) != 5:
        _log(-1, "Exception in set_time")
        raise Exception("List provided is too big (bigger than 5)")
    _current_time = newTime
    _log(0, "None")
    return None

def _tick():
    global _tickInterval
    while True:
        time.sleep(_SETTINGS_DICT["tickInterval"])
        if _isTicking:
            increase_time("sec", 1)
_ticking_thread = threading.Thread(target=_tick, daemon=True)

def increase_time(tip: str, amount: int) -> None:
    _log(1, "increaseTime")
    if amount < 0:
        _log(-1, "ValueError in increase_time")
        raise ValueError("The value has to be bigger then zero")
    try:
        _current_time[_KEYS[tip]] += amount
    except KeyError:
        _log(-1, "KeyError in increase_time")
        raise KeyError("Invalid Key")
    _normalize()
    _log(0, "None")
    return None

def start_ticking() -> None:
    _log(1, "startTicking")
    global _isTicking
    _isTicking = True
    _log(0, "None")
    return None

def stop_ticking() -> None:
    _log(1, "stopTicking")
    global _isTicking
    _isTicking = False
    _log(0, "None")
    return None

def convert(convertFrom: int, fromType: str, convertTo: str) -> int:
    _log(1, "convert")
    try:
        converted = convertFrom
        if _KEYS[fromType] < _KEYS[convertTo]:
            for i in range(_KEYS[fromType], _KEYS[convertTo]):
                converted /= _CONSTS[i]
        elif _KEYS[fromType] > _KEYS[convertTo]:
            for i in range(_KEYS[convertTo], _KEYS[fromType]):
                converted *= _CONSTS[i]
        elif _KEYS[fromType] == _KEYS[convertTo]:
            _log(0, str(converted))
            return convertFrom
    except KeyError:
        _log(-1, "KeyError in convert")
        raise KeyError(f"Either {fromType} or {convertTo} is an invalid time unit")
    _log(0, str(converted))
    return converted

def _get_day() -> int:
    _log(1, "_getDay")
    month = _get_month()
    day = _current_time[3] - _MONTH_OFFSETS[month]
    _log(0, str(day))
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
    _log(1, "_getMonth")
    month = 13
    if _current_time[3] < 0 or _current_time[3] > 366:
        _log(-1, "ValueError in _get_month")
        raise ValueError("Internal error happened")
    for k in range(1, 13):
        if _MONTH_OFFSETS[k] < _current_time[3] and _current_time[3] <= _MONTH_OFFSETS[k + 1]:
            month = k
    _log(0, str(month))
    return month

def __decrease_time(tip: str, amount: int) -> None:
    _log(1, "__decrease_time")
    # Not finished. Should not be used.
    # TODO: fix
    try:
        _current_time[_KEYS[tip]] -= amount
        while _current_time[_KEYS[tip]] < 0:
            _current_time[_KEYS[tip] + 1] -= 1
            _current_time[_KEYS[tip]] += _CONSTS[_KEYS[tip]]
        while _current_time[_KEYS[tip] + 1] < 0:
            _current_time[_KEYS[tip] + 2] -= 1
            _current_time[_KEYS[tip] + 1] += _CONSTS[_KEYS[tip] + 1]
        while _current_time[_KEYS[tip] + 2] < 0:
            _current_time[_KEYS[tip] + 3] -= 1
            _current_time[_KEYS[tip] + 2] += _CONSTS[_KEYS[tip] + 2]

    except KeyError:
        _log(-1, "KeyError in __decrease_time")
        raise KeyError(f"{tip} is not a supported unit of time")
    except IndexError:
        _log(-1, "IndexError in __decrease_time")
        raise IndexError("Minutes, seconds and hours allowed")
    _normalize()
    _log(0, "None")
    return None

def print_nicely() -> None:
    print("Seconds: " + str(_current_time[0]) +
          ", Minutes: " + str(_current_time[1]) +
          ", Hours: " + str(_current_time[2]) +
          ", Days: " + str(_current_time[3]) +
          ", Years: " + str(_current_time[4])
          )
    _log(0, "None")
    return None

def return_clk_style() -> str:
    _log(1, "return_clk_style")
    day = _get_day()
    month = _get_month()
    timeNow = (str(_current_time[_KEYS["hour"]]) + ":" +
               str(_current_time[_KEYS["min"]]) + ":" +
               str(_current_time[_KEYS["sec"]]) + ", " +
               str(day) + "/" +
               str(month) + "/" +
               str(_current_time[_KEYS["year"]]))
    _log(0, timeNow)
    return timeNow

def _normalize() -> None:
    for i in range(0, 4):
        if _current_time[i] >= _CONSTS[i]:
            _current_time[i] -= _CONSTS[i]
            _current_time[i + 1] += 1
            _normalize()
    _log(0, "None")
    return None

def change_settings(name: str, value) -> None:
    _log(1, "changeSettings")
    try:
        _SETTINGS_DICT[name] = value
    except KeyError:
        _log(-1, "KeyError")
        raise KeyError(f"{name} does not exists as a settings")
    with open("settings.py", "w") as f:
        f.write("settingsDict = " + str(_SETTINGS_DICT))
    _log(0, "None")
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