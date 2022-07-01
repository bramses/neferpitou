import itertools

# https://www.pinecone.io/docs/insert-data/

def chunks(iterable, batch_size=32):
    print("Chunking records into batches of size %s ..." % batch_size)
    """A helper function to break an iterable into chunks of size batch_size."""
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))

def insert_batches(index, records):
    print("Inserting batches of records into index ...")
    # Upsert data with 100 vectors per upsert request
    idx = 0
    for ids_vectors_chunk in chunks(records, batch_size=32):
        print("Inserting batch #%s of records ..." % idx)
        # print(ids_vectors_chunk)
        yield ids_vectors_chunk
        idx += 1