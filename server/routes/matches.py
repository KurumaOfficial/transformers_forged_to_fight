"""Match response builders (T1 routing split, behavior unchanged)."""


def activate(load_data_json):
    return load_data_json("match_activate_response.json")


def match_loaded():
    return {"status": "ok"}


def resolve(load_data_json):
    return load_data_json("match_resolve_response.json")
