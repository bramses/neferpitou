from pydantic import BaseModel
from typing import List, Optional
from io_helper import read_text
from txtai_helper import process
from batch import insert_batches
import json

class Document():

    def __init__(self, filename="", raw_text=""):
       print("Initializing Document object ...")
       print('filename: ' + filename)
       print('raw_text: ' + raw_text)
       self.filename = filename
       self.raw_text = raw_text
       self.advanced_chunk(min_chunk_length=10, max_chunk_length=100)
       self.txtai_formatted_chunks = self.to_txtai_format()
       

    def advanced_chunk(self, min_chunk_length: int, max_chunk_length: int, silent=True):
        """
        Parses a document into chunks no smaller than min_chunk_length
        and no larger than max_chunk_length.
        Attempts to not break sentences or paragraphs.
        Uses raw_text if clean_text is not available.
        """
        chunks = []
        current_chunk = ''

        raw_text = self.raw_text

        for i, char in enumerate(raw_text):
            current_chunk += char
            if len(current_chunk) >= max_chunk_length:
                # if the current chunk is too large,
                # check if the next character is a sentence terminator
                if char in '.!?':
                    # if it is, keep the character in the current chunk
                    chunks.append(current_chunk)
                    if not silent:
                        print("The current chunk:\n" + current_chunk)
                    current_chunk = ''
                else:
                    # otherwise, put the character in the next chunk
                    chunks.append(current_chunk[:-1])
                    if not silent:
                        print("The current chunk:\n" + current_chunk[:-1])
                    current_chunk = char
            # if the current chunk is too small,
            # check if the next character is a space
            elif len(current_chunk) >= min_chunk_length and char == ' ':
                # if it is, keep the character in the current chunk
                chunks.append(current_chunk)
                if not silent:
                    print("The current chunk:\n" + current_chunk)
                current_chunk = ''
        # if there is a leftover chunk, add it to the list of chunks
        if current_chunk:
            chunks.append(current_chunk)
            if not silent:
                print("The current chunk:\n" + current_chunk)
        self.chunks = chunks
        return self

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
    content = read_text('./files/daily.md')
    doc = Document(filename='daily.md', raw_text=content)
    print(doc.to_json())
    # doc.advanced_chunk(min_chunk_length=2000, max_chunk_length=3000)

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