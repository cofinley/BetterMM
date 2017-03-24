import os
import sys
import glob
import datetime
import argparse
import codecs
import time

import music_manager
from config.config import Config

current_dir = os.path.dirname(os.path.realpath(__file__))

# Create timestamped log file which pipes from print() using stdout
today = datetime.datetime.today().strftime("%Y-%m-%d")
temp = sys.stdout
log_file = "{}{}{}{}{}.log".format(current_dir,
									os.sep,
									"logs",
									os.sep,
									today)
sys.stdout = codecs.open(log_file, 'w', "utf-8")


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


# HACK get conf to be global so start and end dates can be used globally in this file
# Don't want to redefine start and end every time check_date is called for every file
is_verbose = check_verbosity()
if is_verbose:
	print("Mode: verbose")
	conf = Config(verbose=True)
else:
	print("Mode: non-verbose (no prompts)")
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


def get_failed_uploads() -> iter:
	"""
	Get failed uploads from last session.
	Returns:
		failed_uploads: iterator with file paths of songs
		False if failed_uploads empty
	"""
	failed_uploads = conf.get("failed_uploads")
	if len(failed_uploads) == 0:
		return False
	return failed_uploads


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
		print("**************************************")
		print("These {} files will be uploaded:".format(len(show_itr)))
		print(*show_itr, sep="\n")
		print("**************************************\n")
		return new_itr
	else:
		return None


def main():
	"""
	Main logic.
	Cycle through given file extensions and upload the results.
	After finishing, reset date range to [today, inf)
	"""

	script_start = time.time()

	upload_success = False
	music_dir = conf.get("dir")
	exts = conf.get("ext")
	exts_len = len(exts)
	for idx, ext in enumerate(exts):
		print("\n({}/{}) Checking for {}'s...".format(idx+1, exts_len, ext))
		print("\tPattern: {}**{}*.{}\n".format(music_dir, os.sep, ext))
		new_file_itr = get_new_files(music_dir, ext)
		if new_file_itr:
			upload_success = music_manager.process(new_file_itr, conf)
		else:
			print("No new files found.\n")

	# Upload failed songs from last time if there are any
	retry_songs = get_failed_uploads()
	if retry_songs:
		print("Retrying songs that failed last time...")
		music_manager.process(retry_songs, conf)

	# Update date range if upload was a success
	# start_date => today
	# end_date => remove the bound
	if upload_success:
		conf.set("start_date", today)
		conf.set("end_date", "")

	script_end = time.time()

	total_time = (script_end - script_start)/60
	print("\nFinished.\n\nTotal time: {:.2f} minutes".format(total_time))

	# Clean up log file use
	sys.stdout.close()
	sys.stdout = temp

if __name__ == '__main__':
	main()
