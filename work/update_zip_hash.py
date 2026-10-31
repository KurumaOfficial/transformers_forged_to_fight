files = ["COVERAGE_WIKI.md", "STATE.md", "archive/wiki/README.md"]
for p in files:
    s = open(p, encoding="utf-8").read()
    s = s.replace("27,355,697", "27,355,942")
    s = s.replace("1791fd6662800fce0e4999b1a5bcc82248ec3d44e0126f3baa40e952b9f54223",
                  "7220eabce902e552ed2bc6d86ca9d55477baeede6802ab9fd656306682be1aaf")
    open(p, "w", encoding="utf-8").write(s)
    print(p, "updated")
