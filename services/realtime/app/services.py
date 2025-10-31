from fastapi import HTTPException
import openai
import os
import numpy as np
from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime

# Mock non-memory-related imports during testing
try:
    from transformers import pipeline
    import whisper
except ImportError:
    # These are only needed for STT and Emotion services, not Memory service
    pipeline = None
    whisper = None

class STTService:
    """Speech-to-Text service with Whisper API and local fallback."""
    
    def __init__(self):
        self.whisper_api_key = os.getenv("WHISPER_API_KEY")
        self.local_model = None  # Lazy load if needed
        
    async def transcribe_chunk(self, audio_chunk: str) -> Dict[str, Any]:
        """Transcribe an audio chunk (base64 encoded)."""
        try:
            if self.whisper_api_key:
                return await self._transcribe_whisper_api(audio_chunk)
            return await self._transcribe_local(audio_chunk)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"STT error: {str(e)}")
    
    async def _transcribe_whisper_api(self, audio_chunk: str) -> Dict[str, Any]:
        """Use Whisper API for transcription."""
        # TODO: Implement Whisper API call
        pass
    
    async def _transcribe_local(self, audio_chunk: str) -> Dict[str, Any]:
        """Use local Whisper model as fallback."""
        if not self.local_model:
            self.local_model = whisper.load_model("base")
        
        # Convert base64 to audio
        audio_data = base64.b64decode(audio_chunk)
        # TODO: Convert to proper audio format and transcribe
        return {"text": "Local transcription placeholder"}

class EmotionService:
    """Emotion detection from voice and text."""
    
    def __init__(self):
        self.sentiment_analyzer = pipeline("sentiment-analysis")
    
    async def analyze_emotion(
        self,
        text: str,
        audio_features: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Analyze emotion from text and optional audio features."""
        # Text sentiment
        sentiment = self.sentiment_analyzer(text)[0]
        
        # Combine with audio features if available
        if audio_features:
            return self._combine_emotion_signals(sentiment, audio_features)
        
        return {
            "mood": self._map_sentiment_to_mood(sentiment["label"]),
            "confidence": sentiment["score"],
            "indicators": {"text_sentiment": sentiment["score"]}
        }
    
    def _map_sentiment_to_mood(self, sentiment: str) -> str:
        """Map HuggingFace sentiment to our mood categories."""
        mapping = {
            "POSITIVE": "happy",
            "NEGATIVE": "sad",
            "NEUTRAL": "neutral"
        }
        return mapping.get(sentiment, "neutral")
    
    def _combine_emotion_signals(
        self,
        sentiment: Dict[str, Any],
        audio_features: Dict[str, float]
    ) -> Dict[str, Any]:
        """Combine text sentiment with audio features."""
        # TODO: Implement more sophisticated combination logic
        return {
            "mood": self._map_sentiment_to_mood(sentiment["label"]),
            "confidence": (sentiment["score"] + audio_features.get("confidence", 0.5)) / 2,
            "indicators": {
                "text_sentiment": sentiment["score"],
                **audio_features
            }
        }

class AIService:
    """Low-latency AI response generation."""
    
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    async def get_quick_response(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a quick response optimized for low latency."""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=150,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            return {
                "text": response.choices[0].message.content,
                "usage": response.usage
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"AI response error: {str(e)}")


class MemoryService:
    """Manages conversation history and context using vector embeddings."""
    
    def __init__(self):
        self.openai = openai
        self.openai.api_key = os.getenv("OPENAI_API_KEY")
        self.django_api_url = os.getenv("DJANGO_API_URL", "http://localhost:8000")
        self.memory_decay_rate = 0.1  # Rate at which memory relevance decays
        
    async def store_memory(
        self,
        user_id: int,
        message: str,
        role: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store a new memory with its vector embedding."""
        try:
            # Generate embedding for semantic search
            embedding = await self._generate_embedding(message)
            
            # Create memory in Django backend
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.django_api_url}/api/v1/memories/",
                    json={
                        "user": user_id,
                        "message": message,
                        "role": role,
                        "context": context,
                        "vector_embedding": embedding.tolist(),
                        "relevance_score": 1.0
                    }
                )
                return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Memory storage error: {str(e)}")
    
    async def query_relevant_memories(
        self,
        user_id: int,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memories using semantic search."""
        try:
            # Get query embedding
            query_embedding = await self._generate_embedding(query)
            
            # Get all user memories from Django
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.django_api_url}/api/v1/memories/",
                    params={"user": user_id}
                )
                memories = response.json()
            
            # Calculate similarity scores
            similarities = []
            for memory in memories:
                if memory["vector_embedding"]:
                    similarity = self._calculate_similarity(
                        query_embedding,
                        np.array(memory["vector_embedding"])
                    )
                    # Apply relevance decay based on age
                    age_penalty = self._calculate_age_penalty(memory["timestamp"])
                    adjusted_score = similarity * memory["relevance_score"] * age_penalty
                    similarities.append((adjusted_score, memory))
            
            # Sort by similarity and return top matches
            similarities.sort(key=lambda x: x[0], reverse=True)
            return [memory for _, memory in similarities[:limit]]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Memory query error: {str(e)}")
    
    async def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate vector embedding for text using OpenAI's embedding API."""
        response = await openai.Embedding.acreate(
            input=text,
            model="text-embedding-ada-002"
        )
        return np.array(response["data"][0]["embedding"])
    
    def _calculate_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
    
    def _calculate_age_penalty(self, timestamp: str) -> float:
        """Calculate memory relevance decay based on age."""
        age = (datetime.now() - datetime.fromisoformat(timestamp.replace("Z", "+00:00")))
        days_old = age.total_seconds() / (24 * 3600)
        penalty = np.exp(-self.memory_decay_rate * days_old)
        # clamp very small floating-point drift
        if abs(penalty - 1.0) < 1e-9:
            penalty = 1.0
        return penalty


stt_service = STTService()
emotion_service = EmotionService()
ai_service = AIService()