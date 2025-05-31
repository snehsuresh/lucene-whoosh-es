import os
from fastapi import FastAPI, Query
from whoosh import index
from whoosh.qparser import MultifieldParser
from query_planner import build_query

app = FastAPI()

# Path to index directory
INDEX_DIR = os.path.abspath(
    os.path.join(os.getcwd(), "../indexdir")
    if os.getcwd().endswith("searcher")
    else "indexdir"
)

# Open index
ix = ix = index.open_dir(os.path.join(os.getcwd(), "../indexer/indexdir"))


@app.get("/search")
def search(q: str = Query(...), category: str = None, available: str = None):
    filters = {}
    if category:
        filters["category"] = category
    if available:
        filters["available"] = available
    qp = build_query(ix, q, filters)
    with ix.searcher() as searcher:
        results = searcher.search(qp, limit=10)
        output = []
        for hit in results:
            output.append(dict(hit))
        return {"results": output}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
