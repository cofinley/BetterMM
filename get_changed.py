import os
import itertools
import datetime
import glob

from config import config

def parse(gen):
	for i in gen:
		yield i

date_format = "%Y-%m-%d"

filepath = config.get_var("dir")
if filepath == "":
	filepath=input("Where is your directory? (full path): ")
ext = "md"
given_date = config.get_var("start_date_here") or "1970-01-01"

unix_time = float(datetime.datetime.strptime(given_date, date_format).strftime("%S"))

# recursive argument only appears in python 3.5+
files = glob.iglob(filepath + "**." + ext, recursive=True)

parse(files)

print("**************************************")

def check_date(f):
	if os.path.getctime(f) > unix_time:
		return True

new_files = itertools.takewhile(check_date, files)

for i in new_files:
	print(i)
