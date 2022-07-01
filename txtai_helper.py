from txtai.embeddings import Embeddings
import openai_helper

data = [{ "text": "US tops 5 million confirmed virus cases", "filename": 'file1' },
         { "text": "Canada's last fully intact ice shelf has suddenly collapsed, forming a Manhattan-sized iceberg", "filename": 'file' },
         { "text": "Beijing mobilises invasion craft along coast as Taiwan tensions escalate", "filename": 'file1' },
         { "text": "The National Park Service warns against sacrificing slower friends in a bear attack", "filename": 'file' },
         { "text": "Maine man wins $10M from $25 lottery ticket", "filename": 'file' },
         { "text": "Make huge profits without work, earn up to $100,000 a day", "filename": 'file' }]

class EmbeddingsWrapper:
    def __init__(self, transform):
        if transform is None:
            raise ValueError("transform is required")
        self.embeddings =  Embeddings({"method": "external", "transform": transform, "content": True, "objects": True})

    def get_embeddings(self):
        return self.embeddings

    def set_transform(self, transform):
        self.embeddings.config['transform'] = transform

    def create_index(self, documents):
        self.embeddings.index([(uid, { "text": val['text'], "filename": val['filename'] }, None) for uid, val in enumerate(documents)])
        
    def search(self, query, n=1):
        return self.embeddings.search(query, n)

def main():
    print("Hello World")
    embedd = EmbeddingsWrapper(transform=openai_helper.transform)
    embedd.create_index(data)
    embedd.set_transform(openai_helper.transform_query)
    print(embedd.search("select * from txtai where filename in ('file') and similar('Northeast state with lobster') and score >= 0.15"))

def process(data, query):
    embedd = EmbeddingsWrapper(transform=openai_helper.transform)
    embedd.create_index(data)
    embedd.set_transform(openai_helper.transform_query)
    print(embedd.search(f"select * from txtai where filename in ('file') and similar('{query}') and score >= 0.15"))


if __name__ == "__main__":
    main()