#!/usr/bin/env python3

import requests
import sys
import csv
import os

API = "https://api.github.com/repos/%s"


def get_repo_info(repo: str):
    repo = "/".join(repo.split("/")[:3])
    repo = repo.removeprefix("github.com/")
    r = requests.get(
        API % repo,
        headers={"Authorization": "Bearer {}".format(os.getenv("GH_TOKEN"))},
    )
    print(r.status_code)
    j = r.json()
    print(j, j.get("license"))
    if not j:
        print("failed: ", repo, r, j)
        return repo, "", ""
    return (
        repo,
        (j.get("license", {}) or {}).get("spdx_id", ""),
        j.get("visibility", ""),
    )


def main():
    with open("repo_info.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        for repo in sys.argv[1:]:
            print(repo)
            repo = repo.strip()
            writer.writerow(get_repo_info(repo))


if __name__ == "__main__":
    main()
