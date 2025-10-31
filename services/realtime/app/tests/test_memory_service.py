import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import numpy as np
from datetime import datetime, timedelta
from app.services import MemoryService
from app.main import app, verify_token

# Test data
TEST_USER_ID = 1
TEST_MESSAGE = "Test memory message"
TEST_EMBEDDING = np.random.rand(1536)  # OpenAI Ada-2 embedding size
TEST_MEMORY = {
    "id": 1,
    "user": TEST_USER_ID,
    "message": TEST_MESSAGE,
    "role": "user",
    "context": {"mood": "happy"},
    "vector_embedding": TEST_EMBEDDING.tolist(),
    "relevance_score": 1.0,
    "timestamp": datetime.now().isoformat()
}

@pytest.fixture
def memory_service():
    """Create a MemoryService instance with mocked OpenAI."""
    service = MemoryService()
    service.openai = MagicMock()
    return service

@pytest.fixture
def mock_openai_embedding():
    """Mock OpenAI's embedding creation."""
    async def mock_acreate(*args, **kwargs):
        return {
            "data": [{
                "embedding": TEST_EMBEDDING.tolist()
            }]
        }
    
    with patch("openai.Embedding.acreate", new_callable=AsyncMock) as mock:
        mock.side_effect = mock_acreate
        yield mock

@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for Django API calls."""
    with patch("httpx.AsyncClient") as mock:
        client = AsyncMock()
        client.post = AsyncMock(return_value=AsyncMock(
            json=lambda: TEST_MEMORY,
            status_code=201
        ))
        client.get = AsyncMock(return_value=AsyncMock(
            json=lambda: [TEST_MEMORY],
            status_code=200
        ))
        mock.return_value.__aenter__.return_value = client
        yield mock

@pytest.mark.asyncio
async def test_generate_embedding(memory_service, mock_openai_embedding):
    """Test vector embedding generation."""
    embedding = await memory_service._generate_embedding(TEST_MESSAGE)
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (1536,)  # OpenAI Ada-2 embedding size
    mock_openai_embedding.assert_called_once_with(
        input=TEST_MESSAGE,
        model="text-embedding-ada-002"
    )

@pytest.mark.asyncio
async def test_store_memory(memory_service, mock_openai_embedding, mock_httpx_client):
    """Test memory storage with vector embedding."""
    context = {"mood": "happy"}
    memory = await memory_service.store_memory(
        user_id=TEST_USER_ID,
        message=TEST_MESSAGE,
        role="user",
        context=context
    )
    
    assert memory["message"] == TEST_MESSAGE
    assert memory["context"] == context
    assert len(memory["vector_embedding"]) == 1536

@pytest.mark.asyncio
async def test_query_relevant_memories(memory_service, mock_openai_embedding, mock_httpx_client):
    """Test semantic search functionality."""
    # Create test memories with known embeddings
    memories = await memory_service.query_relevant_memories(
        user_id=TEST_USER_ID,
        query="test query",
        limit=5
    )
    
    assert len(memories) > 0
    assert all("vector_embedding" in m for m in memories)
    assert all("relevance_score" in m for m in memories)

def test_calculate_similarity(memory_service):
    """Test cosine similarity calculation."""
    vec1 = np.array([1, 0, 0])
    vec2 = np.array([1, 0, 0])
    vec3 = np.array([0, 1, 0])
    
    # Same vector should have similarity 1
    assert memory_service._calculate_similarity(vec1, vec2) == pytest.approx(1.0)
    # Orthogonal vectors should have similarity 0
    assert memory_service._calculate_similarity(vec1, vec3) == pytest.approx(0.0)

def test_calculate_age_penalty(memory_service):
    """Test memory relevance decay based on age."""
    now = datetime.now()
    
    # Test cases with different ages
    test_cases = [
        (now.isoformat(), 1.0),  # Current - no decay
        ((now - timedelta(days=7)).isoformat(), pytest.approx(0.5, rel=0.1)),  # 1 week old
        ((now - timedelta(days=30)).isoformat(), pytest.approx(0.05, rel=0.1))  # 1 month old
    ]
    
    for timestamp, expected_relevance in test_cases:
        age_penalty = memory_service._calculate_age_penalty(timestamp)
        assert age_penalty == expected_relevance