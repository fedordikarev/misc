$!/bin/bash

### Open https://cs.k8s.io/?q=hashicorp%5C%2F&i=nope&files=go.mod&excludeFiles=&repos=
### copy&paste data into www-list.txt
python3 parse www-list.txt

awk -F, '{ print $2 }' result.csv | sort | uniq | xargs python3 fetch_repo_info.py
mv repo_info.csv cncf_repo_info.csv

awk -F, '{ print $4 }' result.csv | sort | uniq | xargs python3 fetch_repo_info.py
mv repo_info.csv modules_info.csv

### TODO: add commands to upload into SQL (Clickhouse)
