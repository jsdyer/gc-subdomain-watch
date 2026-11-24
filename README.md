# GC Subdomain Watch

[Open GC Subdomain Watch](https://coolcode.ca/gc-subdomain-watch/)

Compare the official web addresses of Canadian institutions across dated federal directories.

<!-- coolcode:guide -->
Compare the 2023 and current directory, then filter by destination changes. The two recorded dates bound the change. Each result links to the editions used, and the RSS feed carries observed changes.
<!-- /coolcode:guide -->

## Editions and interpretation

The November 2023 and November 2025 baselines are Internet Archive captures of the same Government of Canada department directory. The first current retrieval was November 19, 2026. The importer checks daily, retains earlier editions and records a new version when the published directory changes. Comparisons use the listed English institution name. A rename can appear as a removal plus an addition. A listed destination includes both hostname and path. The RSS feed and CSV report observed directory changes.

Certificate summaries cover four already-public federal, provincial and municipal homepages. The collector queries each exact homepage for unexpired issuances indexed by Cert Spotter. On lookup failure the previous summary retains its own retrieval date. These records establish issuance for a name. They do not establish the date a service opened, its address, or which certificate a browser received. The directory change feed uses the published listings as its source.

[Current directory](https://www.canada.ca/en/government/dept.html) · [Certificate search documentation](https://sslmate.com/help/reference/ct_search_api_v1) · [Change feed](https://coolcode.ca/gc-subdomain-watch/changes.xml)

Run `python scripts/refresh.py` to import, `node --test tests/*.test.mjs` and `python -m unittest discover -s tests` to test, and `python scripts/build.py` for an offline build.

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

This is an interim mitigation, not a scheduling guarantee: GitHub does not document active-workflow renewal as a permanent exemption, and scheduled runs can be delayed or dropped. A scheduler on our own Linux server is the planned independent trigger. The guard does not collect data, create dummy commits, or change source/check timestamps; successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->

Source requests are bounded by time and size. If the primary HTTPS client has a transport error or a 403/429/server response, the collector tries the same public URL with curl (installed on GitHub runners; optional locally). TLS verification remains enabled. Both clients must obtain a valid response and the existing data validation must pass before a successful check is recorded. If both fail, the previous publication keeps its original dates.

A change to the collector, its browser regression check or its Pages workflow triggers a live refresh before publication. Ordinary UI and data-only commits still build from retained data. Scheduled and manual refresh controls are unchanged.
