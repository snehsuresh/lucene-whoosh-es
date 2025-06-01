// LuceneBenchmark.java

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StoredField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.IndexOptions;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.search.Query;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.store.FSDirectory;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import java.io.*;
import java.nio.file.Paths;
import java.util.*;

public class LuceneBenchmark {

    static class Doc {
        String id;
        String name;
        String category;
        boolean available;
        String content;
    }

    public static void main(String[] args) throws Exception {
        final int NUM_QUERIES = 100;
        final String INDEX_DIR = "lucene_index";
        final String DOCS_FILE = "docs_data.json";

        // 1. Load synthetic docs from JSON
        Gson gson = new Gson();
        List<Doc> docs;
        try (Reader reader = new FileReader(DOCS_FILE)) {
            docs = gson.fromJson(reader, new TypeToken<List<Doc>>() {}.getType());
        }

        // 2. Setup Lucene Analyzer, IndexWriter
        Analyzer analyzer = new StandardAnalyzer();
        FSDirectory directory = FSDirectory.open(Paths.get(INDEX_DIR));
        IndexWriterConfig config = new IndexWriterConfig(analyzer);
        IndexWriter writer = new IndexWriter(directory, config);

        // 3. Indexing documents and measure time
        long startIndex = System.nanoTime();
        for (Doc d : docs) {
            Document doc = new Document();
            // id (stored, not tokenized)
            doc.add(new StringField("id", d.id, Field.Store.YES));
            // name (stored & tokenized)
            doc.add(new TextField("name", d.name, Field.Store.YES));
            // category (stored, keyword)
            doc.add(new StringField("category", d.category, Field.Store.YES));
            // available (stored as string)
            doc.add(new StoredField("available", d.available ? "true" : "false"));
            // content (tokenized, stored)
            doc.add(new TextField("content", d.content, Field.Store.YES));
            writer.addDocument(doc);
        }
        writer.close();
        long elapsedIndex = System.nanoTime() - startIndex;

        System.out.printf("[Lucene] Indexed %d docs in %.2f ms%n",
                docs.size(), elapsedIndex / 1_000_000.0);

        // 4. Prepare searcher
        DirectoryReader readerIdx = DirectoryReader.open(directory);
        IndexSearcher searcher = new IndexSearcher(readerIdx);
        QueryParser parser = new QueryParser("content", analyzer);

        // 5. Generate 100 random queries from the same VOCAB
        String[] vocab = {"pizza","burger","sushi","taco","pasta","salad","sandwich","steak","noodle","curry"};
        Random rand = new Random();
        List<String> queries = new ArrayList<>();
        for (int i = 0; i < NUM_QUERIES; i++) {
            queries.add(vocab[rand.nextInt(vocab.length)]);
        }

        // 6. Benchmark queries
        class Result {
            String query;
            double timeMs;
            int hits;
        }
        List<Result> results = new ArrayList<>();

        for (String term : queries) {
            long t0 = System.nanoTime();
            Query q = parser.parse(term);
            TopDocs topDocs = searcher.search(q, docs.size());
            long t1 = System.nanoTime();
            Result r = new Result();
            r.query = term;
            r.timeMs = (t1 - t0) / 1_000_000.0;
            r.hits = (int) topDocs.totalHits.value;
            results.add(r);
        }

        // 7. Print raw results (first 10)
        System.out.println("\n--- Raw Benchmark Results (first 10 queries) ---");
        System.out.printf("%-10s %-12s %-6s%n", "Query", "Time (ms)", "Hits");
        for (int i = 0; i < 10; i++) {
            Result r = results.get(i);
            System.out.printf("%-10s %-12.3f %-6d%n", r.query, r.timeMs, r.hits);
        }

        // 8. Compute summary stats (mean, median, p90, p99)
        List<Double> times = new ArrayList<>();
        for (Result r : results) times.add(r.timeMs);
        Collections.sort(times);
        double mean = times.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
        double median = times.get(times.size() / 2);
        double p90 = times.get((int) (times.size() * 0.9));
        double p99 = times.get((int) (times.size() * 0.99));

        System.out.println("\n--- Summary Statistics (ms) ---");
        System.out.printf("Mean   : %.3f%n", mean);
        System.out.printf("Median : %.3f%n", median);
        System.out.printf("p90    : %.3f%n", p90);
        System.out.printf("p99    : %.3f%n", p99);

        readerIdx.close();
        directory.close();
    }
}
