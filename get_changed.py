import os
import glob

from config import config
conf = config.Config()


def check_date(f):
	return os.path.getctime(f) >= conf.unix_time


def get_new_files():
	# Go through listings for each type of extension
	for ext in conf.ext:

		print("Checking for {}'s...".format(ext))
		print("\tPattern: {}**{}*.{}\n".format(conf.dir, os.sep, ext))
		# recursive argument only appears in python 3.5+
		files = glob.iglob("{}**{}*.{}".format(conf.dir, os.sep, ext), recursive=True)

		new_files = filter(check_date, files)

		upload(new_files)


def upload(itr):
	# TODO gmusicapi code here
	# TODO update start_date in config to today's date after upload
	for i in itr:
		print(i)

newer_files_itr = get_new_files()
