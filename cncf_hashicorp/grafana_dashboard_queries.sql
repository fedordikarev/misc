-- Overview Dashboard
SELECT
a.repo, b.visibility,
a.module, c.license, path
-- count(*) as cnt
FROM cncf_hashicorp a
left join cncf_repo_info b using (repo)
left join modules_info c on (a.module = concat('github.com/', c.module))
WHERE
  (('${repo:raw}' = 'All') or (a.repo = '${repo:raw}'))
AND (('${module:raw}' = 'All') or (a.module = '${module:raw}'))
-- GROUP BY repo
order by a.repo, a.module, path
LIMIT 1000

-- By repo dashboard
select
a.repo,
b.visibility,
b.license,
a.cnt
 from
(
SELECT
repo,
count(*) as cnt
FROM cncf_hashicorp
WHERE
  (('${repo:raw}' = 'All') or (repo = '${repo:raw}'))
AND (('${module:raw}' = 'All') or (module = '${module:raw}'))
GROUP BY repo
) a
LEFT join `cncf_repo_info` b using (repo)
order by cnt desc
LIMIT 1000

-- By module dashboard
select
a.module,
c.visibility,
c.license,
a.cnt
 from
(
SELECT
module,
count(*) as cnt
FROM cncf_hashicorp
WHERE
  (('${repo:raw}' = 'All') or (repo = '${repo:raw}'))
AND (('${module:raw}' = 'All') or (module = '${module:raw}'))
GROUP BY module
) a
LEFT join `modules_info` c on (a.module = concat('github.com/', c.module))
order by cnt desc
LIMIT 1000
