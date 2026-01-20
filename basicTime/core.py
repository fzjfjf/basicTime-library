import time  #need this for counting seconds
import threading
from datetime import datetime   #need this for syncing with pc clock
import settings

_keys = {
    "sec": 0,   
    "min": 1,   
    "hour": 2,  
    "day": 3,
    "year": 4,
    }
_curr_time = [0, 0, 0, 0, 0]
_consts = [60, 60, 24, 365]
_months = {
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
_settingsDict = {
    "default_time": [0, 0, 0, 0, 0],
    "tickInterval": 1,
    "syncOnStart": False,
    "showTestOutput": False,
    "doUnitTests": False,
    "startCounting": False
}

_isTicking = False

def initializer():
    global _settingsDict
    _settingsDict = settings.settingsDict
    _t.start()
    if _settingsDict["startCounting"]:
        startTicking()
    if _settingsDict["syncOnStart"]:
        syncTime()

def syncTime():
    _log(1, "syncTime")
    global _curr_time
    now = datetime.now()
    _curr_time[0] = now.second
    _curr_time[1] = now.minute
    _curr_time[2] = now.hour
    _curr_time[3] = now.day + _months[now.month]
    _curr_time[4] = now.year

def getTime(tip: str):
    _log(1, "getTime")
    if tip == "all":
        _log(0, str(_curr_time.copy))
        return _curr_time.copy()
    elif tip == "dom":
        var17 = _getDay()
        _log(0, str(var17))
        return var17
    elif tip == "month":
        var18 = _getMonth()
        _log(0, str(var18))
        return var18
    else:
        try:
            _log(0, str(_curr_time[_keys[tip]]))
            return _curr_time[_keys[tip]]
        except KeyError:
            _log(-1, "KeyError")
            raise KeyError(f"{tip} is not a valid unit of time")

def setTime(newTime: list[int]):
    _log(1, "setTime")
    global _curr_time
    if len(newTime) != 5:
        _log(-1, "Exception")
        raise Exception("List provided is too big (bigger than 5)")
    _curr_time = newTime

def _tick():
    global _tickInterval
    while True:
        time.sleep(_settingsDict["tickInterval"])
        if _isTicking:
            increaseTime("sec", 1)

_t = threading.Thread(target=_tick, daemon=True)

def increaseTime(tip: str, amount: int):
    _log(1, "increaseTime")
    if amount < 0:
        _log(-1, "ValueError")
        raise ValueError("The value has to be bigger then zero")
    try:
        _curr_time[_keys[tip]] += amount
    except KeyError:
        _log(-1, "KeyError")
        raise KeyError("Invalid Key!!!!!")
    _normalize()

def startTicking():
    _log(1, "startTicking")
    global _isTicking
    _isTicking = True

def stopTicking():
    _log(1, "stopTicking")
    global _isTicking
    _isTicking = False

def convert(convertFrom: int, fromType: str, convertTo: str) -> int:
    _log(1, "convert")
    try:
        converted = convertFrom
        if _keys[fromType] < _keys[convertTo]:
            for i in range(_keys[fromType], _keys[convertTo]):
                converted /= _consts[i]
        elif _keys[fromType] > _keys[convertTo]:
            for i in range(_keys[convertTo], _keys[fromType]):
                converted *= _consts[i]
        elif _keys[fromType] == _keys[convertTo]:
            _log(0, str(converted))
            return convertFrom
    except KeyError:
        _log(-1, "KeyError")
        raise KeyError(f"Either {fromType} or {convertTo} is an invalid time unit")
    _log(0, str(converted))
    return converted

def _getDay():
    _log(1, "_getDay")
    month = _getMonth()
    day = _curr_time[3] - _months[month]
    _log(0, str(day))
    return day

def _log(code: int, additional_info: str):
    s = _curr_time[0]
    mi = _curr_time[1]
    ho = _curr_time[2]
    mon = -1
    for a in range(1, 13):
        if _months[a] < _curr_time[3] and _curr_time[3] <= _months[a + 1]:
            mon = a
    if mon != -1:
        da = _curr_time[3] - _months[mon]
    else:
        da = -1
    ye = _curr_time[4]
    with open("log.txt", "a") as log_file:
        if code == 1:
            log_file.write(f"{ho}:{mi}:{s}, {da}/{mon}/{ye}, " + f"Executing {additional_info}\n")
        elif code == 0:
            log_file.write(f"{ho}:{mi}:{s}, {da}/{mon}/{ye}, " + f"Function returned: {additional_info}\n")
        elif code == -1:
            log_file.write(f"{ho}:{mi}:{s}, {da}/{mon}/{ye}, " + f"Function raised: {additional_info}\n")

def _getMonth():
    _log(1, "_getMonth")
    month = 13
    if _curr_time[3] < 0 or _curr_time[3] > 366:
        _log(-1, "ValueError")
        raise ValueError("Internal error happened")
    for k in range(1, 13):
        if _months[k] < _curr_time[3] and _curr_time[3] <= _months[k + 1]:
            month = k
    _log(0, str(month))
    return month

def decreaseTime(tip: str, amount: int):
    try:
        _curr_time[_keys[tip]] -= amount
        while _curr_time[_keys[tip]] < 0:
            _curr_time[_keys[tip] + 1] -= 1
            _curr_time[_keys[tip]] += _consts[_keys[tip]]
        while _curr_time[_keys[tip] + 1] < 0:
            _curr_time[_keys[tip] + 2] -= 1
            _curr_time[_keys[tip] + 1] += _consts[_keys[tip] + 1]
        while _curr_time[_keys[tip] + 2] < 0:
            _curr_time[_keys[tip] + 3] -= 1
            _curr_time[_keys[tip] + 2] += _consts[_keys[tip] + 2]

    except KeyError:
        raise KeyError(f"{tip} is not a supported unit of time")
    except IndexError:
        raise IndexError("Minutes, seconds and hours allowed")
    _normalize()

def printNicely():
    print("Seconds: " + str(_curr_time[0]) + ", Minutes: " + str(_curr_time[1]) + ", Hours: " + str(_curr_time[2]) + ", Days: " + str(_curr_time[3]) + ", Years: " + str(_curr_time[4]))

def returnClkStyle() -> str:
    day = _getDay()
    month = _getMonth()
    timeNow = (str(_curr_time[_keys["hour"]]) + ":" +
        str(_curr_time[_keys["min"]]) + ":" +
        str(_curr_time[_keys["sec"]]) + ", " +
        str(day) + "/" +
        str(month) + "/" +
        str(_curr_time[_keys["year"]]))
    return timeNow

def _normalize():
    for i in range(0, 4):
        if _curr_time[i] >= _consts[i]:
            _curr_time[i] -= _consts[i]
            _curr_time[i + 1] += 1
            _normalize()

def changeSettings(name: str, value):
    _log(1, "changeSettings")
    if value == "True" and name != "tickInterval":
        value = True
    elif value == "False" and name != "tickInterval":
        value = False
    elif name == "default_time":
        try:
            value = list(value)
        except ValueError:
            _log(-1, "ValueError")
            raise ValueError(f"{value} is not a valid default time")
    else:
        try:
            value = float(value)
        except ValueError:
            _log(-1, "ValueError")
            raise ValueError(f"{name} is an invalid value for any setting")
    try:
        _settingsDict[name] = value
    except KeyError:
        _log(-1, "KeyError")
        raise KeyError(f"{name} does not exists as a settings")
    with open("settings.py", "w") as f:
        f.write("settingsDict = " + str(_settingsDict))


if __name__ == "__main__":
    initializer()
    if _settingsDict["doUnitTests"]:
        overall_pass = True
        passed1 = True
        for i in range(0, 1250):
            increaseTime("sec", 1000)
        for a in range(0, 4):
            if _curr_time[a] < _consts[a] and _curr_time[a] >= 0:
                pass
            else:
                passed1, overall_pass = False, False
        passed2 = True
        i = 0
        for i in range(0, 1200):
            decreaseTime("sec", 1)
        for a in range(0, 4):
            if _curr_time[a] < _consts[a] and _curr_time[a] >= 0:
                pass
            else:
                passed2, overall_pass = False, False

        passed3 = True
        _curr_time[3] = -1
        month = _getMonth()
        if month != None:
            passed3, overall_pass = False, False

        passed4 = True
        _curr_time[3] = 370
        month = _getMonth()
        if month != None:
            passed4, overall_pass = False, False

        passed5 = True
        _curr_time[3] = 200
        day = _getDay()
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

        if _settingsDict["showTestOutput"]:
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

    if not _settingsDict["doUnitTests"]:
        overall_pass = True

    if _settingsDict["syncOnStart"]:
        syncTime()

    while overall_pass:
        try:
            ui = input("> ")
        except KeyboardInterrupt:
            print("""
    Terminating program...""")
            break
        if ui == "print":
            printNicely()
        elif ui == "increaseTime":
            increaseTime(input("type: "), int(input("amount: ")))
        elif ui == "decreaseTime":
            decreaseTime(input("type: "), int(input("amount: ")))
        elif ui == "exit":
            break
        elif ui == "":
            pass
        elif ui == "sync":
            syncTime()
        elif ui == "clk":
            printClkStyle()
        elif ui == "startt":
            startTicking()
        elif ui == "stopt":
            stopTicking()
        elif ui == "convert":
            var3 = convert(int(input("enter value ")), input("from "), input("to "))
            print("result:", var3)
        elif ui == "change":
            changeSettings(input(), input())
        else:

            print("Not a command, dumbass")
