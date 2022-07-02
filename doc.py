from io_helper import read_text
from txtai_helper import process
from batch import insert_batches
import json
import textwrap


class Document():

    def __init__(self, filename="", chunk_length = 20, DEBUG=False):
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
    doc = Document(filename='./files/daily.md')
    print(doc.txtai_formatted_chunks)

    # content2 = read_text('./files/The lens through which your brain views the world shapes your reality.md')
    # doc2 = Document(filename='The lens through which your brain views the world shapes your reality.md', index_name='index', raw_text=content2)
    # doc2.advanced_chunk(min_chunk_length=2000, max_chunk_length=3000)
    # txtai_fomatted_doc2 = doc2.to_txtai_format()

    # txtai_fomatted = doc.to_txtai_format()
    # joined = txtai_fomatted + txtai_fomatted_doc2
    # qry = 'frozen summer treat'
    # batches = insert_batches('index', records=joined)
    # top_doc = process(list(list(batches)[0]), qry, 'daily.md')[0]

    # top_doc_data = json.loads(top_doc['data'])

    # top_doc_intra = Document(filename=top_doc_data['filename'], index_name='index', raw_text=top_doc_data['text'])
    # top_doc_intra.advanced_chunk(min_chunk_length=20, max_chunk_length=30)

    # top_doc_json = top_doc_intra.to_txtai_format()
    # processed_top_doc = process(top_doc_json, qry, 'daily.md')
    # print(processed_top_doc)


if __name__ == "__main__":
    main()
