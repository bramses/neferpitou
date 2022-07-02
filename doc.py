from io_helper import read_text
from txtai_helper import process, process_top_documents
from batch import insert_batches
import json
import textwrap


class Document():

    def __init__(self, filename="", chunk_length = 7500, DEBUG=False):
        print("Initializing Document object ...")
        if filename == "":
            raise Exception("Filename is required")

        self.filename = filename
        file_content = read_text(filename)
        self.raw_text = file_content
        self.chunks = self.wrap(file_content, chunk_length).split('\n')
        self.txtai_formatted_chunks = self.to_txtai_format()

    def wrap(self, s, w):
        return textwrap.fill(s, w)

    def to_json(self):
        return {
            'filename': self.filename,
            'raw_text': self.raw_text,
            'chunks': self.chunks,
            'chunks_length': len(self.chunks)
        }

    def to_txtai_format(self):
        txtai_formatted = []
        for chunk in self.chunks:
            txtai_formatted.append({
                'text': chunk,
                'filename': self.filename
            })
        return txtai_formatted


def main():
    doc = Document(filename='./files/daily.md', chunk_length=7500)
    doc2 = Document(filename='./files/The lens through which your brain views the world shapes your reality.md', chunk_length=7500)
    joined = doc.txtai_formatted_chunks + doc2.txtai_formatted_chunks
    
    qry = 'who was the scientist from world war ii'
    batches = insert_batches('index', records=joined)
    
    top_doc = process(list(list(batches)[0]), qry)

    top_doc_data = json.loads(top_doc[0]['data'])
    top_doc_intra = Document(filename=top_doc_data['filename'], chunk_length=400)

    processed_top_doc = process_top_documents(top_doc_intra.txtai_formatted_chunks, qry)
    print(processed_top_doc)


if __name__ == "__main__":
    main()
