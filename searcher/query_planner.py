from whoosh.qparser import MultifieldParser
from whoosh.query import And, Term

def build_query(ix, raw_query: str, filters: dict):
    parser = MultifieldParser(["name", "description", "category"], schema=ix.schema)
    base_query = parser.parse(raw_query)
    # Apply filters
    filter_queries = []
    if "category" in filters:
        filter_queries.append(Term("category", filters["category"].lower()))
    if "available" in filters:
        val = filters["available"].lower() in ("true", "1", "yes")
        filter_queries.append(Term("available", str(val)))
    if filter_queries:
        return And([base_query] + filter_queries)
    return base_query
