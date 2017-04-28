import tika
tika.initVM()
from tika import parser
parsed = parser.from_file('/path/to/file')
print(parsed["metadata"])
print(parsed["content"])