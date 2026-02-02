"""
Azure Cosmos DB Operations

This module demonstrates CRUD operations with Azure Cosmos DB using the SQL API.
Covers database and container management, document operations, and queries.

Requirements:
    pip install azure-cosmos azure-identity

Environment Variables:
    AZURE_COSMOS_ENDPOINT: Cosmos DB account endpoint (e.g., https://myaccount.documents.azure.com:443/)
    AZURE_COSMOS_KEY: Cosmos DB account key
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.cosmos.container import ContainerProxy
from azure.cosmos.database import DatabaseProxy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CosmosDBManager:
    """
    Manages Azure Cosmos DB operations using SQL API.
    
    Provides methods for database and container management, CRUD operations,
    and querying documents with the SQL API.
    """
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        key: Optional[str] = None
    ):
        """
        Initialize Cosmos DB manager.
        
        Args:
            endpoint: Cosmos DB endpoint URL
            key: Cosmos DB account key
        """
        self.endpoint = endpoint or os.getenv('AZURE_COSMOS_ENDPOINT')
        self.key = key or os.getenv('AZURE_COSMOS_KEY')
        
        if not all([self.endpoint, self.key]):
            raise ValueError(
                "Cosmos DB endpoint and key must be provided or set in environment: "
                "AZURE_COSMOS_ENDPOINT, AZURE_COSMOS_KEY"
            )
        
        # Initialize Cosmos client
        self.client = CosmosClient(self.endpoint, self.key)
        
        logger.info(f"Initialized Cosmos DB client for: {self.endpoint}")
    
    def create_database(
        self,
        database_name: str,
        throughput: Optional[int] = 400
    ) -> DatabaseProxy:
        """
        Create a database.
        
        Args:
            database_name: Name of the database
            throughput: Optional throughput in RU/s (Request Units per second)
        
        Returns:
            DatabaseProxy instance
        """
        try:
            logger.info(f"Creating database: {database_name}")
            
            database = self.client.create_database_if_not_exists(
                id=database_name,
                offer_throughput=throughput
            )
            
            logger.info(f"Database ready: {database_name}")
            return database
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to create database: {e}")
            raise
    
    def create_container(
        self,
        database_name: str,
        container_name: str,
        partition_key_path: str = "/id",
        throughput: Optional[int] = 400
    ) -> ContainerProxy:
        """
        Create a container in a database.
        
        Args:
            database_name: Database name
            container_name: Container name
            partition_key_path: Partition key path (e.g., "/category")
            throughput: Optional throughput in RU/s
        
        Returns:
            ContainerProxy instance
        """
        try:
            logger.info(f"Creating container: {container_name} in {database_name}")
            
            database = self.client.get_database_client(database_name)
            
            container = database.create_container_if_not_exists(
                id=container_name,
                partition_key=PartitionKey(path=partition_key_path),
                offer_throughput=throughput
            )
            
            logger.info(f"Container ready: {container_name}")
            return container
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to create container: {e}")
            raise
    
    def insert_document(
        self,
        database_name: str,
        container_name: str,
        document: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Insert a document into a container.
        
        Args:
            database_name: Database name
            container_name: Container name
            document: Document to insert (must include 'id' field)
        
        Returns:
            Created document with metadata
        
        Example:
            doc = {
                "id": "1",
                "name": "Product A",
                "category": "Electronics",
                "price": 99.99
            }
            result = manager.insert_document("mydb", "products", doc)
        """
        try:
            logger.info(f"Inserting document into {container_name}")
            
            # Ensure document has an ID
            if 'id' not in document:
                document['id'] = str(uuid.uuid4())
            
            # Add timestamp
            document['_created_at'] = datetime.utcnow().isoformat()
            
            database = self.client.get_database_client(database_name)
            container = database.get_container_client(container_name)
            
            created_document = container.create_item(body=document)
            
            logger.info(f"Document created with ID: {created_document['id']}")
            return created_document
            
        except exceptions.CosmosResourceExistsError:
            logger.error(f"Document with ID {document.get('id')} already exists")
            raise
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to insert document: {e}")
            raise
    
    def read_document(
        self,
        database_name: str,
        container_name: str,
        document_id: str,
        partition_key: Any
    ) -> Dict[str, Any]:
        """
        Read a document by ID.
        
        Args:
            database_name: Database name
            container_name: Container name
            document_id: Document ID
            partition_key: Partition key value
        
        Returns:
            Document data
        """
        try:
            logger.info(f"Reading document: {document_id}")
            
            database = self.client.get_database_client(database_name)
            container = database.get_container_client(container_name)
            
            document = container.read_item(
                item=document_id,
                partition_key=partition_key
            )
            
            logger.info(f"Document retrieved: {document_id}")
            return document
            
        except exceptions.CosmosResourceNotFoundError:
            logger.error(f"Document not found: {document_id}")
            raise
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to read document: {e}")
            raise
    
    def update_document(
        self,
        database_name: str,
        container_name: str,
        document_id: str,
        partition_key: Any,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a document.
        
        Args:
            database_name: Database name
            container_name: Container name
            document_id: Document ID
            partition_key: Partition key value
            updates: Dictionary of fields to update
        
        Returns:
            Updated document
        """
        try:
            logger.info(f"Updating document: {document_id}")
            
            # Read existing document
            document = self.read_document(
                database_name,
                container_name,
                document_id,
                partition_key
            )
            
            # Apply updates
            document.update(updates)
            document['_updated_at'] = datetime.utcnow().isoformat()
            
            # Replace document
            database = self.client.get_database_client(database_name)
            container = database.get_container_client(container_name)
            
            updated_document = container.replace_item(
                item=document_id,
                body=document
            )
            
            logger.info(f"Document updated: {document_id}")
            return updated_document
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to update document: {e}")
            raise
    
    def delete_document(
        self,
        database_name: str,
        container_name: str,
        document_id: str,
        partition_key: Any
    ) -> None:
        """
        Delete a document.
        
        Args:
            database_name: Database name
            container_name: Container name
            document_id: Document ID
            partition_key: Partition key value
        """
        try:
            logger.info(f"Deleting document: {document_id}")
            
            database = self.client.get_database_client(database_name)
            container = database.get_container_client(container_name)
            
            container.delete_item(
                item=document_id,
                partition_key=partition_key
            )
            
            logger.info(f"Document deleted: {document_id}")
            
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"Document not found: {document_id}")
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to delete document: {e}")
            raise
    
    def query_documents(
        self,
        database_name: str,
        container_name: str,
        query: str,
        parameters: Optional[List[Dict[str, Any]]] = None,
        partition_key: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Query documents using SQL API.
        
        Args:
            database_name: Database name
            container_name: Container name
            query: SQL query string
            parameters: Optional query parameters
            partition_key: Optional partition key for single-partition queries
        
        Returns:
            List of matching documents
        
        Example:
            results = manager.query_documents(
                "mydb",
                "products",
                "SELECT * FROM c WHERE c.price > @min_price",
                parameters=[{"name": "@min_price", "value": 50}]
            )
        """
        try:
            logger.info(f"Querying documents: {query[:100]}...")
            
            database = self.client.get_database_client(database_name)
            container = database.get_container_client(container_name)
            
            # Prepare query parameters
            query_params = {}
            if partition_key is not None:
                query_params['partition_key'] = partition_key
            if parameters:
                query_params['parameters'] = parameters
            
            # Execute query
            items = list(container.query_items(
                query=query,
                enable_cross_partition_query=True,
                **query_params
            ))
            
            logger.info(f"Query returned {len(items)} documents")
            return items
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Query failed: {e}")
            raise
    
    def upsert_document(
        self,
        database_name: str,
        container_name: str,
        document: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Insert or update a document (upsert).
        
        Args:
            database_name: Database name
            container_name: Container name
            document: Document to upsert
        
        Returns:
            Upserted document
        """
        try:
            logger.info(f"Upserting document: {document.get('id', 'new')}")
            
            # Ensure document has an ID
            if 'id' not in document:
                document['id'] = str(uuid.uuid4())
            
            # Add/update timestamp
            if '_created_at' not in document:
                document['_created_at'] = datetime.utcnow().isoformat()
            document['_updated_at'] = datetime.utcnow().isoformat()
            
            database = self.client.get_database_client(database_name)
            container = database.get_container_client(container_name)
            
            upserted_document = container.upsert_item(body=document)
            
            logger.info(f"Document upserted: {upserted_document['id']}")
            return upserted_document
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Upsert failed: {e}")
            raise
    
    def bulk_insert(
        self,
        database_name: str,
        container_name: str,
        documents: List[Dict[str, Any]]
    ) -> int:
        """
        Insert multiple documents.
        
        Args:
            database_name: Database name
            container_name: Container name
            documents: List of documents to insert
        
        Returns:
            Number of documents inserted
        """
        logger.info(f"Bulk inserting {len(documents)} documents")
        
        inserted_count = 0
        for doc in documents:
            try:
                self.insert_document(database_name, container_name, doc)
                inserted_count += 1
            except Exception as e:
                logger.warning(f"Failed to insert document: {e}")
        
        logger.info(f"Successfully inserted {inserted_count}/{len(documents)} documents")
        return inserted_count
    
    def delete_database(self, database_name: str) -> None:
        """
        Delete a database.
        
        Args:
            database_name: Database name
        """
        try:
            logger.warning(f"Deleting database: {database_name}")
            
            database = self.client.get_database_client(database_name)
            database.delete_database()
            
            logger.info(f"Database deleted: {database_name}")
            
        except exceptions.CosmosResourceNotFoundError:
            logger.warning(f"Database not found: {database_name}")
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Failed to delete database: {e}")
            raise


def main():
    """
    Main function demonstrating Cosmos DB operations.
    """
    try:
        logger.info("=" * 60)
        logger.info("Azure Cosmos DB Example")
        logger.info("=" * 60)
        
        # Initialize manager
        # Note: Update with your Cosmos DB endpoint and key
        cosmos_manager = CosmosDBManager(
            # endpoint="https://your-account.documents.azure.com:443/",
            # key="your-key"
        )
        
        database_name = "demo_database"
        container_name = "products"
        
        # Create database
        logger.info("\n--- Creating Database ---")
        cosmos_manager.create_database(database_name, throughput=400)
        
        # Create container
        logger.info("\n--- Creating Container ---")
        cosmos_manager.create_container(
            database_name,
            container_name,
            partition_key_path="/category"
        )
        
        # Insert documents
        logger.info("\n--- Inserting Documents ---")
        products = [
            {
                "id": "1",
                "name": "Laptop",
                "category": "Electronics",
                "price": 999.99,
                "in_stock": True
            },
            {
                "id": "2",
                "name": "Mouse",
                "category": "Electronics",
                "price": 29.99,
                "in_stock": True
            },
            {
                "id": "3",
                "name": "Desk",
                "category": "Furniture",
                "price": 299.99,
                "in_stock": False
            }
        ]
        
        for product in products:
            cosmos_manager.insert_document(database_name, container_name, product)
        
        # Read document
        logger.info("\n--- Reading Document ---")
        doc = cosmos_manager.read_document(
            database_name,
            container_name,
            "1",
            partition_key="Electronics"
        )
        logger.info(f"Retrieved: {doc['name']} - ${doc['price']}")
        
        # Update document
        logger.info("\n--- Updating Document ---")
        cosmos_manager.update_document(
            database_name,
            container_name,
            "1",
            partition_key="Electronics",
            updates={"price": 899.99, "on_sale": True}
        )
        
        # Query documents
        logger.info("\n--- Querying Documents ---")
        results = cosmos_manager.query_documents(
            database_name,
            container_name,
            "SELECT * FROM c WHERE c.category = @category",
            parameters=[{"name": "@category", "value": "Electronics"}]
        )
        
        logger.info("Electronics products:")
        for item in results:
            logger.info(f"  - {item['name']}: ${item['price']}")
        
        # Query with price filter
        logger.info("\n--- Query with Price Filter ---")
        results = cosmos_manager.query_documents(
            database_name,
            container_name,
            "SELECT * FROM c WHERE c.price < @max_price ORDER BY c.price",
            parameters=[{"name": "@max_price", "value": 500}]
        )
        
        logger.info("Products under $500:")
        for item in results:
            logger.info(f"  - {item['name']}: ${item['price']}")
        
        # Cleanup (commented out for safety)
        # logger.info("\n--- Cleanup ---")
        # cosmos_manager.delete_database(database_name)
        
        logger.info("\n" + "=" * 60)
        logger.info("Example completed successfully!")
        logger.info("=" * 60)
        logger.info(f"\nRemember to clean up: Delete database '{database_name}'")
        
    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
