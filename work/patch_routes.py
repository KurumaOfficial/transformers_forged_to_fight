from pathlib import Path

p = Path("server/stub_server.py")
s = p.read_text(encoding="utf-8")

old_auth = '''        # 1. Auth Init [RUN: confirmed in device test]
        if path == "/auth/init":
            self.send_sparx({
                "status": "ok",
                "session": "sess_tf_stub_token_12345"
            }, assumed_label="[RUN: /auth/init]")
            return

        # 2. Auth Enumerate [STATIC: return [] for fresh account flow to invoke PreLoginFlow]
        if path == "/auth/enumerate":
            self.send_sparx([], assumed_label="[STATIC: /auth/enumerate empty accounts array]")
            return

        # 3. Prelogin [STATIC: salt="" causes SyncGenerateHMACSignatureFromAPK to skip APK_Check_Start_Salt in libapkprotect.so]
        if path == "/auth/prelogin":
            self.send_sparx({
                "salt": "",
                "status": "ok"
            }, assumed_label="[STATIC: /auth/prelogin bypass libapkprotect with empty salt]")
            return

        # 4. Login [STATIC: loaded from server/data/login_response.json]
        if path == "/auth/login":
            data = load_data_json("login_response.json")
            if not data:
                data = {
                    "token": "sess_tf_stub_token_12345",
                    "stoken": "sess_tf_stub_token_12345",
                    "auth": {"device": True},
                    "endpoints": {"device": "http://127.0.0.1:8080"}
                }
            self.send_sparx(data, assumed_label="[STATIC: /auth/login loaded from data/login_response.json]")
            return

        # 5. Account Data [STATIC: loaded from server/data/account_data.json]
        if path == "/account/data":
            data = load_data_json("account_data.json")
            self.send_sparx(data, assumed_label="[STATIC: /account/data loaded from data/account_data.json]")
            return
'''
new_auth = '''        # 1. Auth Init [RUN: confirmed in device test]
        if path == "/auth/init":
            self.send_sparx(auth_routes.init(), assumed_label="[RUN: /auth/init]")
            return

        # 2. Auth Enumerate [STATIC: return [] for fresh account flow to invoke PreLoginFlow]
        if path == "/auth/enumerate":
            self.send_sparx(auth_routes.enumerate_accounts(),
                            assumed_label="[STATIC: /auth/enumerate empty accounts array]")
            return

        # 3. Prelogin [STATIC: salt="" causes SyncGenerateHMACSignatureFromAPK to skip APK_Check_Start_Salt in libapkprotect.so]
        if path == "/auth/prelogin":
            self.send_sparx(auth_routes.prelogin(),
                            assumed_label="[STATIC: /auth/prelogin bypass libapkprotect with empty salt]")
            return

        # 4. Login [STATIC: loaded from server/data/login_response.json]
        if path == "/auth/login":
            self.send_sparx(auth_routes.login(load_data_json),
                            assumed_label="[STATIC: /auth/login loaded from data/login_response.json]")
            return

        # 5. Account Data [STATIC: loaded from server/data/account_data.json]
        if path == "/account/data":
            self.send_sparx(auth_routes.account_data(load_data_json),
                            assumed_label="[STATIC: /account/data loaded from data/account_data.json]")
            return
'''
if old_auth not in s:
    raise SystemExit("auth block not found")
s = s.replace(old_auth, new_auth, 1)

old_match = '''        # 12e2. ODR manifest [ASSUMED: client did not request it in the verified run]
        if path == "/odr/get-manifest":
            data = load_data_json("odr_manifest.json")
            self.send_sparx(data, assumed_label="[ASSUMED: /odr/get-manifest]")
            return
        if path == "/odr/get-published-manifests":
            self.send_sparx([], assumed_label="[ASSUMED: /odr/get-published-manifests empty list]")
            return

        # 12f. Matches: Activate Match [STATIC: loaded from server/data/match_activate_response.json]
        if path.startswith("/matches/activate-match/"):
            data = load_data_json("match_activate_response.json")
            self.send_sparx(data, assumed_label="[STATIC: /matches/activate-match/ loaded from data/match_activate_response.json]")
            return

        # 12g. Matches: Match Loaded [STATIC: MatchAPI SignalMatchLoaded]
        if path.startswith("/matches/match-loaded/"):
            self.send_sparx({"status": "ok"}, assumed_label="[STATIC: /matches/match-loaded/]")
            return

        # 12h. Matches: Resolve Match [STATIC: loaded from server/data/match_resolve_response.json]
        if path.startswith("/matches/resolve-match/"):
            data = load_data_json("match_resolve_response.json")
            self.send_sparx(data, assumed_label="[STATIC: /matches/resolve-match/ loaded from data/match_resolve_response.json]")
            return
'''
new_match = '''        # 12e2. ODR manifest [ASSUMED: client did not request it in the verified run]
        if path == "/odr/get-manifest":
            self.send_sparx(odr_routes.manifest(load_data_json),
                            assumed_label="[ASSUMED: /odr/get-manifest]")
            return
        if path == "/odr/get-published-manifests":
            self.send_sparx(odr_routes.published_manifests(),
                            assumed_label="[ASSUMED: /odr/get-published-manifests empty list]")
            return

        # 12f. Matches: Activate Match [STATIC: loaded from server/data/match_activate_response.json]
        if path.startswith("/matches/activate-match/"):
            self.send_sparx(match_routes.activate(load_data_json),
                            assumed_label="[STATIC: /matches/activate-match/ loaded from data/match_activate_response.json]")
            return

        # 12g. Matches: Match Loaded [STATIC: MatchAPI SignalMatchLoaded]
        if path.startswith("/matches/match-loaded/"):
            self.send_sparx(match_routes.match_loaded(),
                            assumed_label="[STATIC: /matches/match-loaded/]")
            return

        # 12h. Matches: Resolve Match [STATIC: loaded from server/data/match_resolve_response.json]
        if path.startswith("/matches/resolve-match/"):
            self.send_sparx(match_routes.resolve(load_data_json),
                            assumed_label="[STATIC: /matches/resolve-match/ loaded from data/match_resolve_response.json]")
            return
'''
if old_match not in s:
    raise SystemExit("match/odr block not found")
s = s.replace(old_match, new_match, 1)
p.write_text(s, encoding="utf-8")
print("patched")
