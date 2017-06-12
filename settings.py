import jsonlines
import json
import os
import pdb
from crawler.project_vars import Paths

# Read the settings file in.
def load_settings():
	with jsonlines.open('%s/project_settings.json' % Paths.root_path) as f:
		settings = f.read()
	f.close()
	return settings

# Write settings to file
def save_settings(settings):
	with open('%s/project_settings.json' % Paths.root_path, 'w') as f:
		with jsonlines.Writer(f) as writer:
			writer.write(settings)
		writer.close()
	f.close()
