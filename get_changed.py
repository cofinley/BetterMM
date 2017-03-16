import os
import itertools
import datetime
import glob

date_format = "%Y-%m-%d"

filepath = "<dir here>/"
ext = ""
given_date = ""

unix_time = datetime.datetime.strptime(given_date, date_format)

files = glob.iglob(filepath + "**." + ext, recursive=True)

for i in files:
	print(i)

print("**************************************")

def check_date(f):
	if os.path.getctime(f) > given_date:
		return true

new_files = itertools.takewhile(check_date, files)

for i in new_files:
	print(i)
