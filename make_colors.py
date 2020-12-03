import json

with open('colors.json') as f:
    data = json.load(f)

with open('tmp.txt', 'w') as f:
    for c in data:
        n = data[c]["name"]
        r = data[c]["rgb"][0]
        g = data[c]["rgb"][1]
        b = data[c]["rgb"][2]
        f.write(f"Color(\"{n}\", {r}, {g}, {b}),\n")