#!/usr/bin/env python3
"""
Fork binance-skills-hub，贡献「交易者成长分析」skill
提交PR到官方仓库，极大提升比赛独特性评分
"""

import urllib.request, json

TOKEN = "os.environ.get("GITHUB_TOKEN","")"
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "Content-Type": "application/json",
}

def api(method, path, data=None):
    url = f"https://api.github.com{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=HEADERS, method=method)
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

# 1. Fork官方仓库
print("1. Fork binance-skills-hub...")
try:
    r = api("POST", "/repos/binance/binance-skills-hub/forks")
    print(f"   Fork成功: {r.get('html_url', r.get('message'))}")
except Exception as e:
    print(f"   已fork或: {e}")
