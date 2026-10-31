files = ["COVERAGE_WIKI.md", "STATE.md", "archive/wiki/README.md"]
for p in files:
    s = open(p, encoding="utf-8").read()
    s = s.replace("32,513,587", "32,513,591")
    s = s.replace("040255c1d5714b4510493e87de4e323674864f5d54436c776d190c12285d4e18",
                  "14b714b8e7e1409a2e74c32847ad78c7ee1e4a72cde3debfe97c2892da029c17")
    open(p, "w", encoding="utf-8").write(s)
    print(p)
