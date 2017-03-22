import os
from gmusicapi import Musicmanager

from config.config import Config
conf = Config()

current_dir = os.path.dirname(os.path.realpath(__file__))
oauth_path = conf.get("oauth_file")


def upload(itr: iter) -> tuple:
	"""
	Takes iterable of music files and uploads all files to Google Music in 320 kbps mp3

	Args:
		itr: iterable of absolute file paths to songs of a single extension (mp3 or flac, etc.)

	Returns:
		result: tuple of three dictionaries
			(
				{'<filepath>': '<new server id>'},               # uploaded
				{'<filepath>': '<new server id>'},               # matched
				{'<filepath>': '<reason, eg ALREADY_EXISTS>'}    # not uploaded
			)
	"""
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
		print("Done!")
		mm.logout()
		return result


def parse_result(result: tuple) -> None:
	"""
	Takes readout from upload payload and parses what was uploaded, matched, and not uploaded

	Args:
		result: tuple of three dictionaries (see upload function docstring for details)
	"""
	future_uploads = list(conf.get("future_uploads"))
	print("Parsing readout...")
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
		print("\t\tReason: {}".format(reason))
		if "ALREADY_EXISTS" not in reason:
			# Song failed to upload but not because it already existed in google music
			# stage for next upload
			future_uploads.append(n_uploaded)

	# Save out future uploads
	conf.set("future_uploads", future_uploads)

