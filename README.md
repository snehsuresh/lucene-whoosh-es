# Search Engine Prototype

This is a prototype search engine built with Whoosh (Lucene-style indexing) and FastAPI.

## Structure

- `schema.json`: Defines the index schema.
- `indexer/main.py`: Indexer service to build and store indices.
- `indexer/index_utils.py`: Utility functions for indexing.
- `searcher/main.py`: Searcher service to serve queries.
- `searcher/query_planner.py`: Module to transform raw queries into Whoosh-compatible queries.
- `requirements.txt`: Python dependencies.

## How to Run

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Index data**

   ```bash
   python indexer/main.py
   ```

   This will create an index in `indexdir`.

3. **Run searcher**

   ```bash
   uvicorn searcher.main:app --reload --port 8000
   ```

4. **Query**  
   Send a GET request to `http://localhost:8000/search?q=your+search+term`

## Sample Usage

```bash
curl "http://localhost:8000/search?q=laptop&category=electronics"
```

## Benchmark

### Lucene vs Elasticsearch vs Whoosh: A 2025 Search Engine Benchmark

=================================================================

- Apache Lucene (Java) – the low-level engine powering Elasticsearch
- Elasticsearch – REST-based, distributed search engine
- Whoosh – pure-Python, lightweight Lucene-like engine

Inspired by DoorDash’s custom search stack, which replaced Elasticsearch with a performance-optimized Lucene-based engine, this project tests what happens when you do the same — at a small scale.

### Why Benchmark

---

After struggling with high tail latencies using Elasticsearch (~938ms p99), I built a prototype to test Lucene directly, just as DoorDash did. This repo includes:

- Benchmark scripts for each engine
- 5,000 synthetic documents representing menu items
- 100 single-term queries to measure:
  - Mean & p99 latency
  - Indexing speed
  - Hit count accuracy
- Visualizations comparing the results

### Results Summary

---

| Engine        | Mean Latency | P99 Latency | Indexing Time |
| ------------- | ------------ | ----------- | ------------- |
| Lucene        | 2.7 ms       | 16.8 ms     | 411 ms        |
| Whoosh        | 77.1 ms      | 161.0 ms    | 1350 ms       |
| Elasticsearch | 277.6 ms     | 938.7 ms    | 1671 ms       |

Lucene outperformed both alternatives by over 100x at the tail.

### Project Structure

---

- benchmark_es_whoosh.py - Python: Elasticsearch vs Whoosh benchmark
- LuceneBenchmark.java - Java: Lucene benchmark
- docs_data.json - 5k synthetic documents
- visualize.py - (Optional) Visualization script
- requirements.txt - Python dependencies
- README.txt - This file
- schema.json - Optional: field structure
- indexer/ - (Optional) indexing logic
- searcher/ - (Optional) query logic
- .gitignore

### How to Run

---

1. Install requirements

   pip install -r requirements.txt

   Make sure Elasticsearch is running locally on port 9200.

2. Run Python benchmark

   python benchmark_es_whoosh.py

   This generates docs_data.json and benchmark visualizations.

3. Run Lucene benchmark (Java)

   javac -cp "lib/_" LuceneBenchmark.java java -cp ".:lib/_" LuceneBenchmark

### Visual Summary

---

Output charts:

- avg_latency_es_vs_whoosh.png
- latency_distribution_es_vs_whoosh.png
- indexing_time_es_vs_whoosh.png

### Repo Name Suggestions

---

- lucene-vs-es-vs-whoosh
- doordash-inspired-search
- fastsearch-prototype
- lucene-benchmark-2025
- search-stack-reimagined
