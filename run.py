import os
import glob
import datetime
import argparse
import time

import music_manager
from config.config import Config
from logs.logger import main_logger

current_dir = os.path.dirname(os.path.realpath(__file__))
today = datetime.datetime.today()
today_date = today.strftime("%Y-%m-%d")  # YYYY-MM-DD
today_time = today.strftime("%I:%M %p")  # i.e. 7:00 PM
today_time_unix = int(today.timestamp())


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
	main_logger.info("Mode: verbose\n")
else:
	main_logger.info("Mode: non-verbose (no prompts)\n")

conf = Config(is_verbose)

# Start log file with current time and config settings
main_logger.info("Current time: {}".format(today_time))
main_logger.info("Current unix time: {}\n".format(today_time_unix))
conf.pprint()

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
		main_logger.info("**************************************")
		main_logger.info("These {} files will be uploaded:".format(len(show_itr)))
		for track in show_itr:
			main_logger.info(track)
		# main_logger.info(*show_itr, sep="\n")
		main_logger.info("**************************************\n")
		return new_itr
	else:
		return None


def upload_new() -> bool:
	"""
	Find and upload new files.
	Cycle through given file extensions and upload the results.

	Returns:
		False if process cancelled. True if process ran fine.
	"""
	# upload_success bool used to determine if safe to reset date ranges
	music_dir = conf.get("dir")
	exts = conf.get("ext")
	for idx, ext in enumerate(exts):
		main_logger.info("({}/{}) Checking for {}'s...".format(idx + 1, len(exts), ext))
		main_logger.info("\tFile search pattern: {}**{}*.{}\n".format(music_dir, os.sep, ext))
		new_file_itr = get_new_files(music_dir, ext)
		# Check if new files were found
		if new_file_itr:
			# Files found, upload
			upload_result = music_manager.upload(new_file_itr, conf)
			if upload_result:
				# Upload succeeded, print out results
				music_manager.parse_result(upload_result, conf)
			else:
				# Upload cancelled
				return False
		else:
			# No new files found
			main_logger.info("\tNo new files found.\n")

	return True


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


def retry_old() -> None:
	"""
	Upload failed songs from last time if there are any.
	"""
	retry_songs = get_failed_uploads()
	if retry_songs:
		main_logger.info("Retrying songs that failed last time...")
		retry_result = music_manager.upload(retry_songs, conf)
		# Remove failed uploads from config
		# Note: if the songs failed again, they will
		#   be re-added in the parse_result() call below
		conf.set("failed_uploads", [])
		if retry_result:
			# Upload not aborted
			music_manager.parse_result(retry_result, conf)


def reset_dates() -> None:
	"""
	Update date range if main upload was not cancelled
		start_date => today
		end_date => remove the bound
		Final range: [today, inf)
	"""
	conf.set("start_date", today_time_unix)
	conf.set("end_date", "")


def main() -> None:
	"""
	Main logic.
	"""
	script_start = time.time()

	success = upload_new()
	retry_old()
	if success:
		reset_dates()

	script_end = time.time()

	total_time = (script_end - script_start)/60
	main_logger.info("Finished.\n\nTotal time: {:.2f} minutes".format(total_time))


if __name__ == '__main__':
	main()
