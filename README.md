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
