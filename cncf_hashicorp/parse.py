#!/usr/bin/env python3

import fileinput
import csv
from datetime import datetime

### Open https://cs.k8s.io/?q=hashicorp%5C%2F&i=nope&files=go.mod&excludeFiles=&repos=
### copy&paste data into www-list.txt


def parse(batch: str = None):
    if not batch:
        batch = int(datetime.utcnow().timestamp())
    out = list()
    repo, path = None, None

    for line in fileinput.input():
        line = line.strip()
        if " / " in line:
            r1, _, r2 = line.split()
            repo = f"{r1}/{r2}"
            continue
        if "go.mod" in line:
            path = line
            continue
        if not "github.com/hashicorp" in line:
            continue
        els = line.split()
        for el in els[1:]:
            # print("debug: ", el)
            if el.startswith("github.com/"):
                out.append((batch, repo, path, el))
                found = True
                break
        if not found:
            print("can't parse the line: ", line)

    return out


def main():
    out = parse()
    with open("result.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(out)


if __name__ == "__main__":
    main()
