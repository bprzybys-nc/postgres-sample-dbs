# Create database connection configurations for mixed scenarios
database_connections_config = """# src/config/database_connections.py
# Database connection configurations for Mixed Reference scenarios
# These databases have service layer connections but NO complex business logic

import os
from typing import Dict, Optional
from dataclasses import dataclass
from urllib.parse import quote_plus

@dataclass
class DatabaseConfig:
    \"\"\"Database configuration data class\"\"\"
    host: str
    port: int
    database: str
    username: str
    password: str
    ssl_mode: str = "require"
    scenario_type: str = "MIXED"
    
    @property
    def connection_string(self) -> str:
        \"\"\"Generate PostgreSQL connection string\"\"\"
        return (
            f"postgresql://{quote_plus(self.username)}:"
            f"{quote_plus(self.password)}@{self.host}:{self.port}/"
            f"{self.database}?sslmode={self.ssl_mode}"
        )

class DatabaseConnectionManager:
    \"\"\"Manages database connections for mixed scenario databases\"\"\"
    
    def __init__(self):
        self._connections: Dict[str, DatabaseConfig] = {}
        self._load_configurations()
    
    def _load_configurations(self) -> None:
        \"\"\"Load database configurations from environment variables\"\"\"
        
        # Mixed Scenario: Pagila Database (DVD Rental Store)
        self._connections["pagila"] = DatabaseConfig(
            host=os.getenv("PAGILA_DB_HOST", "psql-pagila-staging.postgres.database.azure.com"),
            port=int(os.getenv("PAGILA_DB_PORT", "5432")),
            database=os.getenv("PAGILA_DB_NAME", "pagila"),
            username=os.getenv("PAGILA_DB_USER", "dbadmin"),
            password=os.getenv("PAGILA_DB_PASSWORD", ""),
            ssl_mode=os.getenv("PAGILA_DB_SSL_MODE", "require"),
            scenario_type="MIXED"
        )
        
        # Mixed Scenario: Chinook Database (Digital Media Store)  
        self._connections["chinook"] = DatabaseConfig(
            host=os.getenv("CHINOOK_DB_HOST", "psql-chinook-staging.postgres.database.azure.com"),
            port=int(os.getenv("CHINOOK_DB_PORT", "5432")),
            database=os.getenv("CHINOOK_DB_NAME", "chinook"),
            username=os.getenv("CHINOOK_DB_USER", "dbadmin"),
            password=os.getenv("CHINOOK_DB_PASSWORD", ""),
            ssl_mode=os.getenv("CHINOOK_DB_SSL_MODE", "require"),
            scenario_type="MIXED"
        )
        
        # Mixed Scenario: Netflix Database (Content Catalog)
        self._connections["netflix"] = DatabaseConfig(
            host=os.getenv("NETFLIX_DB_HOST", "psql-netflix-staging.postgres.database.azure.com"),
            port=int(os.getenv("NETFLIX_DB_PORT", "5432")),
            database=os.getenv("NETFLIX_DB_NAME", "netflix"),
            username=os.getenv("NETFLIX_DB_USER", "dbadmin"),
            password=os.getenv("NETFLIX_DB_PASSWORD", ""),
            ssl_mode=os.getenv("NETFLIX_DB_SSL_MODE", "require"),
            scenario_type="MIXED"
        )
    
    def get_config(self, database_name: str) -> Optional[DatabaseConfig]:
        \"\"\"Get database configuration by name\"\"\"
        return self._connections.get(database_name.lower())
    
    def get_connection_string(self, database_name: str) -> Optional[str]:
        \"\"\"Get connection string for database\"\"\"
        config = self.get_config(database_name)
        return config.connection_string if config else None
    
    def list_databases(self) -> Dict[str, str]:
        \"\"\"List all configured databases with their scenario types\"\"\"
        return {
            name: config.scenario_type 
            for name, config in self._connections.items()
        }
    
    def validate_connection_requirements(self, database_name: str) -> Dict[str, bool]:
        \"\"\"Validate that required environment variables are set\"\"\"
        config = self.get_config(database_name)
        if not config:
            return {"valid": False, "error": "Database not found"}
        
        validation_results = {
            "host_set": bool(config.host),
            "username_set": bool(config.username),
            "password_set": bool(config.password),
            "ssl_enabled": config.ssl_mode == "require",
            "azure_postgres": "postgres.database.azure.com" in config.host
        }
        
        validation_results["valid"] = all([
            validation_results["host_set"],
            validation_results["username_set"], 
            validation_results["password_set"]
        ])
        
        return validation_results

# Global connection manager instance
connection_manager = DatabaseConnectionManager()

# Environment variable templates for documentation
REQUIRED_ENV_VARS = {
    "PAGILA": [
        "PAGILA_DB_HOST=psql-pagila-staging.postgres.database.azure.com",
        "PAGILA_DB_USER=dbadmin",
        "PAGILA_DB_PASSWORD=your_secure_password",
        "PAGILA_DB_NAME=pagila",
        "PAGILA_DB_PORT=5432",
        "PAGILA_DB_SSL_MODE=require"
    ],
    "CHINOOK": [
        "CHINOOK_DB_HOST=psql-chinook-staging.postgres.database.azure.com", 
        "CHINOOK_DB_USER=dbadmin",
        "CHINOOK_DB_PASSWORD=your_secure_password",
        "CHINOOK_DB_NAME=chinook",
        "CHINOOK_DB_PORT=5432",
        "CHINOOK_DB_SSL_MODE=require"
    ],
    "NETFLIX": [
        "NETFLIX_DB_HOST=psql-netflix-staging.postgres.database.azure.com",
        "NETFLIX_DB_USER=dbadmin", 
        "NETFLIX_DB_PASSWORD=your_secure_password",
        "NETFLIX_DB_NAME=netflix",
        "NETFLIX_DB_PORT=5432",
        "NETFLIX_DB_SSL_MODE=require"
    ]
}

def print_env_var_template(database_name: str) -> None:
    \"\"\"Print environment variable template for a database\"\"\"
    db_name = database_name.upper()
    if db_name in REQUIRED_ENV_VARS:
        print(f"Required environment variables for {database_name}:")
        for env_var in REQUIRED_ENV_VARS[db_name]:
            print(f"  {env_var}")
    else:
        print(f"No template available for {database_name}")

if __name__ == "__main__":
    # Demo usage
    print("Database Connection Manager - Mixed Scenario Databases")
    print("=" * 55)
    
    databases = connection_manager.list_databases()
    for db_name, scenario in databases.items():
        print(f"\\n{db_name.upper()} ({scenario})")
        validation = connection_manager.validate_connection_requirements(db_name)
        print(f"  Configuration valid: {validation['valid']}")
        if not validation['valid']:
            print(f"  Missing requirements - check environment variables")
            print_env_var_template(db_name)
"""

# Save the database connections file
with open("database_connections.py", "w") as f:
    f.write(database_connections_config)

print("✅ Created database connection configurations")
print("File: src/config/database_connections.py")
print("Contains: pagila, chinook, netflix connection configs for MIXED scenarios")
print("Features: Environment variable management, SSL requirements, Azure PostgreSQL")
