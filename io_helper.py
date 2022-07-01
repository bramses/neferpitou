# read text from file
def read_text(file_path):
    with open(file_path, 'r') as f:
        return f.read()
