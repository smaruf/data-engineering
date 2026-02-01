"""
Azure Functions Example

This module demonstrates Azure Functions code examples for serverless computing.
Covers HTTP triggers, Timer triggers, and blob triggers.

Requirements:
    pip install azure-functions

Note:
    This file contains example function code. To deploy:
    1. Install Azure Functions Core Tools
    2. Create a function app: func init --python
    3. Create functions: func new --name MyFunction --template "HTTP trigger"
    4. Deploy: func azure functionapp publish <APP_NAME>
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict
import azure.functions as func

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# HTTP Trigger Function
# ============================================================================

def http_trigger_example(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP trigger function example.
    
    Triggered by HTTP requests. Useful for building REST APIs.
    
    Args:
        req: HTTP request object
    
    Returns:
        HTTP response object
    
    Usage:
        POST https://your-function-app.azurewebsites.net/api/http_trigger_example
        Body: {"name": "John", "age": 30}
    """
    logger.info('HTTP trigger function processing request')
    
    try:
        # Get request body
        req_body = req.get_json()
        name = req_body.get('name')
        age = req_body.get('age')
        
        if name:
            response_data = {
                'message': f'Hello, {name}!',
                'age': age,
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'success'
            }
            
            return func.HttpResponse(
                body=json.dumps(response_data),
                mimetype='application/json',
                status_code=200
            )
        else:
            return func.HttpResponse(
                body=json.dumps({
                    'error': 'Please provide a name in the request body',
                    'status': 'error'
                }),
                mimetype='application/json',
                status_code=400
            )
            
    except ValueError:
        return func.HttpResponse(
            body=json.dumps({
                'error': 'Invalid JSON in request body',
                'status': 'error'
            }),
            mimetype='application/json',
            status_code=400
        )
    except Exception as e:
        logger.error(f'Error processing request: {e}')
        return func.HttpResponse(
            body=json.dumps({
                'error': str(e),
                'status': 'error'
            }),
            mimetype='application/json',
            status_code=500
        )


# ============================================================================
# Timer Trigger Function
# ============================================================================

def timer_trigger_example(timer: func.TimerRequest) -> None:
    """
    Timer trigger function example.
    
    Triggered on a schedule using cron expressions.
    Useful for scheduled tasks like data processing, cleanup, monitoring.
    
    Args:
        timer: Timer request object
    
    Schedule Examples:
        - "0 */5 * * * *" : Every 5 minutes
        - "0 0 * * * *"   : Every hour
        - "0 0 9 * * *"   : Every day at 9:00 AM
        - "0 0 0 * * MON" : Every Monday at midnight
    
    function.json configuration:
    {
        "schedule": "0 */5 * * * *",
        "runOnStartup": false,
        "useMonitor": true
    }
    """
    logger.info('Timer trigger function executed')
    
    if timer.past_due:
        logger.warning('Timer is past due!')
    
    current_time = datetime.utcnow().isoformat()
    
    # Example: Perform scheduled data processing
    logger.info(f'Processing scheduled task at {current_time}')
    
    # Simulated work
    processed_records = process_scheduled_data()
    
    logger.info(f'Processed {processed_records} records')
    logger.info('Timer trigger function completed')


def process_scheduled_data() -> int:
    """
    Simulate scheduled data processing.
    
    Returns:
        Number of records processed
    """
    # In a real scenario, this would:
    # - Connect to a database
    # - Process pending records
    # - Update status
    # - Send notifications
    
    logger.info('Processing data...')
    
    # Simulated processing
    records = [
        {'id': 1, 'status': 'pending'},
        {'id': 2, 'status': 'pending'},
        {'id': 3, 'status': 'pending'}
    ]
    
    for record in records:
        logger.info(f"Processing record {record['id']}")
        record['status'] = 'completed'
        record['processed_at'] = datetime.utcnow().isoformat()
    
    return len(records)


# ============================================================================
# Blob Trigger Function
# ============================================================================

def blob_trigger_example(blob: func.InputStream) -> None:
    """
    Blob trigger function example.
    
    Triggered when a blob is created or updated in Azure Storage.
    Useful for processing uploaded files, ETL pipelines, image processing.
    
    Args:
        blob: Input stream of the blob
    
    function.json configuration:
    {
        "type": "blobTrigger",
        "direction": "in",
        "name": "blob",
        "path": "samples-workitems/{name}",
        "connection": "AzureWebJobsStorage"
    }
    """
    logger.info(
        f'Blob trigger function processing blob\n'
        f'Name: {blob.name}\n'
        f'Size: {blob.length} bytes'
    )
    
    try:
        # Read blob content
        content = blob.read()
        
        # Process based on file type
        if blob.name.endswith('.json'):
            process_json_blob(content)
        elif blob.name.endswith('.csv'):
            process_csv_blob(content)
        elif blob.name.endswith('.txt'):
            process_text_blob(content)
        else:
            logger.warning(f'Unsupported file type: {blob.name}')
        
        logger.info('Blob processing completed successfully')
        
    except Exception as e:
        logger.error(f'Error processing blob: {e}')
        raise


def process_json_blob(content: bytes) -> None:
    """Process JSON blob content."""
    try:
        data = json.loads(content.decode('utf-8'))
        logger.info(f'Processed JSON with {len(data)} items')
        
        # Example: Validate and transform data
        for item in data if isinstance(data, list) else [data]:
            logger.debug(f'Processing item: {item}')
            
    except json.JSONDecodeError as e:
        logger.error(f'Invalid JSON: {e}')
        raise


