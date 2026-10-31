import re
s = open(r".\work\il2cpp_dump\dump.cs", encoding="utf-8", errors="replace").read()
i = s.find("public class Summary : Serializable // TypeDefIndex: 6443")
j = s.find("// Namespace:", i + 100)
t = s[i:j]
print(t[-2500:])
