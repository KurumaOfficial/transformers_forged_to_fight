"""ODR response builders (T1 routing split, behavior unchanged)."""


def manifest(load_data_json):
    return load_data_json("odr_manifest.json")


def published_manifests():
    return []
