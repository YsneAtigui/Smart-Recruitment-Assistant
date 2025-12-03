"""
Chunk Verification Script for RAG System

This script verifies that all documents are properly indexed in ChromaDB
and displays chunks with their metadata for debugging purposes.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai.rag import RAGPipeline


def print_separator(char="=", length=80):
    """Print a separator line"""
    print(char * length)


def get_all_collections(persist_directory="./chroma_db") -> List[str]:
    """Get all collection names in the ChromaDB"""
    try:
        # Use a temporary pipeline to access the client
        temp_pipeline = RAGPipeline(collection_name="temp", persist_directory=persist_directory)
        collections = temp_pipeline.client.list_collections()
        return [col.name for col in collections]
    except Exception as e:
        print(f"Error accessing ChromaDB: {e}")
        return []


def analyze_collection(collection_name: str, persist_directory="./chroma_db"):
    """Analyze a single collection and display statistics"""
    print_separator()
    print(f"COLLECTION: {collection_name}")
    print_separator()
    
    try:
        pipeline = RAGPipeline(collection_name=collection_name, persist_directory=persist_directory)
        
        # Get collection stats
        stats = pipeline.get_collection_stats()
        print(f"\n📊 Collection Statistics:")
        print(f"   Total chunks: {stats.get('document_count', 0)}")
        
        # Get all chunks
        chunks = pipeline.get_all_chunks()
        
        if not chunks:
            print("\n⚠️  No chunks found in this collection!")
            return
        
        # Analyze metadata
        metadata_summary = defaultdict(set)
        chunk_sizes = []
        empty_chunks = []
        
        for chunk in chunks:
            # Track chunk sizes
            chunk_sizes.append(chunk.get('content_length', 0))
            
            # Check for empty chunks
            if chunk.get('content_length', 0) == 0:
                empty_chunks.append(chunk.get('id'))
            
            # Collect metadata
            metadata = chunk.get('metadata', {})
            for key, value in metadata.items():
                if isinstance(value, (str, int, bool)):
                    metadata_summary[key].add(str(value))
        
        # Display metadata summary
        print(f"\n📋 Metadata Summary:")
        for key, values in metadata_summary.items():
            if key == 'chunk_index':
                continue
            print(f"   {key}: {len(values)} unique value(s)")
            if len(values) <= 10:  # Only show values if there aren't too many
                for val in sorted(values):
                    print(f"      - {val}")
        
        # Display chunk size statistics
        if chunk_sizes:
            avg_size = sum(chunk_sizes) / len(chunk_sizes)
            print(f"\n📏 Chunk Size Statistics:")
            print(f"   Average size: {avg_size:.0f} characters")
            print(f"   Min size: {min(chunk_sizes)} characters")
            print(f"   Max size: {max(chunk_sizes)} characters")
        
        # Display empty chunks warning
        if empty_chunks:
            print(f"\n⚠️  Warning: {len(empty_chunks)} empty chunks found!")
            print(f"   IDs: {', '.join(empty_chunks[:5])}")
            if len(empty_chunks) > 5:
                print(f"   ... and {len(empty_chunks) - 5} more")
        
        # Display sample chunks
        print(f"\n📄 Sample Chunks (showing up to 5):")
        for i, chunk in enumerate(chunks[:5]):
            print(f"\n   --- Chunk {i+1}/{min(5, len(chunks))} ---")
            print(f"   ID: {chunk.get('id')}")
            print(f"   Size: {chunk.get('content_length')} chars")
            print(f"   Has Embedding: {chunk.get('has_embedding', False)}")
            
            metadata = chunk.get('metadata', {})
            if metadata:
                print(f"   Metadata:")
                for key, value in metadata.items():
                    print(f"      {key}: {value}")
            
            content = chunk.get('content', '')
            preview = content[:200] + "..." if len(content) > 200 else content
            print(f"   Content Preview: {preview}")
        
        # Group chunks by candidate/job
        print(f"\n👥 Document Distribution:")
        if 'candidate_id' in metadata_summary or 'candidate_name' in metadata_summary:
            candidates = metadata_summary.get('candidate_name', set()) or metadata_summary.get('candidate_id', set())
            print(f"   Candidates: {len(candidates)}")
            for candidate in sorted(candidates)[:10]:
                # Count chunks for this candidate
                candidate_chunks = [c for c in chunks if c.get('metadata', {}).get('candidate_name') == candidate or c.get('metadata', {}).get('candidate_id') == candidate]
                print(f"      - {candidate}: {len(candidate_chunks)} chunks")
        
        if 'type' in metadata_summary:
            types = metadata_summary.get('type', set())
            print(f"   Document Types:")
            for doc_type in sorted(types):
                type_chunks = [c for c in chunks if c.get('metadata', {}).get('type') == doc_type]
                print(f"      - {doc_type}: {len(type_chunks)} chunks")
        
    except Exception as e:
        print(f"\n❌ Error analyzing collection: {e}")
        import traceback
        traceback.print_exc()


def test_query(collection_name: str, test_query: str, persist_directory="./chroma_db"):
    """Test a sample query on the collection"""
    print(f"\n🔍 Testing Query: '{test_query}'")
    print_separator("-")
    
    try:
        pipeline = RAGPipeline(collection_name=collection_name, persist_directory=persist_directory)
        results = pipeline.query(test_query, n_results=3)
        
        if results.get('documents'):
            docs = results['documents'][0]
            print(f"   Retrieved {len(docs)} results:")
            for i, doc in enumerate(docs):
                preview = doc[:150] + "..." if len(doc) > 150 else doc
                print(f"\n   Result {i+1}:")
                print(f"   {preview}")
        else:
            print("   No results found")
            
    except Exception as e:
        print(f"   ❌ Query failed: {e}")


def main():
    """Main verification function"""
    print("\n" + "="*80)
    print(" "*25 + "RAG CHUNK VERIFICATION")
    print("="*80)
    
    persist_directory = "./chroma_db"
    
    # Check if chroma_db exists
    if not os.path.exists(persist_directory):
        print(f"\n❌ ChromaDB directory not found: {persist_directory}")
        print("   Please ensure documents have been indexed first.")
        return
    
    # Get all collections
    print(f"\n🔍 Scanning ChromaDB at: {persist_directory}\n")
    collections = get_all_collections(persist_directory)
    
    if not collections:
        print("❌ No collections found in ChromaDB!")
        print("   Please index some documents first using the /rag/index endpoint.")
        return
    
    print(f"✅ Found {len(collections)} collection(s):\n")
    for i, col_name in enumerate(collections, 1):
        print(f"   {i}. {col_name}")
    
    # Analyze each collection
    for collection_name in collections:
        analyze_collection(collection_name, persist_directory)
        
        # Test a sample query
        if collection_name.startswith("job_"):
            test_query(collection_name, "What skills are required?", persist_directory)
        elif collection_name == "all_cvs":
            test_query(collection_name, "What experience does the candidate have?", persist_directory)
        elif collection_name == "job_descriptions":
            test_query(collection_name, "What are the job requirements?", persist_directory)
    
    # Summary
    print_separator()
    print("\n✅ Verification Complete!")
    print(f"   Total collections analyzed: {len(collections)}")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
