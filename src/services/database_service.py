# src/services/database_service.py
# Basic database service layer for Mixed Reference scenarios
# Simple connection management without complex business logic

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from contextlib import asynccontextmanager
import asyncpg
from asyncpg import Connection, Pool
from dataclasses import dataclass
from datetime import datetime

from src.config.database_connections import connection_manager, DatabaseConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConnectionInfo:
    """Connection information for monitoring"""
    database_name: str
    connected_at: datetime
    connection_count: int
    last_query_at: Optional[datetime] = None
    scenario_type: str = "MIXED"

class DatabaseHealthChecker:
    """Health check utilities for database connections"""

    @staticmethod
    async def check_connection(config: DatabaseConfig) -> Dict[str, Any]:
        """Check if database connection is healthy"""
        try:
            conn = await asyncpg.connect(config.connection_string)

            # Simple health check query
            result = await conn.fetchval("SELECT 1")
            server_version = await conn.fetchval("SELECT version()")

            await conn.close()

            return {
                "healthy": True,
                "database": config.database,
                "server_version": server_version,
                "checked_at": datetime.utcnow().isoformat(),
                "scenario_type": config.scenario_type
            }

        except Exception as e:
            logger.error(f"Health check failed for {config.database}: {e}")
            return {
                "healthy": False,
                "database": config.database,
                "error": str(e),
                "checked_at": datetime.utcnow().isoformat(),
                "scenario_type": config.scenario_type
            }

class DatabaseService:
    """Basic database service for mixed scenario databases"""

    def __init__(self):
        self._pools: Dict[str, Pool] = {}
        self._connection_info: Dict[str, ConnectionInfo] = {}

    async def initialize_pool(self, database_name: str, min_size: int = 2, max_size: int = 10) -> bool:
        """Initialize connection pool for a database"""
        try:
            config = connection_manager.get_config(database_name)
            if not config:
                logger.error(f"No configuration found for database: {database_name}")
                return False

            # Create connection pool
            pool = await asyncpg.create_pool(
                config.connection_string,
                min_size=min_size,
                max_size=max_size,
                command_timeout=30
            )

            self._pools[database_name] = pool
            self._connection_info[database_name] = ConnectionInfo(
                database_name=database_name,
                connected_at=datetime.utcnow(),
                connection_count=min_size,
                scenario_type=config.scenario_type
            )

            logger.info(f"Initialized connection pool for {database_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize pool for {database_name}: {e}")
            return False

    @asynccontextmanager
    async def get_connection(self, database_name: str):
        """Get database connection from pool"""
        if database_name not in self._pools:
            raise ValueError(f"Pool not initialized for database: {database_name}")

        pool = self._pools[database_name]
        async with pool.acquire() as connection:
            # Update last query time
            if database_name in self._connection_info:
                self._connection_info[database_name].last_query_at = datetime.utcnow()
            yield connection

    async def execute_query(self, database_name: str, query: str, *args) -> List[Dict[str, Any]]:
        """Execute a simple SELECT query (read-only operations)"""
        try:
            async with self.get_connection(database_name) as conn:
                rows = await conn.fetch(query, *args)
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Query execution failed for {database_name}: {e}")
            raise

    async def get_table_info(self, database_name: str) -> List[Dict[str, Any]]:
        """Get basic table information (metadata only)"""
        query = """
        SELECT 
            table_name,
            table_type,
            is_insertable_into
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
        """

        return await self.execute_query(database_name, query)

    async def get_connection_stats(self, database_name: str) -> Dict[str, Any]:
        """Get connection statistics"""
        if database_name not in self._pools:
            return {"error": "Pool not initialized"}

        pool = self._pools[database_name]
        info = self._connection_info.get(database_name)

        return {
            "database_name": database_name,
            "pool_size": pool.get_size(),
            "pool_idle": pool.get_idle_size(),
            "connected_at": info.connected_at.isoformat() if info else None,
            "last_query_at": info.last_query_at.isoformat() if info and info.last_query_at else None,
            "scenario_type": info.scenario_type if info else "UNKNOWN"
        }

    async def close_pool(self, database_name: str) -> None:
        """Close connection pool for a database"""
        if database_name in self._pools:
            await self._pools[database_name].close()
            del self._pools[database_name]
            del self._connection_info[database_name]
            logger.info(f"Closed connection pool for {database_name}")

    async def close_all_pools(self) -> None:
        """Close all connection pools"""
        for database_name in list(self._pools.keys()):
            await self.close_pool(database_name)

