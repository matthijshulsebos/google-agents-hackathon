from typing import Dict, Tuple

from google.api_core import exceptions as gax_exceptions
from google.cloud import discoveryengine_v1 as de


DEFAULT_COLLECTION = "default_collection"
DEFAULT_LOCATION = "global"
DEFAULT_SERVING_CONFIG_ID = "default_serving_config"


def _parent_path(project: str, location: str = DEFAULT_LOCATION, collection: str = DEFAULT_COLLECTION) -> str:
    return f"projects/{project}/locations/{location}/collections/{collection}"


def data_store_path(project: str, data_store_id: str, location: str = DEFAULT_LOCATION, collection: str = DEFAULT_COLLECTION) -> str:
    return f"{_parent_path(project, location, collection)}/dataStores/{data_store_id}"


def serving_config_path(project: str, data_store_id: str, serving_config_id: str = DEFAULT_SERVING_CONFIG_ID,
                        location: str = DEFAULT_LOCATION, collection: str = DEFAULT_COLLECTION) -> str:
    return f"{data_store_path(project, data_store_id, location, collection)}/servingConfigs/{serving_config_id}"


def ensure_data_store(project: str, data_store_id: str, display_name: str) -> str:
    """
    Ensure a Discovery Engine Data Store exists. Returns full resource name.
    """
    client = de.DataStoreServiceClient()
    name = data_store_path(project, data_store_id)
    try:
        client.get_data_store(name=name)
        return name
    except gax_exceptions.NotFound:
        pass
    except Exception:
        # If we cannot verify, attempt create anyway; if fails, bubble up
        pass
    parent = _parent_path(project)
    # Build DataStore with best-effort industry_vertical if available
    ds_kwargs = {"display_name": display_name}
    try:
        # Some library versions require industry_vertical; use GENERIC if present
        industry_enum = getattr(de, "IndustryVertical", None)
        if industry_enum is None:
            # Older versions may have DataStore.IndustryVertical
            industry_enum = getattr(de.DataStore, "IndustryVertical", None)
        if industry_enum is not None:
            ds_kwargs["industry_vertical"] = getattr(industry_enum, "GENERIC", 0)
    except Exception:
        pass
    ds = de.DataStore(**ds_kwargs)
    try:
        op = client.create_data_store(parent=parent, data_store=ds, data_store_id=data_store_id)
        op.result()  # wait
    except gax_exceptions.AlreadyExists:
        # Race condition; treat as success
        pass
    return name


def ensure_serving_config(project: str, data_store_id: str, serving_config_id: str = DEFAULT_SERVING_CONFIG_ID,
                          display_name: str = "Default Serving Config") -> str:
    """
    Ensure a Serving Config exists under the given data store. Returns full resource name.
    """
    client = de.ServingConfigServiceClient()
    name = serving_config_path(project, data_store_id, serving_config_id)
    try:
        client.get_serving_config(name=name)
        return name
    except gax_exceptions.NotFound:
        pass
    except Exception:
        # If cannot verify, attempt create; if fails, bubble up
        pass
    parent = data_store_path(project, data_store_id)
    sc = de.ServingConfig(display_name=display_name)
    try:
        client.create_serving_config(parent=parent, serving_config=sc, serving_config_id=serving_config_id)
    except gax_exceptions.AlreadyExists:
        pass
    return name


def ensure_resources_for_domains(project: str, domains: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    """
    Given a mapping of domains -> {bucket, data_store?, serving_config?}, ensure a data store and serving config exist
    for each domain. Returns a new mapping with full resource names filled in.
    """
    updated: Dict[str, Dict[str, str]] = {}
    for domain, cfg in domains.items():
        bucket = cfg.get("bucket", f"{domain}-bucket")
        # Derive deterministic IDs
        data_store_id = f"{domain}-data-store"
        serving_id = DEFAULT_SERVING_CONFIG_ID
        try:
            ds_name = ensure_data_store(project, data_store_id, display_name=f"{domain.title()} Data Store")
            sc_name = ensure_serving_config(project, data_store_id, serving_id, display_name=f"{domain.title()} Default Serving")
        except Exception as e:
            # On failure, keep any provided values (may be blanks) so app still starts
            print(f"[WARN] Could not ensure Discovery Engine resources for domain '{domain}': {e}")
            ds_name = cfg.get("data_store", "")
            sc_name = cfg.get("serving_config", "")
        updated[domain] = {
            "bucket": bucket,
            "data_store": ds_name,
            "serving_config": sc_name,
        }
    return updated
