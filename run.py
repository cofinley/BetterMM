import os
import glob
import datetime

import music_manager
from config.config import Config
conf = Config()

start = conf.start_unix_time
end = conf.end_unix_time


def check_date(f: object) -> bool:

	""" Function used to filter files by time range.
	Time is based on when files wered copied to dir
	:param f: file from iterator
	:return: True if file falls within date ranges"""

	if start and end:
		# Range: [start, end)
		return start <= os.path.getctime(f) < end
	else:
		if start and not end:
			# Range: [start, inf)
			return start <= os.path.getctime(f)
		elif end and not start:
			# Range: (inf, end)
			return os.path.getctime(f) < end



def get_new_files():
	"""
	For every music file extension, find all files in the given directory that were added
	in the configured date range.
	"""

	music_dir = conf.get("dir")
	for idx, ext in enumerate(conf.get("ext")):

		print("({}/{}) Checking for {}'s...".format(idx, len(ext), ext))
		print("\tPattern: {}**{}*.{}\n".format(music_dir, os.sep, ext))
		# recursive argument only appears in python 3.5+
		files = glob.iglob("{}**{}*.{}".format(music_dir, os.sep, ext), recursive=True)

		new_files = filter(check_date, files)
		# Create duplicate iterators. One for upload, one for showing to user
		new_itr = list(new_files)
		show_itr = new_itr

		if len(show_itr) > 0:
			print("These {} files will be uploaded:".format(len(show_itr)))
			print(*show_itr, sep="\n")
			print("**************************************")
			music_manager.upload(new_itr)
		else:
			print("None Found")


def main():
	"""
	Main logic.
	"""
	# Find newer files and upload them

	# TODO Add args to allow running without prompts (-v or something)
	# TODO run with stdout to timestamped file (python run.py > YYYY-MM-DD_output.log
	# 	%date:~-4,4%%date:~-7,2%%date:~-10,2%_output.log

	# TODO maybe iterate of ext here and have the function return so it can be passed to upload()
	# 	would be more functional that way instead of nesting upload function inside the first function
	get_new_files()

	# Update conf's start date to today
	today = datetime.datetime.today().strftime("%Y-%m-%d")
	conf.set("start_date", today)


if __name__ == '__main__':
	main()
