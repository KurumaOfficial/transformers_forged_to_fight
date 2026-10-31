files = ["COVERAGE_WIKI.md", "STATE.md", "archive/wiki/README.md"]
for p in files:
    s = open(p, encoding="utf-8").read()
    s = s.replace("PENDING_REGENERATE", "040255c1d5714b4510493e87de4e323674864f5d54436c776d190c12285d4e18")
    s = s.replace("27,355,942", "32,513,587")
    s = s.replace("7220eabce902e552ed2bc6d86ca9d55477baeede6802ab9fd656306682be1aaf",
                  "040255c1d5714b4510493e87de4e323674864f5d54436c776d190c12285d4e18")
    open(p, "w", encoding="utf-8").write(s)
    print(p)
