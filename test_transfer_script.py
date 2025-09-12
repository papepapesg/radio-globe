import importlib


def test_transfer_function_exists():
    module = importlib.import_module('transfer_youtube_to_spotify')
    assert hasattr(module, 'transfer_yt_likes_to_spotify')
