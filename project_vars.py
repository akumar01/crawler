import os

# Add useful paths here
class Paths(object):
	root_path = os.path.dirname(os.path.realpath(__file__))
	ui_path = root_path + '/ui'
	files_path = root_path + '/agg/files/'
	json_path = root_path + '/agg/json'

# Add currently functioning spiders definitions here
class Spiders(object):
	spiders = ['nature_news', 'aps_news', 'science_news']

def settings_master_list():
	settings = {}
	for spider in Spiders.spiders:
		settings[spider] = []
		settings[spider].append('boolean')
		settings[spider].append(1)
	settings['sync_length'] = []
	settings['sync_length'].append('numeric')
	settings['sync_length'].append(30)
	return settings