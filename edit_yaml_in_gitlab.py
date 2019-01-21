#!/usr/bin/env python3
""" automated edit yaml in gitlab repo """

import os
import argparse
from urllib.parse import quote
import requests
import ruamel.yaml
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO
from ruamel.yaml.scalarstring import DoubleQuotedScalarString

GITLAB = "https://gitlab.hamilton.rinet.ru"
API = "api/v4/projects"
REPO = quote("folder/repo", safe='')
PATH = quote("path/to/file.yml", safe='')

NEW_BRANCH_NAME = "new_list_in_yaml"

def parse_args():
    """ Parse cli args """
    parser = argparse.ArgumentParser(description="Add domains to field")
    parser.add_argument("domains", nargs="+",
                        help="domains to add")
    return parser.parse_args()

# https://yaml.readthedocs.io/en/latest/example.html#output-of-dump-as-a-string
class MyYAML(YAML):
    """ Used for dump ruamel.yaml as string """
    def dump(self, data, stream=None, **kw):
        inefficient = False
        if stream is None:
            inefficient = True
            stream = StringIO()
        YAML.dump(self, data, stream, **kw)
        if inefficient:
            return stream.getvalue()


def read_config(path="~/.secrets/gitlab.yaml"):
    """ Read config (auth token) from config """
    yaml = ruamel.yaml.YAML()
    with open(os.path.expanduser(path), "r") as f:  #pylint: disable=invalid-name
        return yaml.load(f)

def get_gitlab_yaml(path, token):
    """ Read file yaml settings """
    r = requests.get(   #pylint: disable=invalid-name
        f"{GITLAB}/{API}/{REPO}/repository/files/{path}/raw?ref=master",
        headers={"Private-Token": token}
        )
    return ruamel.yaml.round_trip_load(r.text, preserve_quotes=True)

def update_gitlab_yaml(path, token, yaml_content):
    """ Put new file content and create merge request """
    yaml = MyYAML()
    # Step 1. Create branch with changes
    put_data = {
        "branch": NEW_BRANCH_NAME,
        "start_branch": "master",
        "content": yaml.dump(yaml_content),
        "commit_message": "automated commit"
        }
    r = requests.put(   #pylint: disable=invalid-name
        f"{GITLAB}/{API}/{REPO}/repository/files/{path}",
        headers={"Private-Token": token},
        data=put_data
        )

    # Step 2. Create merge request
    post_data = {
        "source_branch": NEW_BRANCH_NAME,
        "target_branch": "master",
        "title": "Update domains list",
        "remove_source_branch": True,
        "squash": True
        }
    r = requests.post(  #pylint: disable=invalid-name
        f"{GITLAB}/{API}/{REPO}/merge_requests",
        headers={"Private-Token": token},
        data=post_data
        )

    return r

def main():
    """ Main function """
    conf = read_config()
    token = conf['deploy']

    args = parse_args()

    file_yaml = get_gitlab_yaml(PATH, token)
    print(file_yaml['section']['subsection']['field'])
    for domain in args.domains:
        if not domain.startswith("https://"):
            domain = "https://{}".format(domain)
        file_yaml['section']['subsection']['field'].append(
            DoubleQuotedScalarString(domain)
            )
    r = update_gitlab_yaml(PATH, token, file_yaml) #pylint: disable=invalid-name
    # print(r.text)
    print(r)

if __name__ == "__main__":
    main()