def process_csv_blob(content: bytes) -> None:
    """Process CSV blob content."""
    import csv
    import io
    
    try:
        text_content = content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(text_content))
        
        rows = list(csv_reader)
        logger.info(f'Processed CSV with {len(rows)} rows')
        
        # Example: Process each row
        for row in rows:
            logger.debug(f'Processing row: {row}')
            
    except Exception as e:
        logger.error(f'Error processing CSV: {e}')
        raise


def process_text_blob(content: bytes) -> None:
    """Process text blob content."""
    try:
        text = content.decode('utf-8')
        lines = text.split('\n')
        word_count = len(text.split())
        
        logger.info(f'Processed text: {len(lines)} lines, {word_count} words')
        
    except Exception as e:
        logger.error(f'Error processing text: {e}')
        raise


# ============================================================================
# Queue Trigger Function
# ============================================================================

def queue_trigger_example(msg: func.QueueMessage) -> None:
    """
    Queue trigger function example.
    
    Triggered when a message is added to Azure Queue Storage.
    Useful for async task processing, work distribution, decoupling systems.
    
    Args:
        msg: Queue message object
    
    function.json configuration:
    {
        "type": "queueTrigger",
        "direction": "in",
        "name": "msg",
        "queueName": "myqueue-items",
        "connection": "AzureWebJobsStorage"
    }
    """
    logger.info(
        f'Queue trigger function processing message\n'
        f'Message ID: {msg.id}\n'
        f'Dequeue Count: {msg.dequeue_count}'
    )
    
    try:
        # Parse message content
        message_content = msg.get_body().decode('utf-8')
        logger.info(f'Message content: {message_content}')
        
        # Try to parse as JSON
        try:
            data = json.loads(message_content)
            process_queue_message(data)
        except json.JSONDecodeError:
            # Process as plain text
            logger.info(f'Processing plain text message: {message_content}')
        
        logger.info('Queue message processed successfully')
        
    except Exception as e:
        logger.error(f'Error processing queue message: {e}')
        
        # If dequeue count is high, the message has failed multiple times
        if msg.dequeue_count > 5:
            logger.error(f'Message failed {msg.dequeue_count} times, moving to poison queue')
        
        raise


def process_queue_message(data: Dict[str, Any]) -> None:
    """
    Process queue message data.
    
    Args:
        data: Parsed message data
    """
    logger.info(f'Processing queue message: {data}')
    
    # Example: Process different message types
    message_type = data.get('type')
    
    if message_type == 'email':
        send_email_notification(data)
    elif message_type == 'data_processing':
        process_data_task(data)
    else:
        logger.warning(f'Unknown message type: {message_type}')


def send_email_notification(data: Dict[str, Any]) -> None:
    """Simulate sending email notification."""
    logger.info(f"Sending email to: {data.get('recipient')}")
    logger.info(f"Subject: {data.get('subject')}")


def process_data_task(data: Dict[str, Any]) -> None:
    """Simulate data processing task."""
    logger.info(f"Processing data task: {data.get('task_id')}")
    logger.info(f"Data: {data.get('data')}")


# ============================================================================
# Durable Functions Example (Orchestrator)
# ============================================================================

def orchestrator_example(context) -> list:
    """
    Durable Functions orchestrator example.
    
    Orchestrates long-running workflows with multiple activities.
    Useful for complex workflows, human interaction, monitoring.
    
    Args:
        context: Durable orchestration context
    
    Returns:
        List of activity results
    
    Note:
        Requires azure-functions-durable package
    """
    # Example workflow:
    # 1. Get input data
    # 2. Parallel processing
    # 3. Aggregate results
    
    input_data = context.get_input()
    
    # Start parallel activities
    parallel_tasks = []
    for item in input_data:
        parallel_tasks.append(
            context.call_activity('ProcessItem', item)
        )
    
    # Wait for all to complete
    results = []
    for task in parallel_tasks:
        result = task  # In real code: yield task
        results.append(result)
    
    # Aggregate results
    final_result = {
        'total_processed': len(results),
        'results': results,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    return final_result


# ============================================================================
# Main - Example Usage
# ============================================================================

def main():
    """
    Example demonstrating how to test functions locally.
    
    Note: This is for illustration. Real Azure Functions are invoked
    by Azure Functions runtime, not by calling main().
    """
    logger.info("=" * 60)
    logger.info("Azure Functions Examples")
    logger.info("=" * 60)
    
    # Example: Simulate HTTP trigger
    logger.info("\n--- HTTP Trigger Example ---")
    logger.info("In production, this would be called via HTTP endpoint:")
    logger.info("POST https://your-app.azurewebsites.net/api/http_trigger_example")
    
    # Example: Simulate Timer trigger
    logger.info("\n--- Timer Trigger Example ---")
    logger.info("In production, this would run on schedule (e.g., every 5 minutes)")
    logger.info("Schedule: 0 */5 * * * *")
    
    # Example: Simulate Blob trigger
    logger.info("\n--- Blob Trigger Example ---")
    logger.info("In production, this would trigger when files are uploaded to blob storage")
    logger.info("Path: samples-workitems/{name}")
    
    logger.info("\n" + "=" * 60)
    logger.info("Deploy these functions using Azure Functions Core Tools")
    logger.info("=" * 60)
    
    logger.info("\nDeployment steps:")
    logger.info("1. func init MyFunctionApp --python")
    logger.info("2. cd MyFunctionApp")
    logger.info("3. func new --name HttpTrigger --template 'HTTP trigger'")
    logger.info("4. func start  # Test locally")
    logger.info("5. func azure functionapp publish <APP_NAME>")


if __name__ == "__main__":
    main()
