"""Auth/account response builders (T1 routing split, behavior unchanged)."""

FALLBACK_LOGIN = {
    "token": "sess_tf_stub_token_12345",
    "stoken": "sess_tf_stub_token_12345",
    "auth": {"device": True},
    "endpoints": {"device": "http://127.0.0.1:8080"},
}


def init():
    return {"status": "ok", "session": "sess_tf_stub_token_12345"}


def enumerate_accounts():
    return []


def prelogin():
    return {"salt": "", "status": "ok"}


def login(load_data_json):
    data = load_data_json("login_response.json")
    return data or dict(FALLBACK_LOGIN)


def account_data(load_data_json):
    return load_data_json("account_data.json")
