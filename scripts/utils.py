import csv
import pymongo
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

def get_popular_search_keywords_from_db():
    pass


def get_all_search_keywords_from_db():
    pass


def set_popular_search_keywords_to_db():
    pass


def set_all_search_keywords_to_db():
    pass


def is_csv(filename, fields):
    with open(filename, 'rb') as csvfile:
        try:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                first_line = row
                try:
                    elements = first_line[0].strip().split(',')
                except Exception, IndexError:
                    raise csv.Error
                for element in elements:
                    if element not in fields:
                        raise csv.Error
                break
            csvfile.seek(0)
        except csv.Error:
            print "not a csv file, skipping", filename
            return False
    csvfile.close()
    return True


def compute_popular_searches(new_keyword):
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
        current_top_n = {k: v for k, v in current_top_n.items()
                         if v in current_top_n_values}

    set_popular_search_keywords_to_db()
    set_all_search_keywords_to_db()


def query_sparql(artist, prop):
    if prop == "short description":
        sparql_type = "dc:description"
    elif prop == "long description":
        sparql_type = "dbpprop:caption"
    elif prop == "movement":
        sparql_type = "dbpprop:movement"
    elif prop == "birth date":
        sparql_type = "dbpprop:birthDate"
    elif prop == "death date":
        sparql_type = "dbpprop:deathDate"

    sparql.setQuery(
        """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?label
        WHERE { <""" + artist + """>""" + sparql_type + """?label }
        """
    )
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for result in results["results"]["bindings"]:
        return result["label"]["value"]
