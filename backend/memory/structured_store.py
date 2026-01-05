import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import asyncio
import aiosqlite

@dataclass
class CodeEntity:
    id: str
    type: str  # 'widget', 'api_endpoint', 'model', 'service'
    name: str
    file_path: str
    language: str  # 'dart', 'python'
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class Relationship:
    id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: str  # 'calls', 'extends', 'implements', 'uses'
    metadata: Dict[str, Any]
    created_at: datetime

class StructuredStore:
    """SQLite database for storing structured code entities and relationships"""
    
    def __init__(self, db_path: str = "fd_agent_structured.db"):
        self.db_path = db_path
    
    async def init_db(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS code_entities (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    language TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id TEXT PRIMARY KEY,
                    source_entity_id TEXT NOT NULL,
                    target_entity_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_entity_id) REFERENCES code_entities (id),
                    FOREIGN KEY (target_entity_id) REFERENCES code_entities (id)
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS change_requests (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    implementation_notes TEXT,
                    affected_entities TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS api_mappings (
                    id TEXT PRIMARY KEY,
                    flutter_widget_id TEXT,
                    python_endpoint_id TEXT,
                    mapping_type TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (flutter_widget_id) REFERENCES code_entities (id),
                    FOREIGN KEY (python_endpoint_id) REFERENCES code_entities (id)
                )
            """)
            
            # Create indexes for better performance
            await db.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON code_entities (type)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_entities_language ON code_entities (language)")
            await db.execute("CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships (relationship_type)")
            
            await db.commit()
    
    async def add_entity(self, entity: CodeEntity) -> bool:
        """Add a code entity"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO code_entities 
                    (id, type, name, file_path, language, metadata, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    entity.id, entity.type, entity.name, entity.file_path,
                    entity.language, json.dumps(entity.metadata), datetime.now()
                ))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error adding entity: {e}")
            return False
    
    async def add_relationship(self, relationship: Relationship) -> bool:
        """Add a relationship between entities"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO relationships 
                    (id, source_entity_id, target_entity_id, relationship_type, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    relationship.id, relationship.source_entity_id,
                    relationship.target_entity_id, relationship.relationship_type,
                    json.dumps(relationship.metadata)
                ))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error adding relationship: {e}")
            return False
    
    async def get_entities_by_type(self, entity_type: str) -> List[CodeEntity]:
        """Get all entities of a specific type"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT id, type, name, file_path, language, metadata, created_at, updated_at
                FROM code_entities WHERE type = ?
            """, (entity_type,))
            
            rows = await cursor.fetchall()
            entities = []
            
            for row in rows:
                entities.append(CodeEntity(
                    id=row[0], type=row[1], name=row[2], file_path=row[3],
                    language=row[4], metadata=json.loads(row[5] or '{}'),
                    created_at=datetime.fromisoformat(row[6]),
                    updated_at=datetime.fromisoformat(row[7])
                ))
            
            return entities
    
    async def get_related_entities(self, entity_id: str, relationship_type: Optional[str] = None) -> List[CodeEntity]:
        """Get entities related to a given entity"""
        query = """
            SELECT e.id, e.type, e.name, e.file_path, e.language, e.metadata, e.created_at, e.updated_at
            FROM code_entities e
            JOIN relationships r ON (e.id = r.target_entity_id OR e.id = r.source_entity_id)
            WHERE (r.source_entity_id = ? OR r.target_entity_id = ?) AND e.id != ?
        """
        params = [entity_id, entity_id, entity_id]
        
        if relationship_type:
            query += " AND r.relationship_type = ?"
            params.append(relationship_type)
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            
            entities = []
            for row in rows:
                entities.append(CodeEntity(
                    id=row[0], type=row[1], name=row[2], file_path=row[3],
                    language=row[4], metadata=json.loads(row[5] or '{}'),
                    created_at=datetime.fromisoformat(row[6]),
                    updated_at=datetime.fromisoformat(row[7])
                ))
            
            return entities
    
    async def add_api_mapping(self, flutter_widget_id: str, python_endpoint_id: str, mapping_type: str, metadata: Dict[str, Any]) -> bool:
        """Add mapping between Flutter widget and Python endpoint"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                mapping_id = f"{flutter_widget_id}_{python_endpoint_id}"
                await db.execute("""
                    INSERT OR REPLACE INTO api_mappings 
                    (id, flutter_widget_id, python_endpoint_id, mapping_type, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (mapping_id, flutter_widget_id, python_endpoint_id, mapping_type, json.dumps(metadata)))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error adding API mapping: {e}")
            return False
    
    async def get_api_mappings(self, widget_id: Optional[str] = None, endpoint_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get API mappings"""
        query = "SELECT * FROM api_mappings WHERE 1=1"
        params = []
        
        if widget_id:
            query += " AND flutter_widget_id = ?"
            params.append(widget_id)
        
        if endpoint_id:
            query += " AND python_endpoint_id = ?"
            params.append(endpoint_id)
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            
            mappings = []
            for row in rows:
                mappings.append({
                    'id': row[0],
                    'flutter_widget_id': row[1],
                    'python_endpoint_id': row[2],
                    'mapping_type': row[3],
                    'metadata': json.loads(row[4] or '{}'),
                    'created_at': row[5]
                })
            
            return mappings
    
    async def add_change_request(self, cr_id: str, title: str, description: str, affected_entities: List[str]) -> bool:
        """Add a change request"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO change_requests 
                    (id, title, description, affected_entities, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (cr_id, title, description, json.dumps(affected_entities), datetime.now()))
                await db.commit()
                return True
        except Exception as e:
            print(f"Error adding change request: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            stats = {}
            
            # Count entities by type
            cursor = await db.execute("SELECT type, COUNT(*) FROM code_entities GROUP BY type")
            entity_counts = await cursor.fetchall()
            stats['entities'] = {row[0]: row[1] for row in entity_counts}
            
            # Count relationships by type
            cursor = await db.execute("SELECT relationship_type, COUNT(*) FROM relationships GROUP BY relationship_type")
            rel_counts = await cursor.fetchall()
            stats['relationships'] = {row[0]: row[1] for row in rel_counts}
            
            # Count change requests
            cursor = await db.execute("SELECT COUNT(*) FROM change_requests")
            cr_count = await cursor.fetchone()
            stats['change_requests'] = cr_count[0]
            
            # Count API mappings
            cursor = await db.execute("SELECT COUNT(*) FROM api_mappings")
            mapping_count = await cursor.fetchone()
            stats['api_mappings'] = mapping_count[0]
            
            return stats