from pathlib import Path
p = Path(r"C:\Users\gameg\Desktop\TFTF\server\stub_server.py")
s = p.read_text(encoding="utf-8")
old = '''            active_teams.append({
                "aid": qid, "type": "story", "modes": ["Story"], "expire": 0,
                "heroes": {d["bid"]: d for d in hero_details}
            })'''
new = '''            team_obj = {
                "aid": qid, "type": "story", "modes": ["Story"], "expire": 0,
                "heroes": {d["bid"]: d for d in hero_details}
            }
            active_teams.append(team_obj)
            mode_team = json.loads(json.dumps(team_obj))
            mode_team["aid"] = "story"
            mode_team["activityID"] = "story"
            active_teams.append(mode_team)'''
assert old in s
s = s.replace(old, new)
old2 = '''                    fixed["story"] = t
                    fixed["Story"] = t
                wrapper["updates"]["activeTeams"] = fixed'''
new2 = '''                    story_team = json.loads(json.dumps(t))
                    story_team["aid"] = "story"
                    story_team["activityID"] = "story"
                    fixed["story"] = story_team
                    story_upper = json.loads(json.dumps(story_team))
                    story_upper["aid"] = "Story"
                    story_upper["activityID"] = "Story"
                    fixed["Story"] = story_upper
                wrapper["updates"]["activeTeams"] = fixed'''
assert old2 in s
s = s.replace(old2, new2)
p.write_text(s, encoding="utf-8")
print("patched mode team clones")
