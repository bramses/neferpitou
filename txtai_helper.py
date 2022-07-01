from txtai.embeddings import Embeddings
import openai_helper
import json

class EmbeddingsWrapper:
    def __init__(self, transform=openai_helper.transform, content=True, objects=True, DEBUG=False):
        self.embeddings =  Embeddings({ "method": "external", "transform": transform, "content": content, "objects": objects })
        self.debug = DEBUG

    def get_embeddings(self):
        if self.debug:
            print(f"--TXTAI-- getting embeddings")
        return self.embeddings

    def set_transform(self, transform):
        if self.debug:
            print(f"--TXTAI-- setting transform to {transform}")
        self.embeddings.config['transform'] = transform

    def create_index(self, documents):
        if self.debug:
            print(f"--TXTAI-- creating index with {len(documents)} documents")
        return self.embeddings.index([(uid, { "text": val['text'], "filename": val['filename'] }, None) for uid, val in enumerate(documents)])
        
    def search(self, query, n=1):
        if self.debug:
            print(f"--TXTAI-- searching for {query} with {n} results")
        return self.embeddings.search(query, n)

    def save_index(self, path):
        if self.debug:
            print(f"--TXTAI-- saving index to {path}")
        self.embeddings.save(path)
    
    def load_index(self, path):
        if self.debug:
            print(f"--TXTAI-- loading index from {path}")
        self.embeddings.load(path)

    def upsert_index(self, documents):
        if self.debug:
            print(f"--TXTAI-- upserting index with {len(documents)} documents")
        self.embeddings.upsert([(uid, { "text": val['text'], "filename": val['filename'] }, None) for uid, val in enumerate(documents)])

    def delete_ids(self, ids):
        if self.debug:
            print(f"--TXTAI-- deleting ids {ids}")
        self.embeddings.delete(ids)

    def find_ids_by_filename(self, filename):
        if self.debug:
            print(f"--TXTAI-- finding ids by filename {filename}")

        if not self.embeddings.exists('index.txtai'):
            print(f"--TXTAI-- index does not exist")
            return []


        search_results = self.embeddings.search(f"select * from txtai where filename in ('{filename}')")
        print(f"--TXTAI-- search results: {search_results}")

    def exists(self, path):
        if self.debug:
            print(f"--TXTAI-- checking if index exists")
        return self.embeddings.exists(path)

def main():
    data = [{ "text": "US tops 5 million confirmed virus cases", "filename": 'file1' },
         { "text": "Canada's last fully intact ice shelf has suddenly collapsed, forming a Manhattan-sized iceberg", "filename": 'file' },
         { "text": "Beijing mobilises invasion craft along coast as Taiwan tensions escalate", "filename": 'file1' },
         { "text": "The National Park Service warns against sacrificing slower friends in a bear attack", "filename": 'file' },
         { "text": "Maine man wins $10M from $25 lottery ticket", "filename": 'file' },
         { "text": "Make huge profits without work, earn up to $100,000 a day", "filename": 'file' }]
    

    
    embedd = EmbeddingsWrapper(transform=openai_helper.transform, DEBUG=True)
    
    if embedd.exists('index.txtai'):
        embedd.load_index('index.txtai')
    else:
        embedd.create_index(data)
    # embedd.save_index("index.txtai")

    embedd.find_ids_by_filename('file')
    # embedd.set_transform(openai_helper.transform_query)
    # print(embedd.search("select * from txtai where filename in ('file') and similar('Northeast state with lobster') and score >= 0.15"))

def process(data, query, filename, transform=openai_helper.transform):
    embedd = EmbeddingsWrapper(transform=transform)
    embedd.create_index(data)
    embedd.set_transform(openai_helper.transform_query)
    return embedd.search(f"select * from txtai where similar('{query}') and score >= 0.01")


if __name__ == "__main__":
    main()