from doc import Document
import openai_helper
from txtai_helper import EmbeddingsWrapper
import json
import pprint
from os import listdir
from os.path import isfile, join

pp = pprint.PrettyPrinter(indent=4)
INDEX_NAME = "mdtest.txtai"
UPSERT_TEST = False
DELETE_TEST = False
INSERT_TEST = False
FILES_FETCH_TEST = False
SEARCH_TEST = True

if sum([UPSERT_TEST,DELETE_TEST,INSERT_TEST,FILES_FETCH_TEST, SEARCH_TEST]) > 1:
    raise Exception("Please specify at most one test.")

TOP_DOC_CHUNK_LENGTH = 400
FIRST_PASS_DOC_CHUNK_LENGTH = 7000
PATH = './files/Readwise/Books'

SCORE_THRESHOLD = 0.25
qry = "who posts on the internet the most"

def fetch_files(path):
    '''
    Fetches all files in a directory
    '''
    return [f for f in listdir(path) if isfile(join(path, f))]

def load_index_from_data(data, index_name=INDEX_NAME):
    '''
    Loads an index from a list of documents
    '''
    print("Loading index from data with length: " + str(len(data)))
    embedding_instance = EmbeddingsWrapper(transform=openai_helper.transform, DEBUG=True)
    index = embedding_instance.load_index(index_name)

    if not index:
        embedding_instance.create_index(data)
        embedding_instance.save_index(index_name)
    
    return embedding_instance

def search(query, embedding_instance : EmbeddingsWrapper = None, n=3):
    '''
    Searches for a query and returns the results
    '''

    if not embedding_instance:
        print("Embedding instance not found")
        return False

    print('--TEST-- searching for query: ' + query)
    return embedding_instance.search(f"select * from txtai where similar('{query}') and score >= {SCORE_THRESHOLD}", n=n)

def search_for_ids(ids, embedding_instance: EmbeddingsWrapper = None):
    '''
    Searches for a list of ids and returns the results
    '''

    if not embedding_instance:
        print("Embedding instance not found")
        return False

    print('--TEST-- searching for ids: ' + str(ids))
    return embedding_instance.search(f"select * from txtai where id in ({ids})")


def process_top_documents(top_documents_filenames, query, n=3):
    '''
    Processes the top documents and returns a list of tuples with the filename and the score
    '''

    print(f"Processing top documents: {top_documents_filenames} for query: " + query)

    documents = []
    for filename in top_documents_filenames:
        documents.append(Document(filename=filename, chunk_length=TOP_DOC_CHUNK_LENGTH).txtai_formatted_chunks)

    # pp.pprint(documents)

    for doc in documents:
        single_use_embedding_instance = EmbeddingsWrapper(transform=openai_helper.transform, DEBUG=True)
        single_use_embedding_instance.create_index(doc)
        res = search(query, single_use_embedding_instance, n=n)
        print(f"Search results for query: {res}")
        yield res

def upsert_file(filename, embedding_instance: EmbeddingsWrapper = None, index_name=INDEX_NAME):
    '''
    Upserts a file into the index
    '''

    if not embedding_instance:
        print("Embedding instance not found")
        return False

    doc = Document(filename=filename, chunk_length=FIRST_PASS_DOC_CHUNK_LENGTH)
    ids = embedding_instance.find_ids_by_filename(filename)
    delete_ids([i['id'] for i in ids], index_name=index_name, embedding_instance=embedding_instance)
    upsert(doc.txtai_formatted_chunks, embedding_instance, INDEX_NAME)
 
def upsert(new_data, embedding_instance: EmbeddingsWrapper = None, index_name=INDEX_NAME):
    '''
    Upserts a list of documents into the index
    '''
    print('--TEST-- upserting data')
    if not embedding_instance:
        print("Embedding instance not found")
        return False

    embedding_instance.upsert_index(new_data)
    embedding_instance.save_index(index_name)

def delete_ids (ids, index_name=INDEX_NAME, embedding_instance: EmbeddingsWrapper = None):
    if not embedding_instance:
        print("Embedding instance not found")
        return False

    if len(ids) == 0:
        print("No ids to delete")
        return False
    
    ids = embedding_instance.delete_ids(ids)
    print(f"Deleted ids: {ids}")

    embedding_instance.save_index(index_name)
    return ids


def main(data = []):

    embedding_instance = EmbeddingsWrapper(transform=openai_helper.transform, DEBUG=True)
    index = embedding_instance.load_index(INDEX_NAME)

    if not index and not (INSERT_TEST or FILES_FETCH_TEST):
        print("Index not found -- cannot run tests")
        return False

    if INSERT_TEST:
        doc = Document(filename='./files/daily.md', chunk_length=FIRST_PASS_DOC_CHUNK_LENGTH)
        doc2 = Document(filename='./files/The lens through which your brain views the world shapes your reality.md', chunk_length=FIRST_PASS_DOC_CHUNK_LENGTH)
        joined = doc.txtai_formatted_chunks + doc2.txtai_formatted_chunks

        if not index:
            print(f"Index {INDEX_NAME} not found")
            index = embedding_instance.create_index(joined)
            embedding_instance.save_index(INDEX_NAME)

    if UPSERT_TEST:
        doc3 = Document(filename='./files/daily2.md', chunk_length=FIRST_PASS_DOC_CHUNK_LENGTH)
        upsert(doc3.txtai_formatted_chunks, embedding_instance, INDEX_NAME)
    
    if SEARCH_TEST:
    

        search_res = search(qry, embedding_instance, n=3)

        filenames = set()
        for record in search_res:
            data = json.loads(record['data'])
            filenames.add(data['filename'])
        
        blurbs = process_top_documents(filenames, qry, n=1)
        top_blurbs = []

        for blurb in blurbs:
            for search_result in blurb:
                data = json.loads(search_result['data'])
                top_blurbs.append({ "text": search_result['text'], "filename": data['filename'] })

        print('--TEST RESULT--')
        pp.pprint(top_blurbs)
        # print(f"filenames: {embedding_instance.list_filenames()})")

        print('files stored:' + str(fetch_files(PATH)[0:6]))


    if FILES_FETCH_TEST:
        files = fetch_files(PATH)[0:6]

        if not index:
            print(f"Index {INDEX_NAME} not found")
            # index = embedding_instance.create_index([])
            # embedding_instance.save_index(INDEX_NAME)

        for file in files:
            upsert_file(PATH + '/' + file, embedding_instance)
    

if __name__ == "__main__":
    main()
