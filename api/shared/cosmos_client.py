"""
Azure Cosmos DB client for storing and retrieving video summaries.
"""
import os
import logging
from azure.cosmos.aio import CosmosClient
from azure.identity.aio import DefaultAzureCredential

# Configuration
endpoint = os.getenv("COSMOS_ENDPOINT")
database_name = os.getenv("COSMOS_DATABASE_NAME", "videosummaries")
container_videos = os.getenv("COSMOS_CONTAINER_VIDEOS", "videos")

# Lazy initialization
_client = None
_credential = None

def get_client():
    """Get or create Cosmos DB client."""
    global _client, _credential
    if _client is None:
        if not endpoint:
            raise ValueError("COSMOS_ENDPOINT environment variable is not set")
        _credential = DefaultAzureCredential()
        _client = CosmosClient(endpoint, credential=_credential)
    return _client

async def get_database():
    """Get or create database."""
    client = get_client()
    return client.get_database_client(database_name)

async def get_container(container_name: str):
    """Get container client."""
    database = await get_database()
    return database.get_container_client(container_name)

async def save_video_summary(video_data: dict):
    """Save video summary to Cosmos DB."""
    try:
        container = await get_container(container_videos)
        await container.upsert_item(video_data)
        logging.info(f"Saved video summary for {video_data['videoId']}")
    except Exception as e:
        logging.error(f"Error saving to Cosmos DB: {str(e)}")
        raise

async def get_video_summary(video_id: str, user_id: str):
    """Retrieve a video summary from Cosmos DB."""
    try:
        container = await get_container(container_videos)
        query = f"SELECT * FROM c WHERE c.videoId = @videoId AND c.userId = @userId"
        
        items = []
        async for item in container.query_items(
            query=query,
            parameters=[
                {"name": "@videoId", "value": video_id},
                {"name": "@userId", "value": user_id}
            ],
            enable_cross_partition_query=True
        ):
            items.append(item)
        
        return items[0] if items else None
    
    except Exception as e:
        logging.error(f"Error fetching from Cosmos DB: {str(e)}")
        return None

async def get_user_history(user_id: str, limit: int = 20):
    """Get user's video summary history."""
    try:
        container = await get_container(container_videos)
        query = "SELECT * FROM c WHERE c.userId = @userId ORDER BY c.createdAt DESC OFFSET 0 LIMIT @limit"
        
        items = []
        async for item in container.query_items(
            query=query,
            parameters=[
                {"name": "@userId", "value": user_id},
                {"name": "@limit", "value": limit}
            ],
            partition_key=user_id
        ):
            items.append(item)
        
        return items
    
    except Exception as e:
        logging.error(f"Error fetching history: {str(e)}")
        return []