# Specific service classes for each mixed scenario database

class PagilaService(DatabaseService):
    """Service for Pagila DVD rental database (Mixed scenario)"""

    def __init__(self):
        super().__init__()
        self.database_name = "pagila"

    async def get_film_count(self) -> int:
        """Get total number of films (simple read operation)"""
        result = await self.execute_query(
            self.database_name, 
            "SELECT COUNT(*) as count FROM film"
        )
        return result[0]["count"] if result else 0

    async def get_customer_count(self) -> int:
        """Get total number of customers (simple read operation)"""
        result = await self.execute_query(
            self.database_name,
            "SELECT COUNT(*) as count FROM customer"
        )
        return result[0]["count"] if result else 0

class ChinookService(DatabaseService):
    """Service for Chinook digital media database (Mixed scenario)"""

    def __init__(self):
        super().__init__()
        self.database_name = "chinook"

    async def get_track_count(self) -> int:
        """Get total number of tracks (simple read operation)"""
        result = await self.execute_query(
            self.database_name,
            "SELECT COUNT(*) as count FROM "Track""
        )
        return result[0]["count"] if result else 0

    async def get_artist_count(self) -> int:
        """Get total number of artists (simple read operation)"""
        result = await self.execute_query(
            self.database_name,
            "SELECT COUNT(*) as count FROM "Artist""
        )
        return result[0]["count"] if result else 0

class NetflixService(DatabaseService):
    """Service for Netflix content database (Mixed scenario)"""

    def __init__(self):
        super().__init__()
        self.database_name = "netflix"

    async def get_title_count(self) -> int:
        """Get total number of titles (simple read operation)"""
        result = await self.execute_query(
            self.database_name,
            "SELECT COUNT(*) as count FROM netflix_titles"
        )
        return result[0]["count"] if result else 0

    async def get_content_types(self) -> List[str]:
        """Get distinct content types (simple read operation)"""
        result = await self.execute_query(
            self.database_name,
            "SELECT DISTINCT type FROM netflix_titles WHERE type IS NOT NULL"
        )
        return [row["type"] for row in result]

# Service factory for mixed scenario databases
class MixedScenarioServiceFactory:
    """Factory to create service instances for mixed scenario databases"""

    @staticmethod
    def create_service(database_name: str) -> Optional[DatabaseService]:
        """Create appropriate service instance for database"""
        services = {
            "pagila": PagilaService,
            "chinook": ChinookService, 
            "netflix": NetflixService
        }

        service_class = services.get(database_name.lower())
        return service_class() if service_class else None

    @staticmethod
    async def health_check_all() -> Dict[str, Dict[str, Any]]:
        """Run health checks on all mixed scenario databases"""
        results = {}

        for db_name in ["pagila", "chinook", "netflix"]:
            config = connection_manager.get_config(db_name)
            if config:
                results[db_name] = await DatabaseHealthChecker.check_connection(config)
            else:
                results[db_name] = {
                    "healthy": False,
                    "error": "Configuration not found",
                    "database": db_name
                }

        return results

# Global service instances
pagila_service = PagilaService()
chinook_service = ChinookService()
netflix_service = NetflixService()

if __name__ == "__main__":
    async def demo():
        """Demo the database services"""
        print("Database Service Demo - Mixed Scenario Databases")
        print("=" * 50)

        # Health check all databases
        health_results = await MixedScenarioServiceFactory.health_check_all()

        for db_name, health in health_results.items():
            print(f"\n{db_name.upper()}: {'✅ Healthy' if health['healthy'] else '❌ Unhealthy'}")
            if not health['healthy'] and 'error' in health:
                print(f"  Error: {health['error']}")

    asyncio.run(demo())
