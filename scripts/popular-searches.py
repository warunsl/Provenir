import pymongo

def get_popular_search_keywords_from_db():
	pass


def get_all_search_keywords_from_db():
	pass


def set_popular_search_keywords_to_db():
	pass


def set_all_search_keywords_to_db():
	pass


def get_popular_searches(new_keyword):
	current_top_n = get_popular_search_keywords_from_db()
	current_all_searches = get_all_search_keywords_from_db()
	new_keyword_count = 0

	try:
		current_all_searches[new_keyword] += 1
	except KeyError:
		current_all_searches[new_keyword] = 1
	new_keyword_count = current_all_searches[new_keyword]

	current_top_n_values = current_top_n.values()


	if new_keyword_count > min(current_top_n_values):
		current_top_n_values.append(new_keyword_count)
		current_top_n_values = current_top_n_values[:5]
		current_top_n[new_keyword] = new_keyword_count
		current_top_n = {k:v for k,v in current_top_n.items() if v in current_top_n_values}

	set_popular_search_keywords_to_db()
	set_all_search_keywords_to_db()