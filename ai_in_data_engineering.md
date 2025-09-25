# AI in Data Engineering: Complete Guide

A comprehensive guide to leveraging Artificial Intelligence, Large Language Models (LLMs), and AI-powered tools in modern data engineering workflows.

## Table of Contents

1. [Overview](#overview)
2. [Core AI Concepts for Data Engineers](#core-ai-concepts)
3. [Large Language Models (LLMs) Integration](#llms-integration)
4. [Prompt Engineering for Data Tasks](#prompt-engineering)
5. [Retrieval Augmented Generation (RAG)](#rag-setup)
6. [Vector Databases](#vector-databases)
7. [AI Agents for Pipeline Automation](#ai-agents)
8. [Practical Examples](#practical-examples)
9. [Use Case Mapping](#use-case-mapping)
10. [FAQ](#faq)

---

## Overview

Modern data engineering is being transformed by AI technologies. This guide explores how data engineers can leverage AI for:

- **Automated ETL pipeline generation and optimization**
- **Natural language querying of data catalogs**
- **Intelligent anomaly detection in data pipelines**
- **Automated documentation generation**
- **Smart data quality monitoring**
- **Context-aware troubleshooting and alerting**

### Key Benefits for Data Engineers

- **Productivity**: Automate repetitive coding and documentation tasks
- **Intelligence**: Add semantic understanding to data workflows
- **Efficiency**: Reduce manual intervention in pipeline monitoring
- **Accessibility**: Enable natural language interaction with data systems

---

## Core AI Concepts

### 1. Large Language Models (LLMs)

LLMs are AI models trained on vast amounts of text data, capable of understanding and generating human-like text. In data engineering, they excel at:

- Code generation (SQL, Python, Scala)
- Documentation creation
- Natural language to query translation
- Error analysis and troubleshooting

**Relevance for Data Engineering:**
- Generate ETL scripts from natural language descriptions
- Create data pipeline documentation automatically
- Translate business requirements into technical specifications
- Provide intelligent error diagnostics

### 2. Prompt Engineering

The art and science of crafting effective inputs to LLMs to achieve desired outputs.

**Key Principles:**
- **Clarity**: Be specific about what you want
- **Context**: Provide relevant background information
- **Examples**: Use few-shot learning with examples
- **Structure**: Use consistent formatting and templates

### 3. Retrieval Augmented Generation (RAG)

RAG combines the power of LLMs with external knowledge bases, enabling AI to provide accurate, up-to-date information beyond its training data.

**Components:**
- **Knowledge Base**: Document corpus (data catalogs, schemas, logs)
- **Vector Store**: Embedded representations of documents
- **Retrieval System**: Finds relevant documents for queries
- **Generation Model**: LLM that uses retrieved context

### 4. Vector Databases

Specialized databases optimized for storing and querying high-dimensional vectors, essential for semantic search and RAG implementations.

**Popular Options:**
- **ChromaDB**: Open-source, Python-friendly
- **FAISS**: Facebook's similarity search library
- **Pinecone**: Managed vector database service
- **Weaviate**: Open-source vector search engine

---

## LLMs Integration

### Setting Up OpenAI Integration

```python
import openai
import os
from typing import List, Dict, Any

class DataEngineeringLLM:
    def __init__(self, api_key: str = None):
        """Initialize OpenAI client for data engineering tasks."""
        self.client = openai.OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )
    
    def generate_sql(self, description: str, schema_info: str) -> str:
        """Generate SQL query from natural language description."""
        prompt = f"""
        Given the following database schema:
        {schema_info}
        
        Generate a SQL query to: {description}
        
        Requirements:
        - Use proper SQL syntax
        - Include appropriate JOINs if needed
        - Add comments explaining complex logic
        - Optimize for performance
        
        SQL Query:
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert SQL developer specializing in data engineering."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        return response.choices[0].message.content
    
    def generate_etl_code(self, source: str, target: str, transformations: str) -> str:
        """Generate Python ETL code based on requirements."""
        prompt = f"""
        Create a Python ETL pipeline with the following specifications:
        
        Source: {source}
        Target: {target}
        Transformations: {transformations}
        
        Requirements:
        - Use pandas for data manipulation
        - Include error handling
        - Add logging
        - Make it production-ready
        - Include data validation
        
        Python Code:
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert Python developer specializing in ETL pipelines."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
        return response.choices[0].message.content

# Usage Example
llm = DataEngineeringLLM()

# Generate SQL
schema = """
Tables:
- customers (id, name, email, created_at)
- orders (id, customer_id, total, order_date)
- products (id, name, price, category)
- order_items (order_id, product_id, quantity, price)
"""

sql_query = llm.generate_sql(
    "Find the top 10 customers by total order value in the last 30 days",
    schema
)
print(sql_query)
```

### Using Local LLMs with Ollama

Building on the existing pattern in the repository:

```python
import requests
import json
from typing import Optional, Dict, Any

class OllamaDataEngineer:
    def __init__(self, host: str = "http://localhost:11434"):
        """Initialize Ollama client for data engineering tasks."""
        self.host = host
    
    def query_ollama(self, prompt: str, model: str = "codellama") -> str:
        """Query Ollama model with enhanced error handling."""
        url = f"{self.host}/api/generate"
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9
            }
        }
        
        try:
            response = requests.post(url, json=data, timeout=60)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            print(f"[Ollama] Request Error: {e}")
            return "AI analysis unavailable due to connection error."
        except Exception as e:
            print(f"[Ollama] Error: {e}")
            return "AI analysis unavailable due to error."
    
    def analyze_data_quality(self, df_info: Dict[str, Any]) -> str:
        """Analyze data quality issues using AI."""
        prompt = f"""
        Analyze the following dataset information for data quality issues:
        
        Dataset Info:
        {json.dumps(df_info, indent=2)}
        
        Please identify potential data quality issues and suggest remediation steps:
        1. Missing values and strategies to handle them
        2. Data type inconsistencies
        3. Outliers and anomalies
        4. Duplicate records
        5. Data integrity constraints
        
        Provide specific, actionable recommendations.
        """
        
        return self.query_ollama(prompt, model="codellama")
    
    def generate_airflow_dag(self, requirements: str) -> str:
        """Generate Airflow DAG code based on requirements."""
        prompt = f"""
        Create an Apache Airflow DAG with the following requirements:
        {requirements}
        
        Please include:
        - Proper imports and DAG configuration
        - Error handling and retries
        - Task dependencies
        - Logging and monitoring
        - Best practices for production use
        
        Python DAG Code:
        """
        
        return self.query_ollama(prompt, model="codellama")

# Usage Example
ollama_de = OllamaDataEngineer()

# Analyze data quality
df_info = {
    "shape": [1000, 5],
    "columns": ["id", "name", "email", "age", "salary"],
    "dtypes": ["int64", "object", "object", "float64", "float64"],
    "missing_values": {"name": 10, "email": 5, "age": 20},
    "duplicates": 15
}

quality_analysis = ollama_de.analyze_data_quality(df_info)
print("Data Quality Analysis:")
print(quality_analysis)
```

---

## Prompt Engineering

### ETL Automation Recipes

#### 1. SQL Generation Template

```python
def create_sql_prompt(description: str, schema: str, constraints: str = "") -> str:
    """Create optimized prompt for SQL generation."""
    return f"""
You are an expert SQL developer. Generate a SQL query based on the following:

TASK: {description}

SCHEMA:
{schema}

CONSTRAINTS:
{constraints if constraints else "None"}

REQUIREMENTS:
- Write clean, readable SQL
- Use appropriate indexes hints if needed
- Include comments for complex logic
- Optimize for performance
- Handle edge cases (NULL values, empty results)

OUTPUT FORMAT:
```sql
-- Query description
-- Expected result format
[SQL QUERY HERE]
```

EXPLANATION:
[Brief explanation of the query logic]
"""

# Usage
prompt = create_sql_prompt(
    description="Calculate monthly recurring revenue (MRR) by customer segment",
    schema="""
    subscriptions (id, customer_id, plan_id, start_date, end_date, monthly_price)
    customers (id, segment, company_size, industry)
    plans (id, name, features, pricing_tier)
    """,
    constraints="Only include active subscriptions, group by customer segment"
)
```

#### 2. Data Pipeline Troubleshooting

```python
def create_troubleshooting_prompt(error_log: str, pipeline_context: str) -> str:
    """Create prompt for pipeline troubleshooting."""
    return f"""
You are a data engineering expert specializing in pipeline troubleshooting.

PIPELINE CONTEXT:
{pipeline_context}

ERROR LOG:
{error_log}

ANALYSIS REQUIRED:
1. Root cause analysis
2. Immediate fix recommendations
3. Prevention strategies
4. Monitoring improvements

RESPONSE FORMAT:
## Root Cause
[Detailed analysis of what went wrong]

## Immediate Fix
[Step-by-step solution]

## Prevention
[How to prevent this in the future]

## Monitoring
[What alerts/checks to add]
"""

# Usage
troubleshooting_prompt = create_troubleshooting_prompt(
    error_log="ConnectionError: Unable to connect to PostgreSQL database",
    pipeline_context="Daily ETL job extracting customer data from API to warehouse"
)
```

#### 3. Code Review and Optimization

```python
def create_code_review_prompt(code: str, context: str) -> str:
    """Create prompt for code review and optimization."""
    return f"""
You are a senior data engineer reviewing code for production deployment.

CONTEXT: {context}

CODE TO REVIEW:
```python
{code}
```

REVIEW CRITERIA:
1. Code quality and readability
2. Performance optimization
3. Error handling
4. Security considerations
5. Best practices compliance
6. Scalability concerns

RESPONSE FORMAT:
## Overall Assessment
[Rating: Excellent/Good/Needs Improvement/Poor]

## Strengths
- [List positive aspects]

## Issues Found
- [Critical issues that must be fixed]
- [Minor improvements suggestions]

## Optimized Version
```python
[Improved code here]
```

## Additional Recommendations
[Deployment, monitoring, testing suggestions]
"""
```

---

## RAG Setup

### Building a Data Catalog RAG System

```python
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader, JSONLoader
from typing import List, Dict, Any
import os

class DataCatalogRAG:
    def __init__(self, persist_directory: str = "./data_catalog_db"):
        """Initialize RAG system for data catalog search."""
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vectorstore = None
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize or load existing vector store."""
        if os.path.exists(self.persist_directory):
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        else:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
    
    def add_schema_documentation(self, schema_docs: List[Dict[str, Any]]):
        """Add database schema documentation to the vector store."""
        documents = []
        
        for schema in schema_docs:
            # Create comprehensive text representation
            doc_text = f"""
            Table: {schema['table_name']}
            Database: {schema.get('database', 'unknown')}
            Description: {schema.get('description', 'No description available')}
            
            Columns:
            {self._format_columns(schema.get('columns', []))}
            
            Sample Queries:
            {schema.get('sample_queries', 'No sample queries available')}
            
            Business Context:
            {schema.get('business_context', 'No business context available')}
            
            Data Quality Rules:
            {schema.get('quality_rules', 'No quality rules defined')}
            """
            
            documents.append({
                'text': doc_text,
                'metadata': {
                    'table_name': schema['table_name'],
                    'database': schema.get('database', 'unknown'),
                    'type': 'schema_doc'
                }
            })
        
        # Split documents and add to vector store
        texts = []
        metadatas = []
        
        for doc in documents:
            chunks = self.text_splitter.split_text(doc['text'])
            for chunk in chunks:
                texts.append(chunk)
                metadatas.append(doc['metadata'])
        
        self.vectorstore.add_texts(texts=texts, metadatas=metadatas)
        self.vectorstore.persist()
    
    def add_pipeline_documentation(self, pipeline_docs: List[Dict[str, Any]]):
        """Add data pipeline documentation to the vector store."""
        documents = []
        
        for pipeline in pipeline_docs:
            doc_text = f"""
            Pipeline: {pipeline['pipeline_name']}
            Type: {pipeline.get('pipeline_type', 'ETL')}
            Schedule: {pipeline.get('schedule', 'On-demand')}
            
            Description: {pipeline.get('description', 'No description available')}
            
            Source Systems:
            {self._format_sources(pipeline.get('sources', []))}
            
            Target Systems:
            {self._format_targets(pipeline.get('targets', []))}
            
            Transformations:
            {pipeline.get('transformations', 'No transformations documented')}
            
            Monitoring:
            {pipeline.get('monitoring', 'No monitoring information')}
            
            Troubleshooting Guide:
            {pipeline.get('troubleshooting', 'No troubleshooting guide available')}
            """
            
            documents.append({
                'text': doc_text,
                'metadata': {
                    'pipeline_name': pipeline['pipeline_name'],
                    'pipeline_type': pipeline.get('pipeline_type', 'ETL'),
                    'type': 'pipeline_doc'
                }
            })
        
        # Process and add documents
        texts = []
        metadatas = []
        
        for doc in documents:
            chunks = self.text_splitter.split_text(doc['text'])
            for chunk in chunks:
                texts.append(chunk)
                metadatas.append(doc['metadata'])
        
        self.vectorstore.add_texts(texts=texts, metadatas=metadatas)
        self.vectorstore.persist()
    
    def search_catalog(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search the data catalog using semantic similarity."""
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        
        return [
            {
                'content': doc.page_content,
                'metadata': doc.metadata,
                'score': score
            }
            for doc, score in results
        ]
    
    def answer_question(self, question: str, llm_client) -> str:
        """Answer questions about the data catalog using RAG."""
        # Retrieve relevant documents
        relevant_docs = self.search_catalog(question, k=3)
        
        # Create context from retrieved documents
        context = "\n\n".join([doc['content'] for doc in relevant_docs])
        
        # Create prompt for the LLM
        prompt = f"""
        You are a data engineering expert with access to our data catalog.
        Use the following context to answer the user's question accurately.
        
        CONTEXT:
        {context}
        
        QUESTION: {question}
        
        INSTRUCTIONS:
        - Provide accurate information based on the context
        - If information is not available in the context, say so
        - Include relevant table names, column names, and technical details
        - Suggest follow-up questions if appropriate
        
        ANSWER:
        """
        
        # Get response from LLM (using the existing pattern)
        if hasattr(llm_client, 'query_ollama'):
            return llm_client.query_ollama(prompt)
        else:
            # Assume OpenAI client
            response = llm_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful data engineering assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            return response.choices[0].message.content
    
    def _format_columns(self, columns: List[Dict]) -> str:
        """Format column information for documentation."""
        if not columns:
            return "No column information available"
        
        formatted = []
        for col in columns:
            formatted.append(
                f"- {col.get('name', 'unknown')}: {col.get('type', 'unknown')} "
                f"{'(NOT NULL)' if col.get('nullable', True) == False else ''} "
                f"- {col.get('description', 'No description')}"
            )
        return "\n".join(formatted)
    
    def _format_sources(self, sources: List[str]) -> str:
        """Format source system information."""
        return "\n".join([f"- {source}" for source in sources]) if sources else "No sources documented"
    
    def _format_targets(self, targets: List[str]) -> str:
        """Format target system information."""
        return "\n".join([f"- {target}" for target in targets]) if targets else "No targets documented"


# Usage Example
rag_system = DataCatalogRAG()

# Add schema documentation
schema_docs = [
    {
        'table_name': 'customers',
        'database': 'production',
        'description': 'Main customer information table',
        'columns': [
            {'name': 'id', 'type': 'bigint', 'nullable': False, 'description': 'Primary key'},
            {'name': 'email', 'type': 'varchar(255)', 'nullable': False, 'description': 'Customer email address'},
            {'name': 'created_at', 'type': 'timestamp', 'nullable': False, 'description': 'Account creation date'}
        ],
        'sample_queries': 'SELECT * FROM customers WHERE created_at > NOW() - INTERVAL 30 DAY',
        'business_context': 'Contains all registered customers across all platforms'
    }
]

rag_system.add_schema_documentation(schema_docs)

# Search the catalog
results = rag_system.search_catalog("How do I find customers created in the last month?")
for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Content: {result['content'][:200]}...")
    print("---")
```

---

## Vector Databases

### ChromaDB Implementation

```python
import chromadb
from chromadb.config import Settings
import pandas as pd
from typing import List, Dict, Any
import json

class DataEngineeringVectorDB:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB for data engineering use cases."""
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collections = {}
    
    def create_pipeline_logs_collection(self) -> chromadb.Collection:
        """Create collection for pipeline log analysis."""
        collection = self.client.get_or_create_collection(
            name="pipeline_logs",
            metadata={"description": "Data pipeline execution logs and errors"}
        )
        self.collections["pipeline_logs"] = collection
        return collection
    
    def create_schema_collection(self) -> chromadb.Collection:
        """Create collection for database schema information."""
        collection = self.client.get_or_create_collection(
            name="schemas",
            metadata={"description": "Database schemas and table documentation"}
        )
        self.collections["schemas"] = collection
        return collection
    
    def add_pipeline_logs(self, logs: List[Dict[str, Any]]):
        """Add pipeline logs to vector database for semantic search."""
        if "pipeline_logs" not in self.collections:
            self.create_pipeline_logs_collection()
        
        collection = self.collections["pipeline_logs"]
        
        documents = []
        metadatas = []
        ids = []
        
        for i, log in enumerate(logs):
            # Create searchable text from log entry
            doc_text = f"""
            Pipeline: {log.get('pipeline_name', 'unknown')}
            Status: {log.get('status', 'unknown')}
            Timestamp: {log.get('timestamp', 'unknown')}
            Duration: {log.get('duration', 'unknown')}
            
            Message: {log.get('message', '')}
            Error: {log.get('error', 'No error')}
            
            Context:
            Source: {log.get('source', 'unknown')}
            Target: {log.get('target', 'unknown')}
            Records Processed: {log.get('records_processed', 0)}
            """
            
            documents.append(doc_text)
            metadatas.append({
                'pipeline_name': log.get('pipeline_name', 'unknown'),
                'status': log.get('status', 'unknown'),
                'timestamp': log.get('timestamp', 'unknown'),
                'log_level': log.get('log_level', 'INFO')
            })
            ids.append(f"log_{i}_{log.get('timestamp', i)}")
        
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    def search_similar_errors(self, error_description: str, n_results: int = 5) -> List[Dict]:
        """Find similar errors in pipeline logs."""
        if "pipeline_logs" not in self.collections:
            return []
        
        collection = self.collections["pipeline_logs"]
        results = collection.query(
            query_texts=[error_description],
            n_results=n_results,
            where={"status": "ERROR"}
        )
        
        return [
            {
                'document': doc,
                'metadata': meta,
                'distance': dist
            }
            for doc, meta, dist in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )
        ]
    
    def find_related_schemas(self, table_description: str, n_results: int = 5) -> List[Dict]:
        """Find schemas related to a description."""
        if "schemas" not in self.collections:
            return []
        
        collection = self.collections["schemas"]
        results = collection.query(
            query_texts=[table_description],
            n_results=n_results
        )
        
        return [
            {
                'document': doc,
                'metadata': meta,
                'distance': dist
            }
            for doc, meta, dist in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )
        ]


# Usage Example
vector_db = DataEngineeringVectorDB()

# Add pipeline logs
sample_logs = [
    {
        'pipeline_name': 'customer_etl',
        'status': 'ERROR',
        'timestamp': '2024-01-15T10:30:00Z',
        'duration': '45s',
        'message': 'ETL pipeline failed during transformation step',
        'error': 'ConnectionError: Unable to connect to PostgreSQL database at host db.example.com',
        'source': 'customer_api',
        'target': 'data_warehouse',
        'records_processed': 1250,
        'log_level': 'ERROR'
    },
    {
        'pipeline_name': 'sales_etl',
        'status': 'ERROR',
        'timestamp': '2024-01-15T11:15:00Z',
        'duration': '32s',
        'message': 'Database connection timeout during load phase',
        'error': 'psycopg2.OperationalError: timeout expired',
        'source': 'sales_api',
        'target': 'data_warehouse',
        'records_processed': 890,
        'log_level': 'ERROR'
    }
]

vector_db.add_pipeline_logs(sample_logs)

# Search for similar errors
similar_errors = vector_db.search_similar_errors(
    "Database connection failed during ETL process",
    n_results=3
)

for error in similar_errors:
    print(f"Distance: {error['distance']:.3f}")
    print(f"Pipeline: {error['metadata']['pipeline_name']}")
    print(f"Document: {error['document'][:200]}...")
    print("---")
```

### FAISS Implementation

```python
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import json
from typing import List, Dict, Any, Tuple

class FAISSDataCatalog:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize FAISS-based data catalog with sentence transformers."""
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
        self.documents = []
        self.metadata = []
    
    def add_documents(self, docs: List[str], meta: List[Dict[str, Any]]):
        """Add documents to the FAISS index."""
        # Generate embeddings
        embeddings = self.model.encode(docs, convert_to_tensor=False)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add to index
        self.index.add(embeddings.astype(np.float32))
        
        # Store documents and metadata
        self.documents.extend(docs)
        self.metadata.extend(meta)
    
    def search(self, query: str, k: int = 5) -> List[Tuple[str, Dict, float]]:
        """Search for similar documents."""
        # Encode query
        query_embedding = self.model.encode([query], convert_to_tensor=False)
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype(np.float32), k)
        
        # Return results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents):  # Valid index
                results.append((
                    self.documents[idx],
                    self.metadata[idx],
                    float(score)
                ))
        
        return results
    
    def save_index(self, filepath: str):
        """Save the FAISS index and associated data."""
        # Save FAISS index
        faiss.write_index(self.index, f"{filepath}.index")
        
        # Save documents and metadata
        with open(f"{filepath}.pkl", 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'metadata': self.metadata
            }, f)
    
    def load_index(self, filepath: str):
        """Load the FAISS index and associated data."""
        # Load FAISS index
        self.index = faiss.read_index(f"{filepath}.index")
        
        # Load documents and metadata
        with open(f"{filepath}.pkl", 'rb') as f:
            data = pickle.load(f)
            self.documents = data['documents']
            self.metadata = data['metadata']


# Usage Example
faiss_catalog = FAISSDataCatalog()

# Prepare data catalog documents
catalog_docs = [
    "Table: customers - Contains customer information including email, name, and registration date",
    "Table: orders - Order transaction data with customer_id, total amount, and order timestamp",
    "Table: products - Product catalog with SKU, name, description, and pricing information",
    "Pipeline: customer_etl - Daily ETL job that extracts customer data from CRM and loads to warehouse",
    "Pipeline: sales_reporting - Hourly aggregation of sales data for business intelligence dashboards"
]

catalog_metadata = [
    {"type": "table", "name": "customers", "database": "production"},
    {"type": "table", "name": "orders", "database": "production"},
    {"type": "table", "name": "products", "database": "production"},
    {"type": "pipeline", "name": "customer_etl", "schedule": "daily"},
    {"type": "pipeline", "name": "sales_reporting", "schedule": "hourly"}
]

# Add to index
faiss_catalog.add_documents(catalog_docs, catalog_metadata)

# Search
results = faiss_catalog.search("Where can I find customer purchase history?", k=3)
for doc, meta, score in results:
    print(f"Score: {score:.3f}")
    print(f"Type: {meta['type']}, Name: {meta['name']}")
    print(f"Document: {doc}")
    print("---")
```

---

## AI Agents

### Autonomous Pipeline Monitoring Agent

```python
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PipelineStatus:
    pipeline_name: str
    status: str
    last_run: datetime
    duration: Optional[float]
    records_processed: Optional[int]
    error_message: Optional[str]
    metrics: Dict[str, Any]

@dataclass
class Alert:
    pipeline_name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    details: Dict[str, Any]

class PipelineMonitoringAgent:
    def __init__(self, 
                 llm_client,
                 monitoring_interval: int = 300,  # 5 minutes
                 vector_db: Optional[Any] = None):
        """Initialize the AI-powered pipeline monitoring agent."""
        self.llm_client = llm_client
        self.monitoring_interval = monitoring_interval
        self.vector_db = vector_db
        self.pipeline_configs = {}
        self.alert_history = []
        self.running = False
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def add_pipeline(self, 
                    pipeline_name: str, 
                    endpoint: str, 
                    expected_frequency: timedelta,
                    thresholds: Dict[str, Any]):
        """Add a pipeline to monitor."""
        self.pipeline_configs[pipeline_name] = {
            'endpoint': endpoint,
            'expected_frequency': expected_frequency,
            'thresholds': thresholds,
            'last_check': None
        }
    
    async def check_pipeline_status(self, pipeline_name: str) -> Optional[PipelineStatus]:
        """Check the status of a specific pipeline."""
        config = self.pipeline_configs.get(pipeline_name)
        if not config:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(config['endpoint']) as response:
                    if response.status == 200:
                        data = await response.json()
                        return PipelineStatus(
                            pipeline_name=pipeline_name,
                            status=data.get('status', 'unknown'),
                            last_run=datetime.fromisoformat(data.get('last_run', datetime.now().isoformat())),
                            duration=data.get('duration'),
                            records_processed=data.get('records_processed'),
                            error_message=data.get('error_message'),
                            metrics=data.get('metrics', {})
                        )
        except Exception as e:
            self.logger.error(f"Failed to check pipeline {pipeline_name}: {e}")
            return PipelineStatus(
                pipeline_name=pipeline_name,
                status='error',
                last_run=datetime.now(),
                duration=None,
                records_processed=None,
                error_message=str(e),
                metrics={}
            )
    
    def analyze_pipeline_health(self, status: PipelineStatus) -> List[Alert]:
        """Use AI to analyze pipeline health and generate alerts."""
        config = self.pipeline_configs[status.pipeline_name]
        alerts = []
        
        # Check basic thresholds
        if status.status == 'failed':
            alerts.append(Alert(
                pipeline_name=status.pipeline_name,
                severity=AlertSeverity.HIGH,
                message=f"Pipeline failed: {status.error_message}",
                timestamp=datetime.now(),
                details={'error': status.error_message}
            ))
        
        # Check frequency
        expected_freq = config['expected_frequency']
        time_since_last_run = datetime.now() - status.last_run
        if time_since_last_run > expected_freq * 1.5:  # 50% tolerance
            alerts.append(Alert(
                pipeline_name=status.pipeline_name,
                severity=AlertSeverity.MEDIUM,
                message=f"Pipeline overdue by {time_since_last_run - expected_freq}",
                timestamp=datetime.now(),
                details={'expected_frequency': str(expected_freq), 'actual_delay': str(time_since_last_run)}
            ))
        
        # AI-powered analysis
        if status.error_message or alerts:
            ai_analysis = self._get_ai_insights(status, alerts)
            if ai_analysis:
                alerts.append(Alert(
                    pipeline_name=status.pipeline_name,
                    severity=AlertSeverity.LOW,
                    message=f"AI Analysis: {ai_analysis}",
                    timestamp=datetime.now(),
                    details={'ai_analysis': ai_analysis}
                ))
        
        return alerts
    
    def _get_ai_insights(self, status: PipelineStatus, existing_alerts: List[Alert]) -> Optional[str]:
        """Get AI insights about pipeline issues."""
        # Prepare context for AI analysis
        context = {
            'pipeline_name': status.pipeline_name,
            'status': status.status,
            'error_message': status.error_message,
            'duration': status.duration,
            'records_processed': status.records_processed,
            'alerts': [{'severity': alert.severity.value, 'message': alert.message} for alert in existing_alerts]
        }
        
        # Search for similar issues if vector DB is available
        similar_issues = []
        if self.vector_db and status.error_message:
            try:
                similar_issues = self.vector_db.search_similar_errors(status.error_message, n_results=3)
            except Exception as e:
                self.logger.warning(f"Failed to search similar issues: {e}")
        
        prompt = f"""
        Analyze the following pipeline status and provide insights:
        
        Pipeline Status:
        {json.dumps(context, indent=2)}
        
        Similar Historical Issues:
        {json.dumps([issue['document'][:200] for issue in similar_issues], indent=2) if similar_issues else "No similar issues found"}
        
        Please provide:
        1. Root cause analysis (if error present)
        2. Recommended immediate actions
        3. Prevention strategies
        4. Monitoring improvements
        
        Keep the response concise and actionable.
        """
        
        try:
            if hasattr(self.llm_client, 'query_ollama'):
                return self.llm_client.query_ollama(prompt, model="codellama")
            else:
                response = self.llm_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert data engineer analyzing pipeline issues."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=500
                )
                return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Failed to get AI insights: {e}")
            return None
    
    async def send_alerts(self, alerts: List[Alert]):
        """Send alerts via configured channels."""
        for alert in alerts:
            self.logger.info(f"ALERT [{alert.severity.value.upper()}] {alert.pipeline_name}: {alert.message}")
            
            # Here you would integrate with your alerting system
            # Examples: Slack, PagerDuty, email, etc.
            await self._send_to_slack(alert)
    
    async def _send_to_slack(self, alert: Alert):
        """Send alert to Slack (example implementation)."""
        # This is a placeholder - implement actual Slack integration
        webhook_url = "YOUR_SLACK_WEBHOOK_URL"
        
        color_map = {
            AlertSeverity.LOW: "good",
            AlertSeverity.MEDIUM: "warning", 
            AlertSeverity.HIGH: "danger",
            AlertSeverity.CRITICAL: "danger"
        }
        
        payload = {
            "attachments": [
                {
                    "color": color_map[alert.severity],
                    "title": f"Pipeline Alert: {alert.pipeline_name}",
                    "text": alert.message,
                    "fields": [
                        {
                            "title": "Severity",
                            "value": alert.severity.value.upper(),
                            "short": True
                        },
                        {
                            "title": "Timestamp",
                            "value": alert.timestamp.isoformat(),
                            "short": True
                        }
                    ]
                }
            ]
        }
        
        # Implement actual HTTP request to Slack webhook
        # async with aiohttp.ClientSession() as session:
        #     await session.post(webhook_url, json=payload)
    
    async def monitoring_loop(self):
        """Main monitoring loop."""
        self.running = True
        self.logger.info("Pipeline monitoring agent started")
        
        while self.running:
            try:
                for pipeline_name in self.pipeline_configs:
                    status = await self.check_pipeline_status(pipeline_name)
                    if status:
                        alerts = self.analyze_pipeline_health(status)
                        if alerts:
                            await self.send_alerts(alerts)
                            self.alert_history.extend(alerts)
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    def start_monitoring(self):
        """Start the monitoring agent."""
        asyncio.run(self.monitoring_loop())
    
    def stop_monitoring(self):
        """Stop the monitoring agent."""
        self.running = False


# Usage Example
async def main():
    # Initialize with Ollama client (using existing pattern from the repo)
    from your_llm_client import OllamaDataEngineer  # Use the class from earlier examples
    
    llm_client = OllamaDataEngineer()
    
    # Initialize vector database for similar issue search
    from your_vector_db import DataEngineeringVectorDB
    vector_db = DataEngineeringVectorDB()
    
    # Create monitoring agent
    agent = PipelineMonitoringAgent(
        llm_client=llm_client,
        monitoring_interval=300,  # 5 minutes
        vector_db=vector_db
    )
    
    # Add pipelines to monitor
    agent.add_pipeline(
        pipeline_name="customer_etl",
        endpoint="http://airflow:8080/api/v1/dags/customer_etl/dagRuns",
        expected_frequency=timedelta(hours=24),
        thresholds={
            'max_duration': 3600,  # 1 hour
            'min_records': 1000
        }
    )
    
    agent.add_pipeline(
        pipeline_name="sales_reporting",
        endpoint="http://airflow:8080/api/v1/dags/sales_reporting/dagRuns",
        expected_frequency=timedelta(hours=1),
        thresholds={
            'max_duration': 600,  # 10 minutes
            'min_records': 100
        }
    )
    
    # Start monitoring
    await agent.monitoring_loop()

# Run the agent
# asyncio.run(main())
```

---

## Practical Examples

### End-to-End AI-Powered ETL Pipeline

```python
import pandas as pd
import sqlalchemy
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import json

class AIEnhancedETLPipeline:
    """ETL Pipeline enhanced with AI capabilities."""
    
    def __init__(self, llm_client, source_config: Dict, target_config: Dict):
        self.llm_client = llm_client
        self.source_config = source_config
        self.target_config = target_config
        self.logger = logging.getLogger(__name__)
        
        # Setup database connections
        self.source_engine = sqlalchemy.create_engine(source_config['connection_string'])
        self.target_engine = sqlalchemy.create_engine(target_config['connection_string'])
    
    def extract_with_ai_validation(self, query: str) -> pd.DataFrame:
        """Extract data with AI-powered validation."""
        self.logger.info("Starting extraction phase")
        
        # Execute extraction query
        df = pd.read_sql(query, self.source_engine)
        
        # AI-powered data validation
        validation_report = self._validate_data_with_ai(df)
        self.logger.info(f"Data validation report: {validation_report}")
        
        # Log data quality metrics
        self.logger.info(f"Extracted {len(df)} records with {df.shape[1]} columns")
        
        return df
    
    def transform_with_ai_suggestions(self, df: pd.DataFrame, transformation_rules: List[str]) -> pd.DataFrame:
        """Transform data with AI-suggested optimizations."""
        self.logger.info("Starting transformation phase")
        
        # Apply basic transformation rules
        for rule in transformation_rules:
            df = self._apply_transformation_rule(df, rule)
        
        # Get AI suggestions for additional transformations
        ai_suggestions = self._get_ai_transformation_suggestions(df)
        self.logger.info(f"AI transformation suggestions: {ai_suggestions}")
        
        # Apply AI-suggested transformations (with user approval in production)
        # For demo purposes, we'll just log them
        
        return df
    
    def load_with_ai_monitoring(self, df: pd.DataFrame, table_name: str) -> Dict[str, Any]:
        """Load data with AI-powered monitoring."""
        self.logger.info("Starting load phase")
        
        start_time = datetime.now()
        
        try:
            # Load data
            df.to_sql(table_name, self.target_engine, if_exists='replace', index=False)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Gather load metrics
            load_metrics = {
                'records_loaded': len(df),
                'duration_seconds': duration,
                'records_per_second': len(df) / duration if duration > 0 else 0,
                'success': True,
                'timestamp': end_time.isoformat()
            }
            
            # AI-powered load analysis
            load_analysis = self._analyze_load_performance(load_metrics)
            self.logger.info(f"Load performance analysis: {load_analysis}")
            
            return load_metrics
            
        except Exception as e:
            self.logger.error(f"Load failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _validate_data_with_ai(self, df: pd.DataFrame) -> str:
        """Use AI to validate extracted data."""
        # Prepare data summary for AI analysis
        data_summary = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.astype(str).to_dict(),
            'null_counts': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'memory_usage': df.memory_usage(deep=True).sum()
        }
        
        prompt = f"""
        Analyze the following dataset summary for potential data quality issues:
        
        {json.dumps(data_summary, indent=2)}
        
        Please identify:
        1. Data quality concerns
        2. Potential anomalies
        3. Recommendations for data cleaning
        4. Performance considerations
        
        Provide a concise summary focusing on the most critical issues.
        """
        
        try:
            if hasattr(self.llm_client, 'query_ollama'):
                return self.llm_client.query_ollama(prompt)
            else:
                response = self.llm_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a data quality expert."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"AI validation failed: {e}"
    
    def _get_ai_transformation_suggestions(self, df: pd.DataFrame) -> str:
        """Get AI suggestions for data transformations."""
        # Analyze data characteristics
        sample_data = df.head(5).to_dict()
        
        prompt = f"""
        Based on the following dataset sample, suggest optimal transformations:
        
        Sample Data:
        {json.dumps(sample_data, indent=2, default=str)}
        
        Data Types:
        {df.dtypes.astype(str).to_dict()}
        
        Please suggest:
        1. Data type optimizations
        2. Missing value handling strategies
        3. Outlier detection and treatment
        4. Feature engineering opportunities
        5. Performance optimizations
        
        Focus on practical, implementable suggestions.
        """
        
        try:
            if hasattr(self.llm_client, 'query_ollama'):
                return self.llm_client.query_ollama(prompt)
            else:
                response = self.llm_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a data transformation expert."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"AI suggestions failed: {e}"
    
    def _analyze_load_performance(self, metrics: Dict[str, Any]) -> str:
        """Analyze load performance using AI."""
        prompt = f"""
        Analyze the following ETL load performance metrics:
        
        {json.dumps(metrics, indent=2)}
        
        Please provide:
        1. Performance assessment (Good/Average/Poor)
        2. Bottleneck identification
        3. Optimization recommendations
        4. Scalability considerations
        
        Keep the analysis concise and actionable.
        """
        
        try:
            if hasattr(self.llm_client, 'query_ollama'):
                return self.llm_client.query_ollama(prompt)
            else:
                response = self.llm_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an ETL performance expert."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"Performance analysis failed: {e}"
    
    def _apply_transformation_rule(self, df: pd.DataFrame, rule: str) -> pd.DataFrame:
        """Apply a transformation rule to the dataframe."""
        # This is a simplified example - in practice, you'd have more sophisticated rule parsing
        if rule == "remove_duplicates":
            return df.drop_duplicates()
        elif rule == "fill_nulls_with_zero":
            return df.fillna(0)
        elif rule.startswith("drop_column:"):
            column = rule.split(":")[1]
            return df.drop(columns=[column], errors='ignore')
        else:
            self.logger.warning(f"Unknown transformation rule: {rule}")
            return df
    
    def run_pipeline(self, extraction_query: str, transformation_rules: List[str], target_table: str) -> Dict[str, Any]:
        """Run the complete AI-enhanced ETL pipeline."""
        pipeline_start = datetime.now()
        
        try:
            # Extract
            df = self.extract_with_ai_validation(extraction_query)
            
            # Transform
            df = self.transform_with_ai_suggestions(df, transformation_rules)
            
            # Load
            load_result = self.load_with_ai_monitoring(df, target_table)
            
            pipeline_end = datetime.now()
            total_duration = (pipeline_end - pipeline_start).total_seconds()
            
            return {
                'success': load_result.get('success', False),
                'total_duration': total_duration,
                'records_processed': len(df),
                'load_result': load_result,
                'timestamp': pipeline_end.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }


# Usage Example
def run_ai_etl_example():
    # Setup (using existing patterns from the repository)
    from your_llm_client import OllamaDataEngineer
    
    llm_client = OllamaDataEngineer()
    
    source_config = {
        'connection_string': 'postgresql://user:pass@source_db:5432/source'
    }
    
    target_config = {
        'connection_string': 'postgresql://user:pass@target_db:5432/warehouse'
    }
    
    # Create pipeline
    pipeline = AIEnhancedETLPipeline(llm_client, source_config, target_config)
    
    # Run pipeline
    result = pipeline.run_pipeline(
        extraction_query="SELECT * FROM customers WHERE created_at >= CURRENT_DATE - INTERVAL 30 DAY",
        transformation_rules=["remove_duplicates", "fill_nulls_with_zero"],
        target_table="recent_customers"
    )
    
    print(f"Pipeline result: {json.dumps(result, indent=2)}")

# Uncomment to run
# run_ai_etl_example()
```

---

## Use Case Mapping

| AI Feature | Data Engineering Use Cases | Tools/Libraries | Complexity | Impact |
|------------|---------------------------|-----------------|------------|---------|
| **LLMs for Code Generation** | SQL query generation, ETL script creation, documentation | OpenAI API, Codex, GitHub Copilot | Low-Medium | High |
| **Prompt Engineering** | Automated troubleshooting, code review, requirement analysis | Custom prompts, LangChain | Low | Medium |
| **RAG for Data Catalogs** | Semantic search over schemas, pipeline documentation | ChromaDB, FAISS, LangChain | Medium | High |
| **Vector Databases** | Similar error detection, schema matching, log analysis | ChromaDB, Pinecone, Weaviate | Medium | Medium |
| **AI Agents** | Pipeline monitoring, automated alerting, self-healing | LangChain Agents, Custom frameworks | High | Very High |
| **Anomaly Detection** | Data quality monitoring, pipeline performance | Isolation Forest, Autoencoders | Medium-High | High |
| **NLP for Logs** | Log analysis, error categorization, incident correlation | spaCy, NLTK, Transformers | Medium | Medium |
| **Automated Documentation** | Schema documentation, pipeline descriptions | LLMs + templating | Low | Medium |
| **Smart Scheduling** | Adaptive pipeline scheduling, resource optimization | Reinforcement Learning | High | Medium |
| **Data Lineage AI** | Automatic lineage detection, impact analysis | Graph Neural Networks | High | High |

### Detailed Use Case Examples

#### 1. ETL Pipeline Automation
- **Problem**: Manual ETL code creation is time-consuming and error-prone
- **AI Solution**: LLM-powered code generation from business requirements
- **Implementation**: Prompt engineering with schema context
- **Benefits**: 70% reduction in development time, consistent code quality

#### 2. Data Catalog Search
- **Problem**: Finding relevant tables/datasets in large organizations
- **AI Solution**: RAG-based semantic search over data catalogs
- **Implementation**: Vector embeddings of schema documentation
- **Benefits**: Improved data discovery, reduced time to insights

#### 3. Pipeline Monitoring
- **Problem**: Manual monitoring doesn't scale with pipeline growth
- **AI Solution**: Intelligent agents for autonomous monitoring
- **Implementation**: ML-based anomaly detection + LLM analysis
- **Benefits**: Proactive issue detection, reduced downtime

#### 4. Natural Language Querying
- **Problem**: Business users can't write SQL queries
- **AI Solution**: Text-to-SQL translation with context awareness
- **Implementation**: Fine-tuned models on company schema
- **Benefits**: Democratized data access, reduced analyst workload

---

## FAQ

### Getting Started

**Q: I'm new to AI in data engineering. Where should I start?**

A: Start with these steps:
1. Experiment with ChatGPT or GitHub Copilot for SQL/Python code generation
2. Learn basic prompt engineering techniques
3. Try the OpenAI API with simple data tasks
4. Build a small RAG system for your team's documentation
5. Gradually integrate AI into existing workflows

**Q: What's the minimum setup needed to try these examples?**

A: You need:
- Python 3.8+
- OpenAI API key OR local Ollama installation
- Basic libraries: `pandas`, `requests`, `chromadb`
- A sample database or CSV files for testing

**Q: Are there free alternatives to paid LLM APIs?**

A: Yes! Consider:
- **Ollama**: Run models locally (Llama, CodeLlama, Mistral)
- **Hugging Face Transformers**: Open-source models
- **Google Colab**: Free GPU access for experiments
- **Anthropic Claude**: Competitive API pricing

### Implementation

**Q: How do I handle sensitive data with AI tools?**

A: Follow these practices:
- Use local models (Ollama) for sensitive data
- Implement data anonymization before AI processing  
- Never send credentials or PII to external APIs
- Use encryption for data in transit and at rest
- Review AI provider's data handling policies

**Q: What are the performance considerations for RAG systems?**

A: Key factors:
- **Vector Database Choice**: ChromaDB for local, Pinecone for scale
- **Embedding Model**: Balance between speed and accuracy
- **Chunk Size**: 500-1000 tokens usually optimal
- **Index Type**: HNSW for speed, IVF for memory efficiency
- **Caching**: Cache embeddings and frequent queries

**Q: How accurate are AI-generated SQL queries?**

A: Accuracy depends on:
- **Schema Context**: More context = better results
- **Query Complexity**: Simple queries (90%+), complex joins (70-80%)
- **Model Quality**: GPT-4 > GPT-3.5 > CodeLlama
- **Prompt Engineering**: Good prompts improve accuracy significantly
- **Validation**: Always review and test generated queries

### Best Practices

**Q: How do I ensure AI-generated code is production-ready?**

A: Apply these practices:
- **Code Review**: Treat AI code like any other contribution
- **Testing**: Write comprehensive tests for AI-generated functions
- **Monitoring**: Track performance and accuracy metrics
- **Versioning**: Version control prompts and AI configurations
- **Fallbacks**: Have manual processes as backup

**Q: What metrics should I track for AI-enhanced pipelines?**

A: Monitor these metrics:
- **Accuracy**: Correctness of AI predictions/generations
- **Latency**: Response time for AI operations
- **Cost**: API usage and computational resources
- **Adoption**: Team usage and satisfaction metrics
- **Business Impact**: Time saved, errors reduced, productivity gains

**Q: How do I train my team on AI tools?**

A: Follow this approach:
1. **Start Simple**: Begin with code completion and SQL generation
2. **Hands-on Workshops**: Practice with real data engineering tasks
3. **Documentation**: Create internal guides and best practices
4. **Gradual Integration**: Introduce one AI tool at a time
5. **Feedback Loops**: Regular retrospectives and improvement cycles

### Troubleshooting

**Q: My RAG system returns irrelevant results. How do I fix it?**

A: Try these solutions:
- **Improve Chunking**: Adjust chunk size and overlap
- **Better Embeddings**: Use domain-specific embedding models
- **Query Preprocessing**: Clean and expand user queries
- **Metadata Filtering**: Use filters to narrow search scope
- **Hybrid Search**: Combine semantic and keyword search

**Q: AI-generated code has bugs. How do I improve quality?**

A: Implement these strategies:
- **Better Prompts**: Include more context and examples
- **Code Templates**: Use consistent structures and patterns
- **Static Analysis**: Run linters and type checkers
- **Incremental Generation**: Break complex code into smaller parts
- **Human Review**: Always have experienced developers review

**Q: How do I handle AI hallucinations in data engineering?**

A: Use these techniques:
- **Validation**: Verify AI outputs against known facts
- **Confidence Scores**: Use model confidence when available
- **Multiple Sources**: Cross-reference information
- **Human Oversight**: Maintain human involvement in critical decisions
- **Feedback Loops**: Correct and retrain on mistakes

### Advanced Topics

**Q: Can I fine-tune models for specific data engineering tasks?**

A: Yes, consider fine-tuning for:
- **Text-to-SQL**: Company-specific schemas and query patterns
- **Log Analysis**: Domain-specific error patterns
- **Code Generation**: Internal coding standards and frameworks
- **Documentation**: Company writing style and terminology

Fine-tuning requirements:
- Quality training data (1000+ examples)
- Computing resources (GPU access)
- MLOps infrastructure for model management
- Evaluation metrics and testing procedures

**Q: How do I scale AI features across multiple teams?**

A: Follow these strategies:
- **Centralized Platform**: Build shared AI services and APIs
- **Standard Templates**: Create reusable prompt templates
- **Self-Service Tools**: Enable teams to customize without coding
- **Governance**: Establish AI usage policies and guidelines
- **Cost Management**: Monitor and optimize API usage across teams

---

## Conclusion

AI is transforming data engineering by automating routine tasks, enhancing decision-making, and enabling new capabilities. The key to success is starting small, focusing on high-impact use cases, and gradually building expertise.

**Next Steps:**
1. Choose one use case from this guide to pilot
2. Start with existing tools (ChatGPT, GitHub Copilot)
3. Build internal knowledge and expertise
4. Scale successful implementations across teams
5. Stay updated with the rapidly evolving AI landscape

**Resources for Continued Learning:**
- [OpenAI Cookbook](https://github.com/openai/openai-cookbook)
- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Tutorials](https://docs.trychroma.com/)
- [Hugging Face Course](https://huggingface.co/course)
- [Papers with Code - NLP](https://paperswithcode.com/area/natural-language-processing)

Remember: AI augments human expertise rather than replacing it. The most successful implementations combine AI capabilities with domain knowledge and engineering best practices.