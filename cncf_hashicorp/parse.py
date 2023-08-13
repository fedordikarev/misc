#!/usr/bin/env python3

import fileinput
import csv
from datetime import datetime

### Open https://cs.k8s.io/?q=hashicorp%5C%2F&i=nope&files=go.mod&excludeFiles=&repos=
### copy&paste data into www-list.txt
def parse_cs_k8s_io(batch: str = None):
    if not batch:
        batch = int(datetime.utcnow().timestamp())
    out = list()
    repo, path = None, None

    for line in fileinput.input():
        """
        kubernetes / kops
        go.mod
        137     github.com/gorilla/mux v1.8.0 // indirect
        138     github.com/gregjones/httpcache v0.0.0-20190611155906-901d90724c79 // indirect
        139     github.com/hashicorp/errwrap v1.1.0 // indirect
        hack/go.mod
        78      github.com/gostaticanalysis/forcetypeassert v0.1.0 // indirect
        79      github.com/gostaticanalysis/nilerr v0.1.1 // indirect
        80      github.com/hashicorp/errwrap v1.0.0 // indirect
        tests/e2e/go.mod
        75      github.com/googleapis/gax-go/v2 v2.12.0 // indirect
        76      github.com/gophercloud/gophercloud v1.5.0 // indirect
        77      github.com/hashicorp/errwrap v1.1.0 // indirect
        """
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


### gh search code --limit 3000 --filename go.mod --match file "github.com/hashicorp org:${your_org_name}"
def parse_gh_search_code(batch: str = None):
    if not batch:
        batch = int(datetime.utcnow().timestamp())

    out = list()
    repo, location = None, None

    for line in fileinput.input():
        """
        $org/$repo_name:go.mod: github.com/hashicorp/go-multierror v1.1.1
        """
        els = line.split()
        found = False
        repo, location, _ = els[0].split(":")
        # print(repo, location)
        for el in els[1:]:
            # print("debug: ", el)
            if el.startswith("github.com/"):
                out.append((batch, repo, location, el))
                found = True
                break
        if not found:
            print("can't parse the line: ", line)

    return out

def main():
    out = parse_cs_k8s_io()
    with open("result.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(out)


if __name__ == "__main__":
    main()
