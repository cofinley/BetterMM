import os
from gmusicapi import Musicmanager

from logs.logger import mm_logger

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

		Also returns false if ctrl-c hit during upload process.
	"""
	mm = Musicmanager(debug_logging=False)

	oauth_path = conf.get("oauth_file")
	is_logged_in = mm.login(oauth_credentials=oauth_path)
	if is_logged_in:
		mm_logger.info("Uploading (may take awhile)...")
		mm_logger.info("Hold Ctrl-c to abort.")
		try:
			result = mm.upload(itr)
			mm_logger.info("Done.")
		except KeyboardInterrupt:
			# If user ctrl-c's out (aborts upload), return False
			mm_logger.warning("Upload cancelled.")
			result = False
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

	mm_logger.info("Result:")

	mm_logger.info("\tUploaded:")
	for uploaded in result[0]:
		mm_logger.info("\t\t" + uploaded)

	mm_logger.info("\tMatched:")
	for matched in result[1]:
		mm_logger.info("\t\t" + matched)

	mm_logger.warning("\tNot uploaded:")
	for n_uploaded in result[2]:
		mm_logger.warning("\t\t" + n_uploaded)
		reason = result[2][n_uploaded]
		if "ALREADY_EXISTS" not in reason:
			# Song failed to upload but not because it already existed in google music
			# stage for next upload
			mm_logger.warning("\t\t\tReason: {}".format(reason))
			failed_uploads.append(n_uploaded)
		else:
			mm_logger.warning("\t\t\tReason: Already Exists")

	# Save out failed uploads
	conf.set("failed_uploads", failed_uploads)
