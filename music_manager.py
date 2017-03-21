import os
from gmusicapi import Musicmanager

from config.config import Config
conf = Config()

current_dir = os.path.dirname(os.path.realpath(__file__))
oauth_path = conf.get("oauth_file")


def upload(itr):
	mm = Musicmanager()

	is_logged_in = mm.login(oauth_credentials=oauth_path)
	if is_logged_in:
		# TODO only prompt if script not launched with verbose argument
		# is_ready = input("\n\nSure you're ready to upload? (y/N): ")
		# if is_ready is 'y' or 'Y':
		print("Uploading (may take awhile)...")
		# TODO catch UnicodeEncodeError somehow
		# 	It's happening in gmusicapi with Japanese and full width chars in music file paths
		result = mm.upload(itr)
		mm.logout()

		print("Done!")
		print("Uploaded:")
		for uploaded in result[0]:
			print("\t" + uploaded)
		print("Matched:")
		for matched in result[1]:
			print("\t" + matched)
		print("Not uploaded:")
		for n_uploaded in result[2]:
			print("\t" + n_uploaded)
			reason = result[2][n_uploaded]
			if "ALREADY_EXISTS" not in reason:
				# Song failed to upload but not because it already existed in google music
				# stage for next upload
				# TODO if any not uploaded not because it already exists, stage for next time
				pass
			print("\t\tReason: {}".format(reason))

