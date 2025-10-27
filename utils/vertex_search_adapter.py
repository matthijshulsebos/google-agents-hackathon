"""
Vertex AI Search Adapter - Interface with Google Cloud Discovery Engine
Provides search capabilities using Vertex AI Search (Discovery Engine)
"""

import os
from typing import Dict, List, Optional, Any
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions


class VertexSearchAdapter:
    """
    Adapter for Vertex AI Search (Discovery Engine) operations
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        search_engine_id: Optional[str] = None
    ):
        """
        Initialize Vertex AI Search adapter

        Args:
            project_id: Google Cloud project ID (defaults to env var GCP_PROJECT_ID)
            location: Google Cloud location (defaults to env var GCP_LOCATION or 'global')
            search_engine_id: Default search engine/datastore ID
        """
        self.project_id = project_id or os.getenv("GCP_PROJECT_ID")
        self.location = location or os.getenv("GCP_LOCATION", "global")
        self.search_engine_id = search_engine_id or os.getenv("VERTEX_SEARCH_ENGINE_ID")

        if not self.project_id:
            raise ValueError("project_id must be provided or set in GCP_PROJECT_ID environment variable")

        # Initialize client with regional endpoint if needed
        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Discovery Engine search client"""
        # For global location, use the default endpoint
        if self.location == "global":
            self._client = discoveryengine.SearchServiceClient()
        else:
            # For regional locations, use regional endpoint
            client_options = ClientOptions(
                api_endpoint=f"{self.location}-discoveryengine.googleapis.com"
            )
            self._client = discoveryengine.SearchServiceClient(client_options=client_options)

    def search(
        self,
        query: str,
        search_engine_id: Optional[str] = None,
        page_size: int = 10,
        offset: int = 0,
        filter_expr: Optional[str] = None,
        order_by: Optional[str] = None,
        facet_specs: Optional[List[Dict[str, Any]]] = None,
        boost_spec: Optional[Dict[str, Any]] = None,
        query_expansion: bool = True,
        spell_correction: bool = True
    ) -> Dict[str, Any]:
        """
        Execute a search query using Vertex AI Search

        Args:
            query: The search query string
            search_engine_id: Search engine/datastore ID (uses default if not provided)
            page_size: Number of results to return (max 100)
            offset: Number of results to skip for pagination
            filter_expr: Filter expression (e.g., "category: ANY('medical', 'clinical')")
            order_by: Field to order results by
            facet_specs: List of facet specifications for faceted search
            boost_spec: Specification for boosting certain results
            query_expansion: Enable query expansion for better results
            spell_correction: Enable automatic spell correction

        Returns:
            Dictionary containing search results and metadata
        """
        engine_id = search_engine_id or self.search_engine_id
        if not engine_id:
            raise ValueError("search_engine_id must be provided or set in VERTEX_SEARCH_ENGINE_ID")

        # Construct the serving config path
        serving_config = (
            f"projects/{self.project_id}/locations/{self.location}/"
            f"collections/default_collection/engines/{engine_id}/"
            f"servingConfigs/default_config"
        )

        # Build search request
        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=query,
            page_size=min(page_size, 100),  # Max 100 per page
            offset=offset,
        )

        # Add optional parameters
        if filter_expr:
            request.filter = filter_expr

        if order_by:
            request.order_by = order_by

        # Configure query expansion
        if query_expansion:
            request.query_expansion_spec = discoveryengine.SearchRequest.QueryExpansionSpec(
                condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO
            )

        # Configure spell correction
        if spell_correction:
            request.spell_correction_spec = discoveryengine.SearchRequest.SpellCorrectionSpec(
                mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
            )

        # Add facet specifications if provided
        if facet_specs:
            request.facet_specs = [
                self._build_facet_spec(spec) for spec in facet_specs
            ]

        # Add boost specification if provided
        if boost_spec:
            request.boost_spec = self._build_boost_spec(boost_spec)

        try:
            # Execute search
            response = self._client.search(request)

            # Parse and return results
            return self._parse_search_response(response)

        except Exception as e:
            return {
                "error": str(e),
                "query": query,
                "search_engine_id": engine_id,
                "results": []
            }

    def _build_facet_spec(self, spec: Dict[str, Any]) -> discoveryengine.SearchRequest.FacetSpec:
        """
        Build a facet specification from dictionary

        Args:
            spec: Facet spec dictionary with 'key' and optional 'limit'

        Returns:
            FacetSpec object
        """
        facet_key = discoveryengine.SearchRequest.FacetSpec.FacetKey(
            key=spec.get("key"),
            intervals=spec.get("intervals", [])
        )

        return discoveryengine.SearchRequest.FacetSpec(
            facet_key=facet_key,
            limit=spec.get("limit", 10)
        )

    def _build_boost_spec(self, spec: Dict[str, Any]) -> discoveryengine.SearchRequest.BoostSpec:
        """
        Build a boost specification from dictionary

        Args:
            spec: Boost spec dictionary

        Returns:
            BoostSpec object
        """
        # This is a simplified version - extend as needed
        return discoveryengine.SearchRequest.BoostSpec(
            condition_boost_specs=spec.get("condition_boost_specs", [])
        )

    def _parse_search_response(self, response) -> Dict[str, Any]:
        """
        Parse search response into a structured dictionary

        Args:
            response: SearchResponse from Discovery Engine

        Returns:
            Structured response dictionary
        """
        results = []

        for result in response.results:
            doc_data = {
                "id": result.id,
                "document": {}
            }

            # Extract document data
            if result.document:
                doc = result.document
                doc_data["document"] = {
                    "id": doc.id,
                    "name": doc.name,
                }

                # Extract struct data if available
                if hasattr(doc, 'struct_data') and doc.struct_data:
                    doc_data["document"]["data"] = dict(doc.struct_data)
                elif hasattr(doc, 'json_data') and doc.json_data:
                    doc_data["document"]["data"] = doc.json_data

            results.append(doc_data)

        # Extract facets if available
        facets = []
        if hasattr(response, 'facets'):
            for facet in response.facets:
                facet_data = {
                    "key": facet.key,
                    "values": []
                }
                for value in facet.values:
                    facet_data["values"].append({
                        "value": value.value,
                        "count": value.count
                    })
                facets.append(facet_data)

        return {
            "results": results,
            "total_size": getattr(response, 'total_size', len(results)),
            "facets": facets,
            "query_id": getattr(response, 'attribution_token', None),
        }

    def get_datastore_info(self, search_engine_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a search engine/datastore

        Args:
            search_engine_id: Search engine ID (uses default if not provided)

        Returns:
            Dictionary with datastore metadata
        """
        engine_id = search_engine_id or self.search_engine_id
        if not engine_id:
            raise ValueError("search_engine_id must be provided or set in VERTEX_SEARCH_ENGINE_ID")

        return {
            "project_id": self.project_id,
            "location": self.location,
            "search_engine_id": engine_id,
            "endpoint": f"{self.location}-discoveryengine.googleapis.com" if self.location != "global" else "discoveryengine.googleapis.com"
        }

    def list_documents(
        self,
        search_engine_id: Optional[str] = None,
        page_size: int = 10
    ) -> List[Dict[str, Any]]:
        """
        List documents in a datastore (limited functionality in Discovery Engine)

        Args:
            search_engine_id: Search engine ID
            page_size: Number of documents to return

        Returns:
            List of document metadata

        Note:
            This is a placeholder - actual document listing requires DocumentService client
            and appropriate permissions. For most use cases, use search() instead.
        """
        engine_id = search_engine_id or self.search_engine_id
        if not engine_id:
            raise ValueError("search_engine_id must be provided")

        # This is a simplified implementation
        # For production, use DocumentServiceClient for full document management
        return {
            "message": "Document listing requires DocumentService. Use search() for querying documents.",
            "search_engine_id": engine_id,
            "recommendation": "Use search() with a broad query like '*' to retrieve documents"
        }
