import os
import glob
import datetime

import music_manager
from config import config
conf = config.Config()


def check_date(f):
	return os.path.getctime(f) >= conf.unix_time


def get_new_files():
	# Go through listings for each type of extension
	for idx, ext in enumerate(conf.ext):

		print("({}/{}) Checking for {}'s...".format(idx, len(ext), ext))
		print("\tPattern: {}**{}*.{}\n".format(conf.dir, os.sep, ext))
		# recursive argument only appears in python 3.5+
		files = glob.iglob("{}**{}*.{}".format(conf.dir, os.sep, ext), recursive=True)

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

if __name__ == '__main__':
	# Find newer files and upload them

	# TODO maybe iterate of ext here and have the function return so it can be passed to upload()
	# 	would be more functional that way instead of nesting upload function inside the first function
	get_new_files()

	# Update conf's start date to today
	today = datetime.datetime.today().strftime("%Y-%m-%d")
	conf.set_var("start_date", today)

