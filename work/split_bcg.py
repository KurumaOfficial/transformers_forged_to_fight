from pathlib import Path

p = Path(r".\server\stub_server.py")
s = p.read_text(encoding="utf-8")


def replace_block(start_marker, end_marker, new_text):
    global s
    i = s.index(start_marker)
    j = s.index(end_marker, i)
    s = s[:i] + new_text + s[j:]


replace_block(
    "        # 9. BCG base hero data",
    "        # 10. BCG user data",
    """        # 9. BCG base hero data [STATIC: BCGAPI request body {heroes:[{bid,rank,level,sig_lvl,flvl}],api,nonce}]
        # Response is a JSON array of BCGHeroDetails. Attribute values below are [ASSUMED]
        # placeholders (the original Kabam server computed them); schema is [CLIENT].
        if path == "/bcg/getBaseHeroData":
            details = bcg_routes.base_hero_data(body, load_data_json, WEAK_ENEMY)
            self.send_sparx(details, assumed_label="[ASSUMED: /bcg/getBaseHeroData computed details]")
            return

""",
)

replace_block(
    "        # 10. BCG user data (roster)",
    "        # 10b. BCG set saved team",
    """        # 10. BCG user data (roster) [STATIC: loaded from data/bcg_user_data.json]
        if path == "/bcg/getUserData":
            data = bcg_routes.user_data(load_data_json)
            self.send_sparx(data, assumed_label="[STATIC: /bcg/getUserData loaded from data/bcg_user_data.json]")
            return

""",
)

replace_block(
    "        # 10b. BCG set saved team",
    "        # 11. AutoRefresh endpoints",
    """        # 10b. BCG set saved team [CLIENT: POST /bcg/setSavedTeam {teamID, heroes:[bid]}]
        # The client expects a userData-like payload back. Attributes are [ASSUMED].
        if path == "/bcg/setSavedTeam":
            payload = bcg_routes.set_saved_team(body, load_data_json)
            self.send_sparx(payload, assumed_label="[ASSUMED: /bcg/setSavedTeam full BCG payload + userData wrapper]")
            return

""",
)

p.write_text(s, encoding="utf-8")
print("done", len(s))
