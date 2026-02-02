"""
Azure Batch Processing Example

This module demonstrates using Azure Batch for large-scale parallel processing.
Covers pool creation, job submission, and task management.

Requirements:
    pip install azure-batch azure-identity azure-mgmt-batch

Environment Variables:
    AZURE_BATCH_ACCOUNT_NAME: Batch account name
    AZURE_BATCH_ACCOUNT_URL: Batch account URL
    AZURE_BATCH_ACCOUNT_KEY: Batch account key
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from azure.batch import BatchServiceClient
from azure.batch.batch_auth import SharedKeyCredentials
from azure.batch import models as batch_models
from azure.core.exceptions import AzureError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AzureBatchManager:
    """
    Manages Azure Batch operations for parallel processing.
    
    Azure Batch enables large-scale parallel and high-performance computing (HPC)
    applications efficiently in Azure.
    """
    
    def __init__(
        self,
        account_name: Optional[str] = None,
        account_url: Optional[str] = None,
        account_key: Optional[str] = None
    ):
        """
        Initialize Azure Batch manager.
        
        Args:
            account_name: Batch account name
            account_url: Batch account URL
            account_key: Batch account key
        """
        self.account_name = account_name or os.getenv('AZURE_BATCH_ACCOUNT_NAME')
        self.account_url = account_url or os.getenv('AZURE_BATCH_ACCOUNT_URL')
        account_key = account_key or os.getenv('AZURE_BATCH_ACCOUNT_KEY')
        
        if not all([self.account_name, self.account_url, account_key]):
            raise ValueError(
                "Batch account details required. Set environment variables: "
                "AZURE_BATCH_ACCOUNT_NAME, AZURE_BATCH_ACCOUNT_URL, AZURE_BATCH_ACCOUNT_KEY"
            )
        
        # Create credentials and client
        credentials = SharedKeyCredentials(self.account_name, account_key)
        self.batch_client = BatchServiceClient(credentials, batch_url=self.account_url)
        
        logger.info(f"Initialized Batch client for account: {self.account_name}")
    
    def create_pool(
        self,
        pool_id: str,
        vm_size: str = "STANDARD_D2_V2",
        node_count: int = 2,
        vm_image_publisher: str = "Canonical",
        vm_image_offer: str = "UbuntuServer",
        vm_image_sku: str = "18.04-LTS",
        enable_auto_scale: bool = False,
        auto_scale_formula: Optional[str] = None
    ) -> None:
        """
        Create a compute pool.
        
        Args:
            pool_id: Unique pool identifier
            vm_size: VM size (e.g., STANDARD_D2_V2)
            node_count: Number of compute nodes
            vm_image_publisher: VM image publisher
            vm_image_offer: VM image offer
            vm_image_sku: VM image SKU
            enable_auto_scale: Enable autoscaling
            auto_scale_formula: Autoscale formula (if autoscaling enabled)
        """
        try:
            logger.info(f"Creating pool: {pool_id}")
            
            # Check if pool already exists
            if self._pool_exists(pool_id):
                logger.warning(f"Pool {pool_id} already exists")
                return
            
            # Configure VM image
            image_ref = batch_models.ImageReference(
                publisher=vm_image_publisher,
                offer=vm_image_offer,
                sku=vm_image_sku
            )
            
            # Configure VM configuration
            vm_config = batch_models.VirtualMachineConfiguration(
                image_reference=image_ref,
                node_agent_sku_id="batch.node.ubuntu 18.04"
            )
            
            # Create pool configuration
            pool = batch_models.PoolAddParameter(
                id=pool_id,
                virtual_machine_configuration=vm_config,
                vm_size=vm_size,
                target_dedicated_nodes=node_count if not enable_auto_scale else None,
                enable_auto_scale=enable_auto_scale,
                auto_scale_formula=auto_scale_formula if enable_auto_scale else None
            )
            
            # Create pool
            self.batch_client.pool.add(pool)
            
            logger.info(f"Pool created: {pool_id} with {node_count} nodes of size {vm_size}")
            
        except batch_models.BatchErrorException as e:
            logger.error(f"Failed to create pool: {e.message}")
            raise
    
    def create_job(
        self,
        job_id: str,
        pool_id: str
    ) -> None:
        """
        Create a job in a pool.
        
        Args:
            job_id: Unique job identifier
            pool_id: Pool to run the job in
        """
        try:
            logger.info(f"Creating job: {job_id}")
            
            # Create job
            job = batch_models.JobAddParameter(
                id=job_id,
                pool_info=batch_models.PoolInformation(pool_id=pool_id)
            )
            
            self.batch_client.job.add(job)
            
            logger.info(f"Job created: {job_id} in pool {pool_id}")
            
        except batch_models.BatchErrorException as e:
            logger.error(f"Failed to create job: {e.message}")
            raise
    
    def add_tasks(
        self,
        job_id: str,
        tasks: List[Dict[str, Any]]
    ) -> None:
        """
        Add tasks to a job.
        
        Args:
            job_id: Job identifier
            tasks: List of task definitions
        
        Example:
            tasks = [
                {
                    "id": "task1",
                    "command": "echo 'Processing file 1'",
                    "resource_files": []
                },
                {
                    "id": "task2",
                    "command": "python process.py --input file2.txt",
                    "resource_files": [...]
                }
            ]
        """
        try:
            logger.info(f"Adding {len(tasks)} tasks to job: {job_id}")
            
            batch_tasks = []
            for task_def in tasks:
                task = batch_models.TaskAddParameter(
                    id=task_def['id'],
                    command_line=task_def['command'],
                    resource_files=task_def.get('resource_files', [])
                )
                batch_tasks.append(task)
            
            # Add tasks in batch
            self.batch_client.task.add_collection(job_id, batch_tasks)
            
            logger.info(f"Added {len(tasks)} tasks to job: {job_id}")
            
        except batch_models.BatchErrorException as e:
            logger.error(f"Failed to add tasks: {e.message}")
            raise
    
    def monitor_tasks(
        self,
        job_id: str,
        timeout_minutes: int = 30
    ) -> Dict[str, int]:
        """
        Monitor task progress and wait for completion.
        
        Args:
            job_id: Job identifier
            timeout_minutes: Maximum time to wait
        
        Returns:
            Dictionary with task status counts
        """
        try:
            logger.info(f"Monitoring tasks for job: {job_id}")
            
            timeout = timedelta(minutes=timeout_minutes)
            timeout_expiration = datetime.now() + timeout
            
            while datetime.now() < timeout_expiration:
                tasks = self.batch_client.task.list(job_id)
                
                # Count task states
                incomplete_tasks = 0
                completed_tasks = 0
                failed_tasks = 0
                
                for task in tasks:
                    if task.state == batch_models.TaskState.completed:
                        if task.execution_info.exit_code == 0:
                            completed_tasks += 1
                        else:
                            failed_tasks += 1
                    else:
                        incomplete_tasks += 1
                
                logger.info(
                    f"Tasks - Completed: {completed_tasks}, "
                    f"Failed: {failed_tasks}, "
                    f"Incomplete: {incomplete_tasks}"
                )
                
                if incomplete_tasks == 0:
                    logger.info("All tasks completed")
                    return {
                        'completed': completed_tasks,
                        'failed': failed_tasks,
                        'total': completed_tasks + failed_tasks
                    }
                
                # Wait before next check
                import time
                time.sleep(10)
            
            logger.warning(f"Timeout reached after {timeout_minutes} minutes")
            return {
                'completed': completed_tasks,
                'failed': failed_tasks,
                'incomplete': incomplete_tasks,
                'total': completed_tasks + failed_tasks + incomplete_tasks
            }
            
        except batch_models.BatchErrorException as e:
            logger.error(f"Failed to monitor tasks: {e.message}")
            raise
    
    def get_task_output(
        self,
        job_id: str,
        task_id: str
    ) -> Optional[str]:
        """
        Get task output.
        
        Args:
            job_id: Job identifier
            task_id: Task identifier
        
        Returns:
            Task output as string
        """
        try:
            logger.info(f"Getting output for task: {task_id}")
            
            # Get task
            task = self.batch_client.task.get(job_id, task_id)
            
            # Check if completed
            if task.state != batch_models.TaskState.completed:
                logger.warning(f"Task {task_id} has not completed yet")
                return None
            
            # Get stdout
            stream = self.batch_client.file.get_from_task(
                job_id,
                task_id,
                'stdout.txt'
            )
            
            output = stream.content.decode('utf-8')
            logger.info(f"Retrieved output ({len(output)} bytes)")
            
            return output
            
        except batch_models.BatchErrorException as e:
            logger.error(f"Failed to get task output: {e.message}")
            return None
    
    def delete_job(self, job_id: str) -> None:
        """
        Delete a job.
        
        Args:
            job_id: Job identifier
        """
        try:
            logger.info(f"Deleting job: {job_id}")
            self.batch_client.job.delete(job_id)
            logger.info(f"Job deleted: {job_id}")
            
        except batch_models.BatchErrorException as e:
            logger.error(f"Failed to delete job: {e.message}")
            raise
    
    def delete_pool(self, pool_id: str) -> None:
        """
        Delete a pool.
        
        Args:
            pool_id: Pool identifier
        """
        try:
            logger.warning(f"Deleting pool: {pool_id}")
            self.batch_client.pool.delete(pool_id)
            logger.info(f"Pool deleted: {pool_id}")
            
        except batch_models.BatchErrorException as e:
            logger.error(f"Failed to delete pool: {e.message}")
            raise
    
    def _pool_exists(self, pool_id: str) -> bool:
        """Check if a pool exists."""
        try:
            self.batch_client.pool.get(pool_id)
            return True
        except batch_models.BatchErrorException:
            return False
    
    def list_pools(self) -> List[str]:
        """
        List all pools.
        
        Returns:
            List of pool IDs
        """
        try:
            pools = self.batch_client.pool.list()
            pool_ids = [pool.id for pool in pools]
            logger.info(f"Found {len(pool_ids)} pools")
            return pool_ids
            
        except batch_models.BatchErrorException as e:
            logger.error(f"Failed to list pools: {e.message}")
            raise
    
    def list_jobs(self) -> List[str]:
        """
        List all jobs.
        
        Returns:
            List of job IDs
        """
        try:
            jobs = self.batch_client.job.list()
            job_ids = [job.id for job in jobs]
            logger.info(f"Found {len(job_ids)} jobs")
            return job_ids
            
        except batch_models.BatchErrorException as e:
            logger.error(f"Failed to list jobs: {e.message}")
            raise


def main():
    """
    Main function demonstrating Azure Batch operations.
    """
    try:
        logger.info("=" * 60)
        logger.info("Azure Batch Example")
        logger.info("=" * 60)
        
        # Initialize manager
        batch_manager = AzureBatchManager(
            # account_name="mybatchaccount",
            # account_url="https://mybatchaccount.region.batch.azure.com",
            # account_key="your-account-key"
        )
        
        pool_id = "demo-pool"
        job_id = "demo-job"
        
        # Create pool
        logger.info("\n--- Creating Pool ---")
        batch_manager.create_pool(
            pool_id=pool_id,
            vm_size="STANDARD_D2_V2",
            node_count=2
        )
        
        # Create job
        logger.info("\n--- Creating Job ---")
        batch_manager.create_job(job_id, pool_id)
        
        # Add tasks
        logger.info("\n--- Adding Tasks ---")
        tasks = [
            {
                "id": f"task{i}",
                "command": f"echo 'Processing task {i}' && sleep 5",
                "resource_files": []
            }
            for i in range(5)
        ]
        
        batch_manager.add_tasks(job_id, tasks)
        
        # Monitor tasks
        logger.info("\n--- Monitoring Tasks ---")
        results = batch_manager.monitor_tasks(job_id, timeout_minutes=10)
        logger.info(f"Task results: {results}")
        
        # Get task output
        logger.info("\n--- Getting Task Output ---")
        output = batch_manager.get_task_output(job_id, "task0")
        if output:
            logger.info(f"Task output:\n{output}")
        
        # Cleanup (commented out for safety)
        # logger.info("\n--- Cleanup ---")
        # batch_manager.delete_job(job_id)
        # batch_manager.delete_pool(pool_id)
        
        logger.info("\n" + "=" * 60)
        logger.info("Example completed successfully!")
        logger.info("=" * 60)
        logger.info(f"\nRemember to clean up:")
        logger.info(f"  - Delete job: {job_id}")
        logger.info(f"  - Delete pool: {pool_id}")
        
    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
