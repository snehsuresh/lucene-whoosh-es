import json
from index_utils import ensure_index
from whoosh import writing

# Sample data
DATA = [
    {
        "id": "1",
        "name": "Red T-Shirt",
        "description": "A bright red t-shirt made from 100% cotton.",
        "category": "clothing",
        "available": True,
        "latitude": 37.7749,
        "longitude": -122.4194
    },
    {
        "id": "2",
        "name": "Blue Jeans",
        "description": "Comfortable blue jeans with a classic fit.",
        "category": "clothing",
        "available": True,
        "latitude": 34.0522,
        "longitude": -118.2437
    },
    {
        "id": "3",
        "name": "Wireless Mouse",
        "description": "Ergonomic wireless mouse with adjustable DPI.",
        "category": "electronics",
        "available": False,
        "latitude": 40.7128,
        "longitude": -74.0060
    }
]

def main():
    ix = ensure_index()
    writer = ix.writer()
    for item in DATA:
        writer.update_document(
            id=item["id"],
            name=item["name"],
            description=item["description"],
            category=item["category"],
            available=item["available"],
            latitude=item["latitude"],
            longitude=item["longitude"]
        )
    writer.commit()
    print("Indexing complete. Index stored in 'indexdir'.")

if __name__ == "__main__":
    main()
