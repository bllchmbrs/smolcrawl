from dotenv import load_dotenv
import os
import diskcache

load_dotenv()


DEFAULT_STORAGE_PATH = os.path.join(os.getcwd(), "smolcrawl-data")
DEFAULT_CACHE_PATH = os.path.join(DEFAULT_STORAGE_PATH, "cache")


def get_storage_path() -> str:
    return os.environ.get("SMOLCRAWL_STORAGE_PATH", DEFAULT_STORAGE_PATH)


def get_cache_path() -> str:
    return os.environ.get("SMOLCRAWL_CACHE_PATH", DEFAULT_CACHE_PATH)


def get_cache(name: str) -> diskcache.Cache:
    return diskcache.Cache(os.path.join(get_cache_path(), name))
