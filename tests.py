from basicTime import Clock

c = Clock()

c.initializer()
if True == True:
    _CONSTS = [60, 60, 24, 365]
    overall_pass = True
    passed1 = True
    for i in range(0, 1250):
        c.increase_time("sec", 1000)
    for a in range(0, 4):
        _current_time = c.get_time("all")
        if _current_time[a] < _CONSTS[a] and _current_time[a] >= 0:
            pass
        else:
            passed1, overall_pass = False, False
    passed2 = True
    i = 0
    for i in range(0, 1200):
        c.decrease_time("sec", 1)
    for a in range(0, 4):
        _current_time = c.get_time("all")
        if _current_time[a] < _CONSTS[a] and _current_time[a] >= 0:
            pass
        else:
            passed2 = False

    passed3 = False
    c._current_time = [0, 0, 0, -1, 0]
    try:
        month = c._get_month()
    except ValueError:
        passed3 = True
    if not passed3:
        overall_pass = False

    passed4 = True
    c._current_time = [0, 0, 0, 370, 0]
    try:
        month = c._get_month()
    except ValueError:
        passed4 = True
    if not passed4:
        overall_pass = False

    passed5 = True
    c.set_time([0, 0, 0, 200, 0])
    day = c.get_time("dom")
    if day != 19:
        passed5, overall_pass = False, False

    passed6 = True
    var2 = c.convert(1, "day", "sec")
    if var2 != 86400:
        passed6, overall_pass = False, False

    passed7 = True
    var2 = c.convert(86400, "sec", "day")
    if var2 != 1:
        passed7, overall_pass = False, False

    passed8 = True
    var2 = c.convert(12, "sec", "sec")
    if var2 != 12:
        passed8, overall_pass = False, False

    passed9 = False
    try:
        var2 = c.convert(10, "key", "another")
    except KeyError:
        passed9 = True
    if passed9 == False:
        overall_pass = False

    passed10 = False
    try:
        c.set_time([-1, "a", 1000, "eg", 2])
    except ValueError:
        passed10 = True
    if not passed10:
        overall_pass = False

    passed11 = False
    try:
        c.change_settings("hell naw", True)
    except KeyError:
        passed11 = True
    if not passed11:
        overall_pass = False
    if True == True:
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
        print("Test 10 passed") if passed10 == True else print("Test 10 failed")
        print("Test 11 passed") if passed11 == True else print("Test 11 failed")
        print("All tests passed") if overall_pass == True else print("A test/s failed")

        print("*** END OF UNIT TESTS ***")
input()

