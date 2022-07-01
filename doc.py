from pydantic import BaseModel
from typing import List, Optional
from io_helper import read_text
from txtai_helper import process
from batch import insert_batches

class Document(BaseModel):
    filename: str
    index_name: str
    raw_text: str
    clean_text: Optional[str] = None
    chunks: Optional[List[str]] = None

    def clean(self):
        pass
        # self.clean_text = run_all(text=self.raw_text)
        # return self

    def advanced_chunk(self, min_chunk_length: int, max_chunk_length: int, silent=True):
        """
        Parses a document into chunks no smaller than min_chunk_length
        and no larger than max_chunk_length.
        Attempts to not break sentences or paragraphs.
        Uses raw_text if clean_text is not available.
        """
        chunks = []
        current_chunk = ''

        raw_text = None
        if self.clean_text is None:
            raw_text = self.raw_text
        else:
            print('text is clean, using clean text')
            raw_text = self.clean_text

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

    def test_chunk(self, size: int, min_chunk_length: int, max_chunk_length: int):
        '''
        Tests the chunking algorithm on a document of a given size.
        size: the number of characters in the scope of the test
        min_chunk_length: the minimum length of a chunk
        max_chunk_length: the maximum length of a chunk
        '''
        self.clean_text = self.clean_text[:size]
        self.advanced_chunk(min_chunk_length, max_chunk_length, False)

        return self

    def to_json(self):
        return {
            'filename': self.filename,
            'index_name': self.index_name,
            'raw_text': self.raw_text,
            'clean_text': self.clean_text,
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
    # print(content)

    doc = Document(filename='daily.md', index_name='index', raw_text=content)
    doc.advanced_chunk(min_chunk_length=20, max_chunk_length=30)
    # print(doc.to_json())
    txtai_fomatted = doc.to_txtai_format()
    batches = insert_batches('index', records=txtai_fomatted)
    # print(list(list(batches)[0]))
    # process(doc.to_txtai_format(), 'scoop', 'daily.md')
    process(list(list(batches)[0]), 'latitude', 'daily.md')

if __name__ == "__main__":
    main()