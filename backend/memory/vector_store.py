import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import uuid
import json
from config import settings

class VectorStore:
    """Vector database for storing and retrieving code context"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=False)
        )
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # Collections for different types of content
        self.flutter_collection = self._get_or_create_collection("flutter_code")
        self.python_collection = self._get_or_create_collection("python_code")
        self.brd_collection = self._get_or_create_collection("brd_documents")
        self.cr_collection = self._get_or_create_collection("change_requests")
    
    def _get_or_create_collection(self, name: str):
        """Get or create a collection"""
        try:
            return self.client.get_collection(name)
        except:
            return self.client.create_collection(name)
    
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize metadata for ChromaDB (convert lists/dicts to strings)"""
        sanitized = {}
        for key, value in metadata.items():
            if isinstance(value, (list, dict)):
                sanitized[key] = json.dumps(value) if value else ""
            elif value is None:
                sanitized[key] = ""
            elif isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            else:
                sanitized[key] = str(value)
        return sanitized
    
    def add_flutter_code(self, file_path: str, content: str, metadata: Dict[str, Any]):
        """Add Flutter code to vector store"""
        embedding = self.embedding_model.encode([content])[0].tolist()
        
        sanitized_metadata = self._sanitize_metadata(metadata)
        self.flutter_collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[{
                "file_path": file_path,
                "type": "flutter",
                **sanitized_metadata
            }],
            ids=[str(uuid.uuid4())]
        )
    
    def add_python_code(self, file_path: str, content: str, metadata: Dict[str, Any]):
        """Add Python code to vector store"""
        embedding = self.embedding_model.encode([content])[0].tolist()
        
        sanitized_metadata = self._sanitize_metadata(metadata)
        self.python_collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[{
                "file_path": file_path,
                "type": "python",
                **sanitized_metadata
            }],
            ids=[str(uuid.uuid4())]
        )
    
    def add_brd_content(self, document_name: str, content: str, metadata: Dict[str, Any]):
        """Add BRD content to vector store"""
        embedding = self.embedding_model.encode([content])[0].tolist()
        
        sanitized_metadata = self._sanitize_metadata(metadata)
        self.brd_collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[{
                "document_name": document_name,
                "type": "brd",
                **sanitized_metadata
            }],
            ids=[str(uuid.uuid4())]
        )
    
    def add_change_request(self, cr_id: str, description: str, implementation: str, metadata: Dict[str, Any]):
        """Add change request and its implementation"""
        content = f"CR: {description}\nImplementation: {implementation}"
        embedding = self.embedding_model.encode([content])[0].tolist()
        
        self.cr_collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[{
                "cr_id": cr_id,
                "description": description,
                "type": "change_request",
                **metadata
            }],
            ids=[str(uuid.uuid4())]
        )
    
    def search_flutter_code(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search Flutter code by query"""
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        results = self.flutter_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return self._format_results(results)
    
    def search_python_code(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search Python code by query"""
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        results = self.python_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return self._format_results(results)
    
    def search_brd_content(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search BRD content by query"""
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        results = self.brd_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return self._format_results(results)
    
    def search_similar_crs(self, query: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Search for similar change requests"""
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        results = self.cr_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return self._format_results(results)
    
    def search_all(self, query: str, n_results: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """Search across all collections"""
        return {
            "flutter": self.search_flutter_code(query, n_results//4),
            "python": self.search_python_code(query, n_results//4),
            "brd": self.search_brd_content(query, n_results//4),
            "change_requests": self.search_similar_crs(query, n_results//4)
        }
    
    def _format_results(self, results) -> List[Dict[str, Any]]:
        """Format search results"""
        formatted = []
        
        if not results['documents']:
            return formatted
        
        for i in range(len(results['documents'][0])):
            formatted.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics about collections"""
        return {
            "flutter_code": self.flutter_collection.count(),
            "python_code": self.python_collection.count(),
            "brd_documents": self.brd_collection.count(),
            "change_requests": self.cr_collection.count()
        }