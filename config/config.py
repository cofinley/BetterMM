import os
import json
import re
import datetime

from logs.logger import config_logger

from gmusicapi import Musicmanager
mm = Musicmanager(debug_logging=False)

current_dir = os.path.dirname(os.path.realpath(__file__))

json_file = "{}{}{}".format(current_dir, os.sep, "config.json")
oauth_file = "{}{}{}".format(current_dir, os.sep, "oauth.cred")

date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
date_format = "%Y-%m-%d"


class Config:
	"""
	Configuration class that gets/sets variables used throughout the utility.
	"""
	def __init__(self, verbose=False):

		self.verbose = verbose

		self.config = {}
		self.start_unix_time = 0.0
		self.end_unix_time = 0.0

		self.load_config()
		self.check_oauth()
		self.init_unix_timestamps()


	def get(self, var_name: str) -> object:

		return self.config[var_name]


	def set(self, var_name: str, value: object) -> None:

		self.config[var_name] = value

		with open(json_file, "w") as output_file:
			json.dump(self.config, output_file)


	def load_config(self):
		"""
		Load json config into memory if the file exists. If not, create one.
		"""
		# Check if config file exists
		if not os.path.isfile(json_file):
			# No config file, create new config and populate with parameters
			self.create_config()

		else:
			# Config exists, load config json into memory
			with open(json_file, 'r') as j:
				self.config = json.load(j)

		if self.verbose:
			self.create_date_ranges()


	"""Application-specific section"""


	def create_config(self):
		"""
		Generate new config file. Input music directory and date ranges.
		"""
		self.config = {
				"ext": ["mp3", "flac"],
				"dir": "",
				"start_date": "",
				"end_date": "",
				"failed_uploads": []
		}

		with open(json_file, 'w') as j:
			json.dump(self.config, j)

		# Define and save dir & date range
		self.set("dir", input("Full path of music directory: "))
		self.prompt_date_ranges()


	def check_oauth(self):
		"""
		Create oauth credentials file if it doesn't exist.
		"""
		if not os.path.isfile(oauth_file):
			self.create_oauth_token()
		else:
			# Oauth file exists, make sure oauth path in config file
			self.set("oauth_file", oauth_file)


	def create_oauth_token(self):
		"""
		Generate oauth token from signing into Google in the browser.
		"""
		# If no oauth file, create one
		open(oauth_file, 'w').close()

		# Create oauth token (will save to file)
		mm.perform_oauth(storage_filepath=oauth_file, open_browser=True)
		mm.logout()

		self.set("oauth_file", oauth_file)


	def prompt_date_ranges(self):
		"""
		Prompt user for date ranges of music files to be added. Saves to config json.
		"""
		# Do while until user enters <enter> or appropriate date format
		chosen = False
		while chosen is False:
			choice = input("No date range defined, change? (y/N): ")

			if choice in ['', 'N', 'n']:
				# No preference for dates, include all
				self.set("start_date", "1970-01-01")
				today = datetime.datetime.today().strftime("%Y-%m-%d")
				self.set("end_date", today)
				chosen = True

			elif choice in ['y', 'Y']:
				self.create_date_ranges()
				chosen = True


	def create_date_ranges(self):
		"""
		Define start and end dates to look for music files (based on creation/copy time).
		Called when config first created or scipt called with verbose arguments (-v, --verbose)
		"""
		range_choice = ""
		while range_choice not in ["1", "2", "3"]:
			range_choice = input("(1) Just start date?\n(2) Just end date?\n(3) Both?\nEnter number here: ")
		range_choice_idx = int(range_choice) - 1

		# Translate choice to index of list of choices
		# Indicies match with numbers in the question
		date_range_choices = [["start_date"], ["end_date"], ["start_date", "end_date"]]
		date_range_chosen = date_range_choices[range_choice_idx]

		# Go through each key and validate date format inputted by user
		for key in date_range_chosen:
			input_date = ""
			while not date_pattern.match(input_date):
				input_date = input("{}: YYYY-MM-DD: ".format(key.replace("_", " ").title()))
				if date_pattern.match(input_date):
					self.set(key, input_date)

		config_logger.info("The date range will be reset after the uploading finishes.")
		config_logger.info("If you would like custom date ranges next time, run the script with the '-v' or '--verbose' argument\n")


	def pprint(self):
		"""
		Pretty print config variables.
		"""
		config_logger.info("Config:")
		config_logger.info("\tWorking directory: {}".format(self.get("dir")))
		start_date = self.get("start_date")
		if type(start_date) is int:
			start_date = datetime.datetime.fromtimestamp(start_date).strftime("%Y-%m-%d %I:%M %p")
			config_logger.info("\tStart date: {}".format(start_date))
		else:
			config_logger.info("\tStart date: {}".format(self.get("start_date")))
		config_logger.info("\t\tUnix timestamp: {}".format(self.start_unix_time))
		config_logger.info("\tEnd date: {}".format(self.get("end_date")))
		config_logger.info("\t\tUnix timestamp: {}".format(self.end_unix_time))
		config_logger.info("\tFormats being searched for: {}\n".format(self.get("ext")))


	def init_unix_timestamps(self):
		"""
		Get Unix timestamps for date ranges if they exist, otherwise set to None.
		"""
		start = self.get("start_date")
		if type(start) is int:
			# Last session reset start_date to a full unix timestamp, not just date
			self.start_unix_time = start
		else:
			# Start date just a date in YYYY-MM-DD format
			self.start_unix_time = self.to_timestamp(start) if start else None

		end = self.get("end_date")
		self.end_unix_time = self.to_timestamp(end) if end else None


	@staticmethod
	def to_timestamp(date: str) -> float:
		"""
		Convert YYYY-MM-DD to Unix timestamp.
		"""
		timestamp = datetime.datetime.strptime(date, date_format).timestamp()
		return timestamp


	@staticmethod
	def from_timestamp(timestamp) -> str:
		"""
		Convert from Unix timestamp to YYYY-MM-DD.
		"""
		str_date = datetime.datetime.fromtimestamp(float(timestamp)).strftime("%Y-%m-%d")
		return str_date
