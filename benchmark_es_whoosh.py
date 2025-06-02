# benchmark_es_whoosh.py

import os
import time
import random
import json
import shutil
import pandas as pd
import matplotlib.pyplot as plt
from elasticsearch import Elasticsearch, helpers
from whoosh import index as whoosh_index
from whoosh.fields import Schema, TEXT, ID, BOOLEAN
from whoosh.qparser import QueryParser

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
NUM_DOCS = 5000  # Number of synthetic documents
DOC_WORD_COUNT = 50  # Words per document
NUM_QUERIES = 100  # Number of random queries to run
ELASTIC_INDEX = "benchmark_docs"  # Elasticsearch index name
WHOOSH_INDEX = "whoosh_index"  # Folder for Whoosh index
VOCAB = [
    "pizza",
    "burger",
    "sushi",
    "taco",
    "pasta",
    "salad",
    "sandwich",
    "steak",
    "noodle",
    "curry",
]

# ─── 1. GENERATE SYNTHETIC DOCUMENTS ─────────────────────────────────────────
docs = []
for i in range(NUM_DOCS):
    content = " ".join(random.choices(VOCAB, k=DOC_WORD_COUNT))
    docs.append(
        {
            "id": f"doc_{i}",
            "name": f"Item {i}",
            "category": random.choice(["food", "beverage", "snack"]),
            "available": random.choice([True, False]),
            "content": content,
        }
    )

# Save docs_data.json for reference or other benchmarks (e.g. Java)
with open("docs_data.json", "w") as f:
    json.dump(docs, f, indent=2)

# ─── 2. INDEX TO ELASTICSEARCH ───────────────────────────────────────────────
es = Elasticsearch("http://localhost:9200")
if es.indices.exists(index=ELASTIC_INDEX):
    es.indices.delete(index=ELASTIC_INDEX)

mapping = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "name": {"type": "text"},
            "category": {"type": "keyword"},
            "available": {"type": "boolean"},
            "content": {"type": "text"},
        }
    }
}
es.indices.create(index=ELASTIC_INDEX, body=mapping)


def _es_actions(doc_list):
    for d in doc_list:
        yield {"_index": ELASTIC_INDEX, "_id": d["id"], "_source": d}


start = time.perf_counter()
helpers.bulk(es, _es_actions(docs))
es.indices.refresh(index=ELASTIC_INDEX)
elapsed_es_index = time.perf_counter() - start

# ─── 3. INDEX TO WHOOSH ──────────────────────────────────────────────────────
if os.path.exists(WHOOSH_INDEX):
    shutil.rmtree(WHOOSH_INDEX)
os.makedirs(WHOOSH_INDEX, exist_ok=True)

whoosh_schema = Schema(
    id=ID(stored=True, unique=True),
    name=TEXT(stored=True),
    category=TEXT(stored=True),
    available=BOOLEAN(stored=True),
    content=TEXT(stored=True),
)

ix = whoosh_index.create_in(WHOOSH_INDEX, whoosh_schema)
writer = ix.writer()

start = time.perf_counter()
for d in docs:
    writer.add_document(
        id=d["id"],
        name=d["name"],
        category=d["category"],
        available=d["available"],
        content=d["content"],
    )
writer.commit()
elapsed_whoosh_index = time.perf_counter() - start


# ─── 4. SEARCH FUNCTIONS ──────────────────────────────────────────────────────
def es_search(term: str):
    body = {"query": {"match": {"content": {"query": term}}}}
    resp = es.search(index=ELASTIC_INDEX, body=body, size=NUM_DOCS)
    return resp["hits"]["hits"]


def whoosh_search(term: str):
    qp = QueryParser("content", ix.schema)
    parsed = qp.parse(term)
    with ix.searcher() as searcher:
        results = searcher.search(parsed, limit=None)
        return [dict(hit) for hit in results]


# ─── 5. BENCHMARK QUERIES (ES vs Whoosh) ───────────────────────────────────────
queries = random.choices(VOCAB, k=NUM_QUERIES)
bench_data = []
for term in queries:
    t0 = time.perf_counter()
    es_hits = es_search(term)
    t1 = time.perf_counter()

    t2 = time.perf_counter()
    whoosh_hits = whoosh_search(term)
    t3 = time.perf_counter()

    bench_data.append(
        {
            "query": term,
            "es_time_ms": (t1 - t0) * 1000,
            "whoosh_time_ms": (t3 - t2) * 1000,
            "es_hits": len(es_hits),
            "whoosh_hits": len(whoosh_hits),
        }
    )

df_bench = pd.DataFrame(bench_data)

# ─── 6. SUMMARY & VISUALIZATION ───────────────────────────────────────────────
summary = pd.DataFrame(
    {
        "Elasticsearch (ms)": {
            "mean": df_bench["es_time_ms"].mean(),
            "median": df_bench["es_time_ms"].median(),
            "p90": df_bench["es_time_ms"].quantile(0.90),
            "p99": df_bench["es_time_ms"].quantile(0.99),
        },
        "Whoosh (ms)": {
            "mean": df_bench["whoosh_time_ms"].mean(),
            "median": df_bench["whoosh_time_ms"].median(),
            "p90": df_bench["whoosh_time_ms"].quantile(0.90),
            "p99": df_bench["whoosh_time_ms"].quantile(0.99),
        },
    }
)

# Display DataFrames
print("\n--- Raw Benchmark Results (first 10 queries) ---")
print(df_bench.head(10))
print("\n--- Summary Statistics (ms) ---")
print(summary)

# A) Average query latency
plt.figure(figsize=(8, 5))
plt.bar(
    ["Elasticsearch", "Whoosh"],
    [df_bench["es_time_ms"].mean(), df_bench["whoosh_time_ms"].mean()],
    yerr=[df_bench["es_time_ms"].std(), df_bench["whoosh_time_ms"].std()],
    capsize=5,
)
plt.ylabel("Average Query Time (ms)")
plt.title("Average Query Latency: Elasticsearch vs Whoosh")
plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.savefig("avg_latency_es_vs_whoosh.png")
plt.show()

# B) Latency distribution
plt.figure(figsize=(8, 5))
plt.boxplot(
    [df_bench["es_time_ms"], df_bench["whoosh_time_ms"]],
    labels=["Elasticsearch", "Whoosh"],
    showfliers=False,
)
plt.ylabel("Query Time (ms)")
plt.title("Query Latency Distribution (100 Random Queries)")
plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.savefig("latency_distribution_es_vs_whoosh.png")
plt.show()

# C) Indexing time comparison
plt.figure(figsize=(8, 5))
plt.bar(
    ["Elasticsearch", "Whoosh"],
    [elapsed_es_index * 1000, elapsed_whoosh_index * 1000],
    capsize=5,
)
plt.ylabel("Indexing Time (ms)")
plt.title("Indexing Time: Elasticsearch vs Whoosh")
plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.savefig("indexing_time_es_vs_whoosh.png")
plt.show()

# Print indexing times
print(f"[Elasticsearch] Indexed {NUM_DOCS} docs in {elapsed_es_index*1000:.2f} ms")
print(f"[Whoosh]       Indexed {NUM_DOCS} docs in {elapsed_whoosh_index*1000:.2f} ms")
