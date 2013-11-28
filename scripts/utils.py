import os
import csv
import sys
import pymongo
from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

#Project specific directories
scripts_dir = os.getcwd()
base_dir = os.path.dirname(scripts_dir)
data_dir = os.path.abspath(os.path.join(base_dir, 'data'))
nga_data_dir = os.path.abspath(os.path.join(data_dir, 'nga'))
getty_data_dir = os.path.abspath(os.path.join(data_dir, 'getty'))
refine_dir = os.path.abspath(os.path.join(data_dir, 'refine'))
provenance_dir = os.path.abspath(os.path.join(data_dir, 'provenance'))

#Project specific files
getty_reconciled_artists = os.path.abspath(os.path.join(refine_dir,
                                           'getty-artists-dbpedia.csv'))
nga_reconciled_artists = os.path.abspath(os.path.join(refine_dir,
                                         'nga-artists-dbpedia.csv'))
nga_artists_json = os.path.abspath(os.path.join(nga_data_dir,
                                   'artists.json'))


def get_dirs():
    dir_map = {}
    dir_map["base"] = base_dir
    dir_map["scripts"] = scripts_dir
    dir_map["data"] = data_dir
    dir_map["data-refine"] = refine_dir
    dir_map["data-nga"] = nga_data_dir
    dir_map["data-getty"] = getty_data_dir
    dir_map["data-provenance"] = provenance_dir
    return dir_map


def get_files():
    file_map = {}
    file_map["nga-artists"] = nga_artists_json
    file_map["nga-artists-dbpedia"] = nga_reconciled_artists
    file_map["getty-artists-dbpedia"] = getty_reconciled_artists
    return file_map


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
        try:
            sparql.setQuery(
                """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT ?label
                WHERE {
                { <""" + artist + """> dbpprop:birthDate ?label }
                UNION
                { <""" + artist + """> dbpedia-owl:birthDate ?label }
                UNION
                { <""" + artist + """> dbpprop:dateOfBirth ?label }
                }
                """
            )
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            for result in results["results"]["bindings"]:
                return result["label"]["value"]
        except Exception:
            print "Sparql query error!"
            sys.exit(1)

    elif prop == "death date":
        sparql_type = "dbpprop:deathDate"
        try:
            sparql.setQuery(
                """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT ?label
                WHERE {
                { <""" + artist + """> dbpprop:deathDate ?label }
                UNION
                { <""" + artist + """> dbpedia-owl:deathDate ?label }
                UNION
                { <""" + artist + """> dbpprop:dateOfDeath ?label }
                }
                """
            )
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()

            for result in results["results"]["bindings"]:
                return result["label"]["value"]
        except Exception:
            print "Sparql query error!"
            sys.exit(1)

    try:
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
    except Exception:
        print "Sparql query error!"
        sys.exit(1)

