# Phase A - FastAPI Microservice Scaffold & Integration

## Files Changed/Added

1. `/services/realtime/`
   - `app/main.py` - FastAPI application with routes
   - `app/services.py` - Core services (STT, Emotion, AI)
   - `Dockerfile` - Container configuration
   - `requirements.txt` - Python dependencies

2. `.env.example`
   - Added new environment variables for FastAPI service

## New Endpoints

1. FastAPI Service (port 8000):
   - `POST /voice/stream/` - Stream voice chunks
   - `POST /voice/complete/` - Finalize voice analysis
   - `POST /ai/respond/` - Quick AI responses
   - `POST /wake/` - Wake word events
   - `WS /ws/voice/{session_id}` - WebSocket for real-time voice

## Implementation Details

### Speech-to-Text (STT)
- Primary: Whisper API
- Fallback: Local Whisper model
- Supports streaming chunks

### Emotion Detection
- Text sentiment via HuggingFace
- Audio feature extraction (pitch, tempo)
- Combined confidence scoring

### AI Response
- OpenAI GPT-3.5 Turbo
- Optimized for low latency
- Context-aware prompts

## Local Development Setup

1. Create and activate Python environment:
```bash
cd services/realtime
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run the FastAPI service:
```bash
cd services/realtime
uvicorn app.main:app --reload --port 8000
```

4. Test endpoints:
```bash
curl -X POST http://localhost:8000/voice/stream/ \
  -H "Content-Type: application/json" \
  -d '{"audio_chunk": "base64_audio", "session_id": "test"}'
```

## Docker Setup

```bash
cd services/realtime
docker build -t chaos-realtime .
docker run -p 8000:8000 chaos-realtime
```

## Testing

Basic tests implemented for:
- STT service
- Emotion analysis
- AI response generation

To run tests:
```bash
cd services/realtime
pytest
```

## Next Steps

1. Implement Django authentication endpoint for FastAPI
2. Add proper audio processing pipeline
3. Integrate with frontend voice capture
4. Add proper error handling and retry logic

## Notes

- Audio data is never persisted, only processed in-memory
- Emotion detection uses combined text/audio analysis
- AI responses are optimized for low latency
- WebSocket support added for future real-time features