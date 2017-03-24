import os
from gmusicapi import Musicmanager

current_dir = os.path.dirname(os.path.realpath(__file__))


def upload(itr: iter, conf: object) -> tuple:
	"""
	Takes iterable of music files and uploads all files to Google Music in 320 kbps mp3

	Args:
		itr: iterable of absolute file paths to songs of a single extension (mp3 or flac, etc.)
		conf: config object from run.py

	Returns:
		result: tuple of three dictionaries
			(
				{'<filepath>': '<new server id>'},               # uploaded
				{'<filepath>': '<new server id>'},               # matched
				{'<filepath>': '<reason, eg ALREADY_EXISTS>'}    # not uploaded
			)
	"""
	mm = Musicmanager(debug_logging=False)

	oauth_path = conf.get("oauth_file")
	is_logged_in = mm.login(oauth_credentials=oauth_path)
	if is_logged_in:
		print("Uploading (may take awhile)...")
		result = mm.upload(itr)
		print("Done.")
		mm.logout()
		return result


def parse_result(result: tuple, conf: object) -> None:
	"""
	Takes readout from upload payload and parses what was uploaded, matched, and not uploaded

	Args:
		result: tuple of three dictionaries (see upload function docstring for details)
		conf: config object from run.py
	"""
	failed_uploads = list(conf.get("failed_uploads"))
	print("Result:")
	print("\n\tUploaded:")
	for uploaded in result[0]:
		print("\t\t" + uploaded)
	print("\n\tMatched:")
	for matched in result[1]:
		print("\t\t" + matched)
	print("\n\tNot uploaded:")
	for n_uploaded in result[2]:
		print("\t\t" + n_uploaded)
		reason = result[2][n_uploaded]
		if "ALREADY_EXISTS" not in reason:
			# Song failed to upload but not because it already existed in google music
			# stage for next upload
			print("\t\t\tReason: {}".format(reason))
			failed_uploads.append(n_uploaded)
		else:
			print("\t\t\tReason: Already Exists")

	# Save out failed uploads
	conf.set("failed_uploads", failed_uploads)


def process(itr: iter, conf: object):
	"""
	Run the functions that upload the files in the iterator and pretty print the results.

	Args:
		itr: file iterator of song file paths
		conf: config object from run.py
	Returns:
		False if upload aborted.
	"""
	readout = upload(itr, conf)
	if readout:
		parse_result(readout, conf)
		return True
	else:
		print("Upload cancelled.")
		return False
