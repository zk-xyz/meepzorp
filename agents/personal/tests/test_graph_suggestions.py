import importlib
import sys
import types
import pytest

class MockResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json = json_data or []
    def json(self):
        return self._json

@pytest.fixture
def capability(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "http://localhost")
    monkeypatch.setenv("SUPABASE_KEY", "test-key")

    # Stub external libraries not installed in the test environment
    requests_mod = types.ModuleType('requests')
    requests_mod.get = lambda *a, **k: None
    requests_mod.post = lambda *a, **k: None
    requests_mod.patch = lambda *a, **k: None
    requests_mod.delete = lambda *a, **k: None
    sys.modules['requests'] = requests_mod

    loguru_mod = types.ModuleType('loguru')
    loguru_mod.logger = types.SimpleNamespace(info=lambda *a, **k: None,
                                              error=lambda *a, **k: None,
                                              debug=lambda *a, **k: None,
                                              warning=lambda *a, **k: None)
    sys.modules['loguru'] = loguru_mod

    nltk_mod = types.ModuleType('nltk')
    data_mod = types.ModuleType('nltk.data')
    data_mod.find = lambda *a, **k: True
    nltk_mod.data = data_mod
    nltk_mod.download = lambda *a, **k: None
    corpus_mod = types.ModuleType('nltk.corpus')
    corpus_mod.stopwords = types.SimpleNamespace(words=lambda *a, **k: [])
    nltk_mod.corpus = corpus_mod
    tokenize_mod = types.ModuleType('nltk.tokenize')
    tokenize_mod.word_tokenize = lambda *a, **k: []
    nltk_mod.tokenize = tokenize_mod
    stem_mod = types.ModuleType('nltk.stem')
    stem_mod.WordNetLemmatizer = lambda: types.SimpleNamespace()
    nltk_mod.stem = stem_mod
    for name, mod in {
        'nltk': nltk_mod,
        'nltk.data': data_mod,
        'nltk.corpus': corpus_mod,
        'nltk.tokenize': tokenize_mod,
        'nltk.stem': stem_mod,
    }.items():
        sys.modules[name] = mod

    spacy_mod = types.ModuleType('spacy')
    spacy_mod.load = lambda name: object()
    sys.modules['spacy'] = spacy_mod

    rake_mod = types.ModuleType('rake_nltk')
    rake_mod.Rake = lambda *a, **k: object()
    sys.modules['rake_nltk'] = rake_mod

    skl_mod = types.ModuleType('sklearn')
    fe_mod = types.ModuleType('sklearn.feature_extraction')
    text_mod = types.ModuleType('sklearn.feature_extraction.text')
    text_mod.TfidfVectorizer = lambda *a, **k: object()
    fe_mod.text = text_mod
    skl_mod.feature_extraction = fe_mod
    metrics_mod = types.ModuleType('sklearn.metrics')
    pairwise_mod = types.ModuleType('sklearn.metrics.pairwise')
    pairwise_mod.cosine_similarity = lambda *a, **k: []
    metrics_mod.pairwise = pairwise_mod
    skl_mod.metrics = metrics_mod
    for name, mod in {
        'sklearn': skl_mod,
        'sklearn.feature_extraction': fe_mod,
        'sklearn.feature_extraction.text': text_mod,
        'sklearn.metrics': metrics_mod,
        'sklearn.metrics.pairwise': pairwise_mod,
    }.items():
        sys.modules[name] = mod

    numpy_mod = types.ModuleType('numpy')
    numpy_mod.array = lambda x: x
    sys.modules['numpy'] = numpy_mod

    from agents.personal.src import db as db_module
    import agents.personal.src.capabilities.graph_suggestions as gs
    importlib.reload(db_module)
    importlib.reload(gs)
    return gs.SuggestConnectionsCapability(db_module.KnowledgeDB())

@pytest.mark.asyncio
async def test_get_potential_targets_uses_embedding(mocker, capability):
    source = {"embedding": [0.1, 0.2, 0.3]}
    mock_resp = MockResponse(200, [])

    def mock_get(url, headers=None, params=None):
        assert params["order"] == f"embedding <-> '{source['embedding']}'::vector"
        return mock_resp

    mocker.patch('requests.get', side_effect=mock_get)
    await capability._get_potential_targets(source, limit=5)


