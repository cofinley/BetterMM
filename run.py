import os
import glob
import datetime
import argparse

import music_manager
from config.config import Config


def check_verbosity() -> bool:
	"""
	Parse args for verbosity. If found, (re)run through config prompts

	Returns:
		True if -v or --verbose arg used, False if not
	"""
	parser = argparse.ArgumentParser(
		description="Upload music to Google Music by directory, file extension, and date range"
	)
	parser.add_argument("-v", "--verbose", help="(Re)run through config prompts",
						action="store_true")
	args = parser.parse_args()

	return args.verbose


# HACK get conf to be global so start and end dates can be used globally
is_verbose = check_verbosity()
if is_verbose:
	print("Mode: verbose")
	conf = Config(verbose=True)
else:
	print("Mode: regular")
	conf = Config()

start = conf.start_unix_time
end = conf.end_unix_time


def check_date(f: object) -> bool:

	"""
	Function used to filter files by time range.
	Time is based on when files were copied to dir

	Args:
		f: file from iterator

	Returns:
		True if file falls within date ranges
	"""

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



def get_new_files(music_dir: str, ext: str) -> iter:
	"""
	Find all files with given extension in the given directory that were added
	in the configured date range.

	Args:
		music_dir: absolute file path of music directory
		ext: file extension to look for (mp3, flac)

	Returns:
		new_itr: iterator of files that matched the parameters
	"""
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
		return new_itr
	else:
		return None

	# TODO include future_uploads if any


def main():
	"""
	Main logic.
	Cycle through given file extensions and upload the results.
	After finishing, reset date range to [today, inf)
	"""

	# TODO run with stdout to timestamped file (python run.py > YYYY-MM-DD_output.log
	# 	%date:~-4,4%-%date:~-10,2%-%date:~-7,2%_output.log

	music_dir = conf.get("dir")
	for idx, ext in enumerate(conf.get("ext")):
		print("({}/{}) Checking for {}'s...".format(idx, len(ext), ext))
		print("\tPattern: {}**{}*.{}\n".format(music_dir, os.sep, ext))
		new_file_itr = get_new_files(music_dir, ext)
		if new_file_itr:
			upload_readout = music_manager.upload(new_file_itr)
			music_manager.parse_result(upload_readout)
		else:
			print("No new files found")

	# Update conf's start date to today
	# Update end_date to blank, basically removing the bound
	if is_verbose:
		today = datetime.datetime.today().strftime("%Y-%m-%d")
		conf.set("start_date", today)
		conf.set("end_date", "")


if __name__ == '__main__':
	main()
