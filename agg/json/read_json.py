import json_lines
import json 
import os

def read_data(folder):
	item_list = []
	# Select the last modified record
	json_files = os.listdir('crawler/agg/json/%s' % folder)
	time_mod = []
	for file in json_files:
		time_mod.append(os.path.getmtime('crawler/agg/json/%s/%s' % (folder, file)))
	# Get indicies of sorting by modification time
	newest = sorted(range(len(json_files)), key = lambda k: time_mod[k], reverse=True)
	with open('crawler/agg/json/%s/%s' % (folder, json_files[newest[0]]), 'rb') as f:
		for item in json_lines.reader(f):
	 		item_list.append(item)
	f.close()
	return item_list

# 
def get_update_log():
	with open('last_update.json') as f:
		return json.load(f)
