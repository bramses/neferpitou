from txtai.embeddings import Embeddings
import openai_helper
import json

class EmbeddingsWrapper:
    def __init__(self, transform=openai_helper.transform, content=True, objects=True, DEBUG=False):
        self.embeddings =  Embeddings({ "method": "external", "transform": transform, "content": content, "objects": objects })
        self.debug = DEBUG
        self.limit = 1000

    def get_embeddings(self):
        if self.debug:
            print(f"--TXTAI-- getting embeddings")
        return self.embeddings

    def set_transform(self, transform):
        if self.debug:
            print(f"--TXTAI-- setting transform to {transform}")
        self.embeddings.config['transform'] = transform

    def create_index(self, documents, tags=None):
        if self.debug:
            print(f"--TXTAI-- creating index with {len(documents)} documents")
        return self.embeddings.index([(uid, { "text": val['text'], "filename": val['filename'] }, tags) for uid, val in enumerate(documents)])
        
    def search(self, query, n=1, transform=openai_helper.transform_query):
        if self.debug:
            print(f"--TXTAI-- searching for {query} with {n} results")

        if transform:
            self.set_transform(transform)

        return self.embeddings.search(query, n)

    def save_index(self, path):
        if self.debug:
            print(f"--TXTAI-- saving index to {path}")
        self.embeddings.save(path)

    def info(self):
        if self.debug:
            print(f"--TXTAI-- getting info")
        return self.embeddings.info()
    
    def load_index(self, path):
        if self.debug:
            print(f"--TXTAI-- loading index from {path}")
        if not self.exists(path):
            return False
        if self.debug:
            print(f"--TXTAI-- index exists")
        self.embeddings.load(path)
        return True

    def upsert_index(self, documents, tags=None, transform=openai_helper.transform):
        if self.debug:
            print(f"--TXTAI-- upserting index with document ids {[doc['indexid'] for doc in documents]}")

        if transform:
            self.set_transform(transform)

        self.embeddings.upsert([(val['indexid'], { "text": val['text'], "filename": val['filename'] }, tags) for uid, val in enumerate(documents)])

    def delete_ids(self, ids):
        if self.debug:
            print(f"--TXTAI-- deleting ids {ids}")
        self.embeddings.delete(ids)

    def find_ids_by_filename(self, filename):
        if self.debug:
            print(f"--TXTAI-- finding ids by filename {filename}")

        search_results = self.embeddings.search(f"select * from txtai where filename in ('{filename}') limit {self.limit}")
        
        if self.debug:
            print(f"--TXTAI-- search results: {search_results}")
            print([result['id'] for result in search_results])

        return search_results

    def exists(self, path):
        if self.debug:
            print(f"--TXTAI-- checking if index exists")
        return self.embeddings.exists(path)

    def update_documents_text(self, documents, new_text):
        if len(documents) != len(new_text):
            raise Exception("Number of documents and new text must be the same")
        updated_documents = []
        if self.debug:
            print(f"--TXTAI-- updating document text")
        
        idx = 0
        for document in documents:
            if self.debug:
                print(f"--TXTAI-- updating document {document['indexid']}")
            data = json.loads(document['data'])
            updated_documents.append({ "indexid": document['indexid'], "text": new_text[idx], "filename": data['filename'] })
            idx += 1

        return updated_documents



def main():
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


def process_top_documents(top_documents, query):
    embedd = EmbeddingsWrapper(transform=openai_helper.transform, DEBUG=True)
    embedd.create_index(top_documents)
    return embedd.search(query)

def process(data, query):
    embedd = EmbeddingsWrapper(transform=openai_helper.transform, DEBUG=True)
    index = embedd.load_index('mdtest.txtai')

    if not index:
        embedd.create_index(data)
        embedd.save_index("mdtest.txtai")
    
    return embedd.search(f"select * from txtai where similar('{query}') and score >= 0.01")


if __name__ == "__main__":
    main()