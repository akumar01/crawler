import json_lines
def read_data():
	item_list = []
	with open('crawler/agg/json/nature_news/17_Mar_20_19_58', 'rb') as f:
		for item in json_lines.reader(f):
	 		item_list.append(item)
	f.close()
	return item_list