import os
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, KEYWORD, NUMERIC, BOOLEAN
from whoosh.analysis import StemmingAnalyzer

def create_schema():
    return Schema(
        id=ID(stored=True, unique=True),
        name=TEXT(stored=True, analyzer=StemmingAnalyzer()),
        description=TEXT(stored=True, analyzer=StemmingAnalyzer()),
        category=KEYWORD(stored=True, commas=True, lowercase=True),
        available=BOOLEAN(stored=True),
        latitude=NUMERIC(stored=True, decimal_places=6),
        longitude=NUMERIC(stored=True, decimal_places=6)
    )

def ensure_index(index_dir="indexdir"):
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)
    if not index.exists_in(index_dir):
        ix = index.create_in(index_dir, create_schema())
    else:
        ix = index.open_dir(index_dir)
    return ix
