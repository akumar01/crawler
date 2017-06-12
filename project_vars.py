import os

# Add useful paths here
class Paths(object):
	root_path = os.path.dirname(os.path.realpath(__file__))
	ui_path = root_path + '/ui_qt'
	files_path = root_path + '/agg/files/'
	json_path = root_path + '/agg/json'

# Add currently functioning spiders definitions here
class Spiders(object):
	spiders = ['nature_news', 'aps_news', 'science_news', 'washpost']
	# User interface 
	spider_names = ["Nature News and Views", "APS News", "Science News", "The Washington Post"]
	# How many days back into the past can we reliably sync?
	max_range = [30, 30, 10, 2]

# Master list for use in the settings panel of the UI (Kivy version)
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
