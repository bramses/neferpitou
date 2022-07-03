from io_helper import read_text
import textwrap
from uuid import uuid4


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
        self.uuid = str(uuid4())

    def wrap(self, s, w):
        return textwrap.fill(s, w)

    def to_json(self):
        return {
            'filename': self.filename,
            'raw_text': self.raw_text,
            'chunks': self.chunks,
            'chunks_length': len(self.chunks),
            'uuid': self.uuid
        }

    def to_txtai_format(self):
        txtai_formatted = []
        for chunk in self.chunks:
            txtai_formatted.append({
                'text': chunk,
                'filename': self.filename,
                'chunk_uuid': str(uuid4())
            })
        return txtai_formatted