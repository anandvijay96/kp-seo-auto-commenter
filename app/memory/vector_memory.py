import chromadb
from chromadb.utils import embedding_functions
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use a specific sentence transformer model
# This provides more control and avoids ambiguity with default models.
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

class VectorMemory:
    """
    A class to manage agent memory using a ChromaDB vector store.
    """
    def __init__(self, host="chromadb", port=8000, collection_name="agent_memory"):
        """
        Initializes the connection to the ChromaDB server and gets or creates a collection.
        """
        try:
            self.client = chromadb.HttpClient(
                host=host, 
                port=port,
                # Explicitly setting tenant and database can help with connection issues
                tenant="default_tenant",
                database="default_database"
            )
            # Use the specific sentence transformer embedding function
            self.embedding_function = sentence_transformer_ef
            
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}  # Specify the distance metric
            )
            self.collection_name = collection_name
            logger.info(f"Successfully connected to ChromaDB and got collection '{collection_name}'.")
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB or get collection: {e}")
            self.client = None
            self.collection = None

    def add_memory(self, document: str, metadata: dict, doc_id: str):
        """
        Adds a new memory (document) to the collection.
        """
        if not self.collection:
            logger.error("Cannot add memory, collection is not available.")
            return
        
        try:
            self.collection.add(
                documents=[document],
                metadatas=[metadata],
                ids=[doc_id]
            )
            logger.info(f"Successfully added memory with ID: {doc_id}")
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")

    def retrieve_memories(self, query: str, n_results: int = 5) -> list:
        """
        Retrieves the most relevant memories for a given query.
        """
        if not self.collection:
            logger.error("Cannot retrieve memories, collection is not available.")
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            logger.info(f"Retrieved {len(results.get('documents', [[]])[0])} memories for query: '{query}'")
            return results.get('documents', [[]])[0]
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            return []
