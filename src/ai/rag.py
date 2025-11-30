import chromadb
from chromadb.utils import embedding_functions
import textwrap

from src.utils.embeddings import generate_embeddings

class RAGPipeline:
    def __init__(self, collection_name="cv_collection", persist_directory="./chroma_db"):
        """
        Initializes the RAG pipeline with a ChromaDB vector store.

        Args:
            collection_name (str): The name of the collection to use in ChromaDB.
            persist_directory (str): The directory to persist the ChromaDB data to.
        """
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def _chunk_text(self, text, chunk_size=1000, chunk_overlap=200):
        """
        Splits a text into overlapping chunks.

        Args:
            text (str): The text to chunk.
            chunk_size (int): The size of each chunk.
            chunk_overlap (int): The overlap between consecutive chunks.

        Returns:
            list[str]: A list of text chunks.
        """
        return textwrap.wrap(text, width=chunk_size, subsequent_indent=" " * (chunk_size - chunk_overlap))

    def index_documents(self, documents, metadatas=None):
        """
        Indexes a list of documents into the ChromaDB vector store.

        Args:
            documents (list[str]): A list of documents (e.g., CV texts) to index.
            metadatas (list[dict], optional): A list of metadata dictionaries corresponding to each document.
                                              Defaults to None.
        """
        if metadatas and len(documents) != len(metadatas):
            raise ValueError("The number of documents and metadatas must be the same.")

        all_chunks = []
        all_metadatas = []
        doc_ids = []

        for i, doc in enumerate(documents):
            chunks = self._chunk_text(doc)
            all_chunks.extend(chunks)
            
            # Create metadata for each chunk
            chunk_metadatas = []
            for j, chunk in enumerate(chunks):
                meta = metadatas[i].copy() if metadatas else {}
                meta['chunk_index'] = j
                chunk_metadatas.append(meta)
            all_metadatas.extend(chunk_metadatas)

            # Create unique IDs for each chunk
            for j in range(len(chunks)):
                doc_ids.append(f"doc_{i}_chunk_{j}")

        # Generate embeddings for all chunks at once
        embeddings = generate_embeddings(all_chunks)

        # Add the chunks, embeddings, and metadatas to the collection
        self.collection.add(
            embeddings=embeddings,
            documents=all_chunks,
            metadatas=all_metadatas,
            ids=doc_ids
        )
        print(f"Successfully indexed {len(documents)} documents into the '{self.collection.name}' collection.")

    def query(self, query_text, n_results=3):
        """
        Queries the vector store for the most relevant document chunks.

        Args:
            query_text (str): The text to query for.
            n_results (int): The number of results to return.

        Returns:
            dict: A dictionary containing the retrieved documents and their metadata.
        """
        query_embedding = generate_embeddings([query_text])
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        return results
