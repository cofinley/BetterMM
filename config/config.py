import os
import json
import re
import datetime

from gmusicapi import Musicmanager
mm = Musicmanager()

current_dir = os.path.dirname(os.path.realpath(__file__))

json_file = "{}{}{}".format(current_dir, os.sep, "config.json")
oauth_file = "{}{}{}".format(current_dir, os.sep, "oauth.cred")

date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
date_format = "%Y-%m-%d"


class Config:

	def __init__(self):

		self.config = {}
		self.start_unix_time = 0.0
		self.end_unix_time = 0.0
		self.load_config()
		self.pprint()


	def get(self, var_name: str) -> str:
		"""
		Get config setting from memory.

		Args:
			var_name: string of key to get from config

		Returns:
			string of value of key from config
		"""

		return self.config[var_name]


	def set(self, var_name, value):
		"""
		Save new value to key in config in memory and json file.

		Args:
			var_name: string of config key
			value: string of new value
		"""

		self.config[var_name] = value

		with open(json_file, "w") as output_file:
			json.dump(self.config, output_file)


	def load_config(self):
		"""
		Load json config into memory if the file exists. If not, create one.

		Check for Google Oauth too.
		Bring human-readable date ranges from config into class member variable as Unix timestamps.
		Void any date endpoints not used.
		"""

		# Check if config file exists
		if not os.path.isfile(json_file):
			# No config file, create one and populate with parameters
			self.create_config()

		else:
			# Config exists, load into memory
			with open(json_file, 'r') as j:
				self.config = json.load(j)

		# Create oauth credentials file if it doesn't exist
		if not os.path.isfile(oauth_file):
			self.create_oauth_token()

		# Get Unix timestamps for date ranges if they exist, otherwise set to None
		if self.get("start_date") is not "":
			self.start_unix_time = self.to_timestamp(self.get("start_date"))
		else:
			self.start_unix_time = None

		if self.get("end_date") is not "":
			self.end_unix_time = self.to_timestamp(self.get("end_date"))
		else:
			self.end_unix_time = None


	def create_config(self):
		"""
		Generate new config file. Input music directory and date ranges.
		"""

		config_dict = {
				"ext": ["mp3", "flac"],
				"dir": "",
				"start_date": "",
				"end_date": ""
		}
		with open(json_file, 'w') as j:
			json.dump(config_dict, j)

		# Define and save dir & date range
		self.set("dir", input("Full path of music directory: "))
		self.create_date_ranges()


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


	def create_date_ranges(self):

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
				# Prompt for start and/or end dates
				range_choice = ""
				while range_choice not in ["0", "1", "2"]:
					range_choice = input("(0) Just start date?\n(1) Just end date?\n(2) Both?\nEnter number here: ")
				range_choice_idx = int(range_choice)

				# Translate choice to index of list of choices
				# Indicies match with numbers in the question
				date_range_choices = [["start_date"], ["end_date"], ["start_date", "end_date"]]
				date_range_chosen = date_range_choices[range_choice_idx]

				# Go through each key and validate date format inputted by user
				for key in date_range_chosen:
					while not date_pattern.match(self.get(key)):
						input_date = input("Specific date: YYYY-MM-DD: ")
						if date_pattern.match(input_date):
							self.set(key, input_date)
							chosen = True


	def pprint(self):

		"""
		Pretty print config.
		"""
		print("\nConfig:")
		print("\tWorking directory: {}".format(self.get("dir")))
		print("\tStart date: {}".format(self.get("start_date")))
		print("\t\tUnix timestamp: {}".format(self.start_unix_time))
		print("\tEnd date: {}".format(self.get("end_date")))
		print("\t\tUnix timestamp: {}".format(self.end_unix_time))
		print("\tFormats being searched for: {}\n".format(self.get("ext")))


	def to_timestamp(self, date: str) -> float:
		"""
		Convert YYYY-MM-DD to Unix timestamp.

		Args:
			date: string in format of YYYY-MM-DD

		Returns:
			timestamp: Unix timestamp float
		"""
		timestamp = datetime.datetime.strptime(date, date_format).timestamp()
		return timestamp


	def from_timestamp(self, timestamp) -> str:
		"""
		Convert from Unix timestamp to YYYY-MM-DD.
		Args:
			timestamp: float or string of float of Unix timestamp

		Returns:
			str_date: string in date format of YYYY-MM-DD
		"""
		str_date = datetime.datetime.fromtimestamp(float(timestamp)).strftime("%Y-%m-%d")
		return str_date
