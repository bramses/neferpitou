# nyi

from txtai.embeddings import Embeddings
import openai
from pydantic import BaseModel
from typing import List, Optional

openai.api_key = ""

# Create embeddings index with content enabled. The default behavior is to only store indexed vectors.
embeddings = Embeddings(
    {"path": "sentence-transformers/nli-mpnet-base-v2", "content": True, "objects": True})

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

    def chunk(self):
        """
        Parses a document into chunks no smaller than min_chunk_length
        and no larger than max_chunk_length.
        Attempts to not break sentences or paragraphs.
        """
        self.chunks = self.raw_text.split("\n\n")
        return self

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

    def embed(self):
        '''
        Create embeddings for each chunk
        '''
        embeddings.index([(uid, text, None)
                         for uid, text in enumerate(self.chunks)])
        # Save the index
        embeddings.save(self.index_name)

    def to_json(self):
        return {
            'filename': self.filename,
            'index_name': self.index_name,
            'raw_text': self.raw_text,
            'clean_text': self.clean_text,
            'chunks': self.chunks
        }