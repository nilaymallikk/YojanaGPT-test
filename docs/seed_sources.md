# Official Seed Source Plan

Use official URLs only. Start with public pages, then add structured APIs where access is available.

## Primary Public Sources

| Source | URL | Purpose |
| --- | --- | --- |
| myScheme | https://www.myscheme.gov.in/ | Main national discovery platform for central and state schemes. |
| National Scholarship Portal | https://scholarships.gov.in/ | Scholarship discovery, student registration, processing, and DBT workflows. |
| National Portal of India | https://www.india.gov.in/ | Single-window national government information and citizen-services directory. |
| States and UTs Directory | https://www.india.gov.in/explore-india/facts-of-india/states-ut-districts | Verified directory for state and union territory portals. |

## Optional API Sources

| Source | URL | What is needed |
| --- | --- | --- |
| Open Government Data Platform India | https://www.data.gov.in/apis | A data.gov.in account/API key for API-backed datasets. |
| API Setu Directory | https://directory.apisetu.gov.in/ | API Setu account and access approval for specific APIs. |

## Ingestion Order

1. Ingest myScheme public pages and scheme detail pages.
2. Ingest NSP public scheme and eligibility pages.
3. Ingest India.gov.in scheme and citizen-service pages.
4. Use the States and UTs Directory to discover verified state portal URLs.
5. Add data.gov.in or API Setu only after credentials and target API names are available.
