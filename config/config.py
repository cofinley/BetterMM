import os
import json
import re
import datetime

current_dir = os.path.dirname(os.path.realpath(__file__))
json_file = "{}{}config.json".format(current_dir, os.sep)
date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
date_format = "%Y-%m-%d"
# TODO insert oauth path (copy from mm.py and alter directory level in string formatting)


class Config:

	def __init__(self):
		self.dir = ""
		self.start_date = ""
		self.ext = ["mp3", "flac"]
		self.unix_time = 0.0
		self.config = {}
		self.load_config()
		self.pprint()


	def pprint(self):
		print("\nConfig:")
		print("\tWorking directory: {}".format(self.dir))
		print("\tStart date: {}".format(self.start_date))
		print("\t\tUnix timestamp: {}".format(self.unix_time))
		print("\tFormats being searched for: {}\n".format(self.ext))


	def update_date(self):

		# Do while until user enters <enter> or appropriate date format
		chosen = False
		while chosen is False:
			choice = input("No start date defined, change? (y/N): ")
			print(choice)
			if choice in ['', 'N', 'n']:
				self.start_date = '1970-01-01'
				chosen = True
			elif choice in ['y', 'Y']:
				while not date_pattern.match(self.start_date):
					input_date = input("Specific date: YYYY-MM-DD: ")
					if date_pattern.match(input_date):
						self.start_date = input_date
						chosen = True

		self.set_var("start_date", self.start_date)


	def get_var(self, var_name, external=None):
		# Use external for project variables not in vars array (project name, version, etc.)
		if external:
			return self.config[var_name]

		return self.config["vars"][var_name]


	def set_var(self, var_name, value):
		self.config["vars"][var_name] = value
		# External project variables changed manually, not here.
		with open(json_file, "w") as output_file:
			json.dump(self.config, output_file)


	def load_config(self):
		if not os.path.isfile(json_file):
			with open(json_file, 'w') as j:
				self.config["vars"] = {}
				json.dump(self.config, j)
				j.close()
			self.dir = input("Full path of music directory: ")
			self.set_var("dir", self.dir)
			self.update_date()
			# TODO insert gmusicapi oauth creation (take from mm.py directly)
			# TODO maybe move this block under the if statement to a function
		else:
			with open(json_file, 'r') as j:
				self.config = json.load(j)
			self.start_date = self.get_var('start_date')
			self.dir = self.get_var('dir')

		self.unix_time = datetime.datetime.strptime(self.start_date, date_format).timestamp()
