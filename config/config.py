import os
import json

current_dir = os.path.dirname(os.path.realpath(__file__))
with open(current_dir + "/config.json", 'r') as j:
	config = json.load(j)


def get_var(var_name, external=None):
	# Use external for project variables not in vars array (project name, version, etc.)
	if external:
		return config[var_name]

	return config["vars"][var_name]


def set_var(var_name, value):
	config["vars"][var_name] = value
	# External project variables changed manually, not here.
	with open("config.json", "w") as output_file:
		json.dump(config, output_file)
