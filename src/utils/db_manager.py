"""
Database Management Utilities for ChromaDB

Provides utilities for managing ChromaDB collections, viewing statistics,
and performing database-level operations.
"""
import chromadb
from typing import List, Dict, Any
from pathlib import Path


class DatabaseManager:
    """Manages ChromaDB database operations across all collections."""
    
    def __init__(self, persist_directory="./chroma_db"):
        """
        Initialize database manager.
        
        Args:
            persist_directory (str): Path to ChromaDB persistence directory.
        """
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
    
    def list_all_collections(self) -> List[str]:
        """
        List all collection names in the database.
        
        Returns:
            list[str]: List of collection names.
        """
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            print(f"Error listing collections: {e}")
            return []
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive database statistics.
        
        Returns:
            dict: Database statistics including total documents, collections, etc.
        """
        try:
            collections = self.client.list_collections()
            collection_info = []
            total_documents = 0
            
            for col in collections:
                count = col.count()
                total_documents += count
                collection_info.append({
                    "name": col.name,
                    "document_count": count,
                    "metadata": col.metadata if hasattr(col, 'metadata') else {}
                })
            
            return {
                "total_collections": len(collections),
                "total_documents": total_documents,
                "collections": collection_info,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            return {
                "error": str(e),
                "total_collections": 0,
                "total_documents": 0,
                "collections": []
            }
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific collection.
        
        Args:
            collection_name (str): Name of the collection.
            
        Returns:
            dict: Collection information including document count and metadata.
        """
        try:
            collection = self.client.get_collection(name=collection_name)
            count = collection.count()
            
            return {
                "name": collection_name,
                "document_count": count,
                "metadata": collection.metadata if hasattr(collection, 'metadata') else {},
                "exists": True
            }
        except Exception as e:
            return {
                "name": collection_name,
                "exists": False,
                "error": str(e)
            }
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete an entire collection.
        
        Args:
            collection_name (str): Name of the collection to delete.
            
        Returns:
            bool: True if deletion was successful.
        """
        try:
            self.client.delete_collection(name=collection_name)
            print(f"Successfully deleted collection: {collection_name}")
            return True
        except Exception as e:
            print(f"Error deleting collection {collection_name}: {e}")
            return False
    
    def get_indexed_documents(self, collection_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get indexed documents from a collection.
        
        Args:
            collection_name (str): Name of the collection.
            limit (int): Maximum number of documents to return.
            
        Returns:
            list[dict]: List of documents with their metadata.
        """
        try:
            collection = self.client.get_collection(name=collection_name)
            results = collection.get(limit=limit)
            
            documents = []
            if results and 'ids' in results:
                for i, doc_id in enumerate(results['ids']):
                    doc_info = {
                        'id': doc_id,
                        'metadata': results.get('metadatas', [])[i] if i < len(results.get('metadatas', [])) else {},
                        'preview': results.get('documents', [])[i][:200] if i < len(results.get('documents', [])) else ''
                    }
                    documents.append(doc_info)
            
            return documents
        except Exception as e:
            print(f"Error getting documents from {collection_name}: {e}")
            return []
    
    def clear_all_collections(self) -> Dict[str, bool]:
        """
        Clear all documents from all collections (keeps collections, removes documents).
        
        Returns:
            dict: Dictionary mapping collection names to success status.
        """
        try:
            collections = self.client.list_collections()
            results = {}
            
            for col in collections:
                try:
                    # Get all IDs and delete them
                    data = col.get()
                    if data and 'ids' in data and len(data['ids']) > 0:
                        col.delete(ids=data['ids'])
                        results[col.name] = True
                    else:
                        results[col.name] = True  # Already empty
                except Exception as e:
                    print(f"Error clearing {col.name}: {e}")
                    results[col.name] = False
            
            return results
        except Exception as e:
            print(f"Error clearing collections: {e}")
            return {}


# Global database manager instance
db_manager = DatabaseManager()
