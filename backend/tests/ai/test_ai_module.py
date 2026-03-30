import pytest
from unittest.mock import patch, MagicMock
from backend.ai.rag_service import retrieve_aosa_context, retrieve_dynamic_context
from backend.ai.llm_client import generate_completion, LLMError

def test_retrieve_dynamic_context_basic():
    texts = ["Microservices Architecture", "Layered Architecture", "Distributed Systems"]
    query = "Microservices"
    results = retrieve_dynamic_context(query, texts, k=1)
    assert len(results) == 1
    assert "Microservices" in results[0]

def test_retrieve_dynamic_context_empty():
    results = retrieve_dynamic_context("test", [], k=5)
    assert results == []

@patch("backend.ai.rag_service._AOSA_INDEX")
@patch("backend.ai.rag_service._AOSA_CHUNKS")
@patch("backend.ai.rag_service._get_model")
def test_retrieve_aosa_context_mock(mock_get_model, mock_chunks, mock_index):
    mock_model = MagicMock()
    mock_model.encode.return_value = [[0.1, 0.2]] 
    mock_get_model.return_value = mock_model

    mock_index.search.return_value = ([[0.1]], [[0]])
    
    import backend.ai.rag_service as rag_service
    rag_service._AOSA_CHUNKS = ["Chunk 1", "Chunk 2"]
    rag_service._AOSA_INDEX = mock_index
    
    results = retrieve_aosa_context("query", k=1)
    assert len(results) == 1
    assert results[0] == "Chunk 1"


@patch("requests.post")
def test_generate_completion_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": '{"title": "Test Decision"}'}}]
    }
    mock_post.return_value = mock_response
    
    with patch.dict("os.environ", {"GROQ_API_KEY": "fake_key"}):
        from backend.ai.llm_client import GROQ_API_KEY
        with patch("backend.ai.llm_client.GROQ_API_KEY", "fake_key"):
            result = generate_completion("Hello")
            assert "Test Decision" in result

@patch("requests.post")
def test_generate_completion_api_error(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_post.return_value = mock_response
    
    with patch("backend.ai.llm_client.GROQ_API_KEY", "fake_key"):
        with pytest.raises(LLMError) as exc:
            generate_completion("Hello")
        assert "Groq API error 500" in str(exc.value)
