import json_lines
import json 
import os
import pdb

def read_data(spider_name):
	
	item_list = []
	# Select the last modified record
	# json_files = os.listdir('crawler/agg/json/%s' % folder)
	# time_mod = []
	# for file in json_files:
	# 	time_mod.append(os.path.getmtime('crawler/agg/json/%s/%s' % (folder, file)))
	# # Get indicies of sorting by modification time
	# newest = sorted(range(len(json_files)), key = lambda k: time_mod[k], reverse=True)
	# with open('crawler/agg/json/%s/%s' % (folder, json_files[newest[0]]), 'rb') as f:
	# 	for item in json_lines.reader(f):
	#  		item_list.append(item)
	# f.close()

	with open('crawler/agg/json_out/%s.json' % spider_name, 'rb') as f:
		for item in json_lines.reader(f):
			item_list.append(item)
	f.close()

	return item_list

# Get date modified of latest json file
def date_last_synced():
	json_files = []
	json_files += [each for each in os.listdir('crawler/agg/json_out')
						if each.endswith('.json')]
	time_mod = []
	for file in json_files:
	 	time_mod.append(os.path.getmtime('crawler/agg/json_out/%s/%s' % (folder, file)))
	pdb.set_trace()
	return None