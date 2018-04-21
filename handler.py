import json
from functools import reduce
from collections import Counter

with open('sols') as f:
    sols = json.load(f)

def lower(x):
    return x.lower()

res = [list(map(lower, i)) for j in sols['res'] for i in j]

tech = Counter(i for j in res for i in j)

def next(event, context):
    q = event["queryStringParameters"] or {}

    interested = set(map(lower, q.get("skills", "").split(",")))
    notinterested = set(map(lower, q.get("notinterested", "").split(",")))

    iConst = float(q.get("interested_const", 5.0))
    nConst = float(q.get("notinterested_const", 5.0))

    def reeval(job):
        s = set(job)
        n = s.intersection(notinterested)
        i = s.intersection(interested)
        d = s.difference(interested).difference(notinterested)
        return {j: ((1.0 + iConst * len(i) - nConst * len(n)) / len(d)) for j in d}

    def red(d1, d2):
        for k, v in d1.items():
            d2[k] = d2.get(k, 0) + v
        return d2

    y = map(reeval, res)
    x = reduce(red, y, {})
    r = list(x.items())
    r.sort(key=lambda x: -x[1])

    response = {
        "statusCode": 200,
        "body": json.dumps(r[:10]),
        "headers": {
             "Access-Control-Allow-Origin": "*"
        }
    }

    return response

def autocomplete(event, context):
    q = (event["queryStringParameters"] or {}).get("q", "")
    res = list((k, -l) for (l, k) in sorted((-tech[i], i) for i in tech if i.startswith(q)))
    response = {
        "statusCode": 200,
        "body": json.dumps(res[:10]),
        "headers": {
             "Access-Control-Allow-Origin": "*"
        }
    }

    return response
