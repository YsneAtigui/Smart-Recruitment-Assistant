import chromadb
from chromadb.utils import embedding_functions
import textwrap
from typing import List, Dict, Any, Optional
from datetime import datetime

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
        self.persist_directory = persist_directory
        self.collection_name = collection_name

    def _chunk_text(self, text, chunk_size=1000, chunk_overlap=200):
        """
        Splits a text into overlapping chunks with better handling.

        Args:
            text (str): The text to chunk.
            chunk_size (int): The size of each chunk.
            chunk_overlap (int): The overlap between consecutive chunks.

        Returns:
            list[str]: A list of text chunks.
        """
        if not text or len(text.strip()) == 0:
            return []
        
        # Better chunking: split by sentences/paragraphs first
        chunks = []
        current_chunk = ""
        
        # Simple sentence splitting
        sentences = text.replace('\n', ' ').split('. ')
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + '. '
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + '. '
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text[:chunk_size]]

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

    def query_with_filter(self, query_text: str, metadata_filter: Optional[Dict[str, Any]] = None, n_results: int = 3):
        """
        Queries the vector store with metadata filtering.

        Args:
            query_text (str): The text to query for.
            metadata_filter (dict, optional): Metadata filters to apply.
            n_results (int): The number of results to return.

        Returns:
            dict: A dictionary containing the retrieved documents and their metadata.
        """
        query_embedding = generate_embeddings([query_text])
        
        query_params = {
            "query_embeddings": query_embedding,
            "n_results": n_results
        }
        
        if metadata_filter:
            query_params["where"] = metadata_filter
        
        results = self.collection.query(**query_params)
        return results

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current collection.

        Returns:
            dict: Statistics including document count and collection metadata.
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "metadata": self.collection.metadata if hasattr(self.collection, 'metadata') else {}
            }
        except Exception as e:
            return {
                "collection_name": self.collection_name,
                "document_count": 0,
                "error": str(e)
            }

    def delete_documents(self, ids: List[str]) -> bool:
        """
        Delete documents from the collection by their IDs.

        Args:
            ids (list[str]): List of document IDs to delete.

        Returns:
            bool: True if deletion was successful.
        """
        try:
            self.collection.delete(ids=ids)
            print(f"Successfully deleted {len(ids)} documents from '{self.collection_name}'")
            return True
        except Exception as e:
            print(f"Error deleting documents: {e}")
            return False

    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection.

        Returns:
            bool: True if clearing was successful.
        """
        try:
            # Get all document IDs and delete them
            results = self.collection.get()
            if results and 'ids' in results and len(results['ids']) > 0:
                self.collection.delete(ids=results['ids'])
                print(f"Successfully cleared collection '{self.collection_name}'")
            return True
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False

    def get_all_documents(self) -> List[Dict[str, Any]]:
        """
        Get all documents in the collection with their metadata.

        Returns:
            list[dict]: List of documents with their IDs, content, and metadata.
        """
        try:
            results = self.collection.get()
            documents = []
            
            if results and 'ids' in results:
                for i, doc_id in enumerate(results['ids']):
                    doc_info = {
                        'id': doc_id,
                        'metadata': results.get('metadatas', [])[i] if i < len(results.get('metadatas', [])) else {},
                        'content': results.get('documents', [])[i] if i < len(results.get('documents', [])) else ''
                    }
                    documents.append(doc_info)
            
            return documents
        except Exception as e:
            print(f"Error getting documents: {e}")
            return []
