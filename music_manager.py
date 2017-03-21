import os
from gmusicapi import Musicmanager

current_dir = os.path.dirname(os.path.realpath(__file__))
oauth_path = "{}{}{}{}{}".format(current_dir, os.sep, "config", os.sep, "oauth.cred")


def upload(itr):
	mm = Musicmanager()

	if not os.path.isfile(oauth_path):
		# If no oauth file, create one
		open(oauth_path, 'w').close()
		# Create oauth token (will save to file)
		mm.perform_oauth(storage_filepath=oauth_path, open_browser=True)

	is_logged_in = mm.login(oauth_credentials=oauth_path)
	if is_logged_in:
		is_ready = input("\n\nSure you're ready to upload? (y/N): ")
		if is_ready is 'y' or 'Y':
			print("Uploading (may take awhile)...")
			result = mm.upload(itr)

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
