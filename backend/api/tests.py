from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import timedelta
import numpy as np
from unittest.mock import patch, AsyncMock, Mock
from .models import Memory
from .serializers import MemorySerializer

User = get_user_model()

class MemoryModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.memory = Memory.objects.create(
            user=self.user,
            message="Test memory message",
            role="user",
            context={"mood": "happy", "task_id": 1},
            vector_embedding=[0.1, 0.2, 0.3],
            relevance_score=1.0
        )

    def test_memory_creation(self):
        """Test that a memory can be created with all fields."""
        self.assertEqual(self.memory.message, "Test memory message")
        self.assertEqual(self.memory.role, "user")
        self.assertEqual(self.memory.context["mood"], "happy")
        self.assertEqual(self.memory.relevance_score, 1.0)
        self.assertIsNotNone(self.memory.timestamp)

    def test_memory_ordering(self):
        """Test that memories are ordered by timestamp descending."""
        older_memory = Memory.objects.create(
            user=self.user,
            message="Older message",
            role="user",
            context={},
            timestamp=timezone.now() - timedelta(days=1)
        )
        newer_memory = Memory.objects.create(
            user=self.user,
            message="Newer message",
            role="user",
            context={},
            timestamp=timezone.now() + timedelta(minutes=1)
        )
        memories = list(Memory.objects.all())
        # Ensure timestamps are in descending order
        timestamps = [m.timestamp for m in memories]
        self.assertTrue(all(timestamps[i] >= timestamps[i+1] for i in range(len(timestamps)-1)))

    def test_vector_embedding_validation(self):
        """Test that vector embeddings are properly stored and retrieved."""
        embedding = [0.1, 0.2, 0.3]
        memory = Memory.objects.create(
            user=self.user,
            message="Vector test",
            role="user",
            vector_embedding=embedding
        )
        retrieved_memory = Memory.objects.get(pk=memory.pk)
        self.assertEqual(retrieved_memory.vector_embedding, embedding)

    def test_memory_str_representation(self):
        """Test the string representation of the Memory model."""
        expected_str = f"{self.memory.role} message from {self.user.username} at {self.memory.timestamp}"
        self.assertEqual(str(self.memory), expected_str)


class MemoryAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.memory_data = {
            "message": "Test API memory",
            "role": "user",
            "context": {"test": True},
            "relevance_score": 1.0
        }

    def test_create_memory(self):
        """Test creating a memory through the API."""
        response = self.client.post(
            '/api/v1/memories/',
            {
                "user": self.user.id,
                "message": "Test API memory",
                "role": "user",
                "context": {"test": True},
                "relevance_score": 1.0
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Memory.objects.count(), 1)
        self.assertEqual(Memory.objects.get().message, "Test API memory")

    def test_retrieve_memories(self):
        """Test retrieving memories through the API."""
        Memory.objects.create(user=self.user, **self.memory_data)
        response = self.client.get('/api/v1/memories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    @patch('httpx.post')
    def test_semantic_search(self, mock_post):
        """Test semantic search functionality."""
        memory = Memory.objects.create(
            user=self.user,
            message="Test semantic search",
            role="user",
            vector_embedding=[0.1, 0.2, 0.3]
        )
        
        # Setup mock response
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json = Mock(return_value=[MemorySerializer(memory).data])
        mock_post.return_value = mock_resp
        
        with self.settings(REALTIME_SERVICE_URL='http://test-service:8000'):
            response = self.client.post(
                '/api/v1/memories/semantic_search/',
                {"query": "test search"},
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            mock_post.assert_called_once()

    def test_memory_cleanup(self):
        """Test memory cleanup functionality."""
        # Set up user preferences
        self.user.preferences = {
            'memory': {
                'memory_retention_days': 30,
                'min_relevance_score': 0.5
            }
        }
        self.user.save()

        # Create an old memory
        now = timezone.now()
        old_timestamp = now.replace(microsecond=0) - timedelta(days=35)
        old_memory = Memory.objects.create(
            user=self.user,
            message="Old memory",
            role="user",
            timestamp=old_timestamp,
            relevance_score=0.7
        )
        
        # Create a recent memory
        recent_memory = Memory.objects.create(
            user=self.user,
            message="Recent memory",
            role="user",
            timestamp=timezone.now()
        )
        
        response = self.client.delete('/api/v1/memories/cleanup/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify old memory is deleted but recent one remains
        self.assertFalse(Memory.objects.filter(pk=old_memory.pk).exists())
        self.assertTrue(Memory.objects.filter(pk=recent_memory.pk).exists())

    def test_update_memory(self):
        """Test updating a memory through the API."""
        memory = Memory.objects.create(user=self.user, **self.memory_data)
        
        # Test PATCH update
        patch_data = {
            "message": "Updated message",
            "relevance_score": 0.8,
            "user": self.user.id
        }
        response = self.client.patch(
            f'/api/v1/memories/{memory.id}/',
            patch_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Updated message")
        self.assertEqual(response.data["relevance_score"], 0.8)
        
        # Test PUT update
        put_data = {
            **self.memory_data,
            "message": "Complete update",
            "user": self.user.id
        }
        response = self.client.put(
            f'/api/v1/memories/{memory.id}/',
            put_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Complete update")

    def test_delete_memory(self):
        """Test deleting a single memory."""
        memory = Memory.objects.create(user=self.user, **self.memory_data)
        response = self.client.delete(f'/api/v1/memories/{memory.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Memory.objects.filter(pk=memory.id).exists())

    def test_filter_memories_by_date(self):
        """Test filtering memories by date range."""
        # Create memories with different dates
        week_ago = timezone.now() - timedelta(days=7)
        month_ago = timezone.now() - timedelta(days=30)
        
        # Create memories with different dates
        memory_data = self.memory_data.copy()
        
        memory_data["message"] = "Recent memory"
        Memory.objects.create(
            user=self.user,
            timestamp=timezone.now(),
            **memory_data
        )

        memory_data["message"] = "Week old memory"
        Memory.objects.create(
            user=self.user,
            timestamp=week_ago,
            **memory_data
        )

        memory_data["message"] = "Month old memory"
        Memory.objects.create(
            user=self.user,
            timestamp=month_ago,
            **memory_data
        )

        # Test filtering last week's memories
        response = self.client.get(
            '/api/v1/memories/',
            {'start_date': week_ago.isoformat(), 'end_date': timezone.now().isoformat()}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should include recent and week-old memories

    def test_unauthorized_access(self):
        """Test unauthorized access to memories."""
        # Create another user and their memory
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        other_memory = Memory.objects.create(user=other_user, **self.memory_data)

        # Try to access other user's memory
        response = self.client.get(f'/api/v1/memories/{other_memory.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Try to update other user's memory
        response = self.client.patch(
            f'/api/v1/memories/{other_memory.id}/',
            {"message": "Unauthorized update"},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_memory_data(self):
        """Test handling of invalid memory data."""
        # Test missing required fields
        response = self.client.post(
            '/api/v1/memories/',
            {"user": self.user.id},  # Missing required fields
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid relevance score
        response = self.client.post(
            '/api/v1/memories/',
            {**self.memory_data, "relevance_score": 2.0},  # Score should be between 0 and 1
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bulk_operations(self):
        """Test bulk memory operations."""
        # Create test data
        memories_data = [
            {**self.memory_data, "message": f"Bulk memory {i}"} 
            for i in range(3)
        ]
        
        # Test bulk create
        response = self.client.post(
            '/api/v1/memories/bulk/',
            {"memories": memories_data},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 3)
        
        # Get created memory IDs
        memory_ids = [m["id"] for m in response.data]
        
        # Test bulk update
        bulk_update_data = [
            {"id": memory_id, "relevance_score": 0.5}
            for memory_id in memory_ids
        ]
        response = self.client.patch(
            '/api/v1/memories/bulk_update/',
            {"memories": bulk_update_data},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(m["relevance_score"] == 0.5 for m in response.data))
