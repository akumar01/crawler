import json_lines
import json
import os
import pdb

# Read the settings file in.
def load_settings():
	settings = []
	with open('project_settings.json', 'rb') as f:
		for setting in json_lines.reader(f):
			settings.append()
	f.close()
	pdb.set_trace()

# Write settings to file
def save_settings(settings):

	with open('project_settings.')

