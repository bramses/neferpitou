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
TOP_DOC_CHUNK_LENGTH = 400

SCORE_THRESHOLD = 0.15
qry = "hanoi is the capital of"

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

    doc = Document(filename=filename, chunk_length=7500)
    ids = embedding_instance.find_ids_by_filename(filename)
    deleted = delete_ids([i['id'] for i in ids], index_name=index_name, embedding_instance=embedding_instance)
    print(f"Deleted ids: {deleted}")
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
    
    ids = embedding_instance.delete_ids(ids)
    embedding_instance.save_index(index_name)
    return ids


def main(data = []):

    embedding_instance = EmbeddingsWrapper(transform=openai_helper.transform, DEBUG=True)
    index = embedding_instance.load_index(INDEX_NAME)

    if not index and not INSERT_TEST:
        print("Index not found -- cannot run tests")
        return False

    if INSERT_TEST:
        doc = Document(filename='./files/daily.md', chunk_length=7500)
        doc2 = Document(filename='./files/The lens through which your brain views the world shapes your reality.md', chunk_length=7500)
        joined = doc.txtai_formatted_chunks + doc2.txtai_formatted_chunks

        if not index:
            print(f"Index {INDEX_NAME} not found")
            index = embedding_instance.create_index(joined)
            embedding_instance.save_index(INDEX_NAME)

    if UPSERT_TEST:
        doc3 = Document(filename='./files/daily2.md', chunk_length=7500)
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

    if FILES_FETCH_TEST:
        PATH = './files/Readwise/Tweets'
        files = fetch_files(PATH)[:20]

        for file in files:
            upsert_file(PATH + '/' + file, embedding_instance)
    

if __name__ == "__main__":
    main()


def local_test():
    data = [{ "text": "US tops 5 million confirmed virus cases", "filename": 'file1' },
         { "text": "Canada's last fully intact ice shelf has suddenly collapsed, forming a Manhattan-sized iceberg", "filename": 'file' },
         { "text": "Beijing mobilises invasion craft along coast as Taiwan tensions escalate", "filename": 'file1' },
         { "text": "The National Park Service warns against sacrificing slower friends in a bear attack", "filename": 'file' },
         { "text": "Maine man wins $10M from $25 lottery ticket", "filename": 'file' },
         { "text": "Make huge profits without work, earn up to $100,000 a day", "filename": 'file' }]
    

    
    embedd = EmbeddingsWrapper(transform=openai_helper.transform, DEBUG=True)
    index = embedd.load_index('index.txtai')

    if not index:
        embedd.create_index(data)
        embedd.save_index("index.txtai")

    # embedd.info()

    # ids = embedd.find_ids_by_filename('file')
    # print(f"--TXTAI-- ids: {ids}")
    # embedd.delete_ids([3])
    # embedd.save_index("index.txtai")
    print(embedd.search("select * from txtai where filename in ('file') and similar('savings account') and score >= 0.15"))

    docs_to_update = embedd.search("select * from txtai where id = 1")
    docs_to_update = embedd.update_documents_text(docs_to_update, ['deposit into bank'])

    embedd.upsert_index(docs_to_update)

    
    # print(embedd.search("select * from txtai where filename in ('file') and similar('savings account') and score >= 0.15"))

    all = embedd.search("select * from txtai limit 100")
    [print(f"{doc['id']} {doc['text']}") for doc in all]