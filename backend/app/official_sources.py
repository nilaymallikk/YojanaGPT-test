from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class OfficialSource:
    name: str
    url: str
    purpose: str
    source_type: str
    priority: int
    needs_api_key: bool = False


OFFICIAL_SOURCES: tuple[OfficialSource, ...] = (
    OfficialSource(
        name="myScheme",
        url="https://www.myscheme.gov.in/",
        purpose="Primary national search and discovery portal for central and state government schemes.",
        source_type="scheme_discovery",
        priority=1,
    ),
    OfficialSource(
        name="National Scholarship Portal",
        url="https://scholarships.gov.in/",
        purpose="Official portal for student scholarship discovery, registration, processing, and DBT workflows.",
        source_type="scholarships",
        priority=2,
    ),
    OfficialSource(
        name="National Portal of India",
        url="https://www.india.gov.in/",
        purpose="Single-window directory for government information, ministries, citizen services, and scheme pages.",
        source_type="national_directory",
        priority=3,
    ),
    OfficialSource(
        name="States and UTs Directory",
        url="https://www.india.gov.in/explore-india/facts-of-india/states-ut-districts",
        purpose="Verified state and union territory portal directory maintained by the National Portal of India.",
        source_type="state_directory",
        priority=4,
    ),
    OfficialSource(
        name="Open Government Data Platform India",
        url="https://www.data.gov.in/apis",
        purpose="Structured government datasets and APIs where scheme metadata is available.",
        source_type="dataset_api",
        priority=5,
        needs_api_key=True,
    ),
    OfficialSource(
        name="API Setu Directory",
        url="https://directory.apisetu.gov.in/",
        purpose="Government API directory for selected formal API integrations when approved access is available.",
        source_type="api_directory",
        priority=6,
        needs_api_key=True,
    ),
)


def list_official_sources() -> list[dict]:
    return [asdict(source) for source in sorted(OFFICIAL_SOURCES, key=lambda source: source.priority)]


def get_public_seed_urls() -> list[str]:
    return [source.url for source in OFFICIAL_SOURCES if not source.needs_api_key]
