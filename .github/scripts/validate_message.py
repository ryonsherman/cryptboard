import json, sys, base64

with open(sys.argv[1]) as fh:
    d = json.load(fh)

assert isinstance(d, dict) and 'h' in d and 'b' in d, 'missing h/b keys'
base64.b64decode(d['h'])
base64.b64decode(d['b'])
