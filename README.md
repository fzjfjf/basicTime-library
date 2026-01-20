basicTime library
basicTime is a simple-to-use time library. You can use it as a counter or to get time from the PC clock. The library REQUIRES a settings.py file to work. settings.py has these settings:
settingsDict = {'default_time': [0, 0, 0, 0, 0], 'tickInterval': 1, 'syncOnStart': False, 'showTestOutput': False, 'doUnitTests': False, 'startCounting': False}
To change the settings, either use changeSettings() fuction or edit settings.py manually. Ticking uses a background thread. 
Functions and examples
•	getTime(unitType: str)
  o	Returns the value shown in the table below
  Argument (str)	Output example	        Note
  „all“	          [14, 52, 14, 32, 2026]	Returns units in this order: [sec, min, hour, day, year]
  „month“	        2	                      Month in number form
  „dom“	          1	                      Day in the current month 
  „day“	          32	                    Current day of the year on the library's clock
  „min“	          52	                    Curent minute on the library's clock
  „sec“	          14	                    Current second on the library's clock
  „hour“	        14	                    Current hour on the library's clock
  „year“	        2026	                  Current year on the librayr's clock
  o	If argument is invalid, a KeyError will be raised
•	syncTime()
  o	Doesn't return anything
  o	Will sync time to the PC clock
•	initializer()
  o	Doesn’t return anything
  o	Needs to be run at the start to apply chosen settings
  o	Warning: can not be run more than once, as it starts a background thread. 
•	setTime(new_time: list[int])
  o	Doesn't return anything
  o	Will set time to the provided time
  o	Format of new time is a list with units in this order: seconds, minutes, hours, day of year, year
  o	Will raise an exception if the lenght of the list is NOT equal to 5.
•	increaseTime(unitType: str, value: int)
  o	Doesn't return anything
  o	Will increase the selected unit of time by the value provided
  o	If the value is below 0, ValueError will be raised. If an invalid unit of time is selected, a KeyError will be raised
  o	Supported units are: „sec“, „min“, „hour“, „day“, „year“.
•	startTicking()	
  o	Doesn't return anything
  o	If the clock is not ticking, it will start ticking
  o	If the clock is already ticking, nothing will happen
  •	stopTicking()  
  o	Doesn't return aynthing
  o	If the clock is ticking, it will stop ticking
  o	If the clock isnt ticking, nothing will happen
•	printNicely()
  o	Doesn't return anything
  o	Will print the current time to the console in this format:   
    Seconds: 2, Minutes: 44, Hours: 21, Days: 19, Years: 2026
•	printClkStyle()
  o	Returns a string with the current time formatted like this: 
    21:44:2, 19/1/2026
  o The string IS NOT zero-padded
•	convert(value: int, unitFrom: str, unitTo, str)
  o	Returns the converted value. If unitFrom and unitTo are the same, the provided value will be returned. 
  o	If an invalid unit is provided, a KeyError will be raised
•	changeSettings(settingName: str, value)
  o	Doesn't return anything
  o	Takes two arguments: first one has the name of the setting, second one has the value.
  o	If the chosen setting does not exist, a KeyError will be raised. 
