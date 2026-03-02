def test_anthropic_importable():
    import anthropic
    assert anthropic.__version__

def test_yaml_importable():
    import yaml
    assert yaml.__version__

def test_pydantic_importable():
    import pydantic
    assert pydantic.__version__

def test_dotenv_importable():
    import dotenv
    assert dotenv

def test_tqdm_importable():
    import tqdm
    assert tqdm.__version__
