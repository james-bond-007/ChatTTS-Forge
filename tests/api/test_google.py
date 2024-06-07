import pytest
from fastapi.testclient import TestClient
from launch import create_api
import base64
import os

import tests.conftest

app_instance = create_api()
client = TestClient(app_instance.app)


@pytest.fixture
def google_text_synthesize_request():
    return {
        "input": {"text": "这是一个测试文本。"},
        "voice": {
            "languageCode": "ZH-CN",
            "name": "female2",
            "style": "",
            "temperature": 0.5,
            "topP": 0.8,
            "topK": 50,
            "seed": 42,
        },
        "audioConfig": {
            "audioEncoding": "mp3",
            "speakingRate": 1.0,
            "pitch": 0.0,
            "volumeGainDb": 0.0,
            "sampleRateHertz": 24000,
            "batchSize": 1,
            "spliterThreshold": 100,
        },
    }


def test_google_text_synthesize_success(google_text_synthesize_request):
    response = client.post("/v1/text:synthesize", json=google_text_synthesize_request)
    assert response.status_code == 200
    assert "audioContent" in response.json()

    with open(
        os.path.join(
            tests.conftest.test_outputs_dir, "google_text_synthesize_success.mp3"
        ),
        "wb",
    ) as f:
        b64_str = response.json()["audioContent"]
        b64_str = b64_str.split(",")[1]
        f.write(base64.b64decode(b64_str))


def test_google_text_synthesize_missing_input():
    response = client.post("/v1/text:synthesize", json={})
    assert response.status_code == 422
    assert "Field required" == response.json()["detail"][0]["msg"]


def test_google_text_synthesize_invalid_voice():
    request = {
        "input": {"text": "这是一个测试文本。"},
        "voice": {
            "languageCode": "EN-US",
            "name": "invalid_voice",
            "style": "",
            "temperature": 0.5,
            "topP": 0.8,
            "topK": 50,
            "seed": 42,
        },
        "audioConfig": {
            "audioEncoding": "mp3",
            "speakingRate": 1.0,
            "pitch": 0.0,
            "volumeGainDb": 0.0,
            "sampleRateHertz": 24000,
            "batchSize": 1,
            "spliterThreshold": 100,
        },
    }
    response = client.post("/v1/text:synthesize", json=request)
    assert response.status_code == 400
    assert "detail" in response.json()


def test_google_text_synthesize_invalid_audio_encoding():
    request = {
        "input": {"text": "这是一个测试文本。"},
        "voice": {
            "languageCode": "ZH-CN",
            "name": "female2",
            "style": "",
            "temperature": 0.5,
            "topP": 0.8,
            "topK": 50,
            "seed": 42,
        },
        "audioConfig": {
            "audioEncoding": "invalid_format",
            "speakingRate": 1.0,
            "pitch": 0.0,
            "volumeGainDb": 0.0,
            "sampleRateHertz": 24000,
            "batchSize": 1,
            "spliterThreshold": 100,
        },
    }
    response = client.post("/v1/text:synthesize", json=request)
    assert response.status_code == 400
    assert "detail" in response.json()