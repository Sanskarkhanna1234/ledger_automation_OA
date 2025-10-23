import os

def project_root() -> str:
    return os.path.dirname(os.path.abspath(__file__))

def abspath_from_root(*parts: str) -> str:
    root = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(root, '..', *parts))
