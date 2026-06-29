"""
Abstract base for all data-source connectors.

Each connector provides:
  - is_available()  → credentials are configured
  - fetch(**kwargs) → call real API, return list[dict]
  - mock_data()     → return mock list[dict] (always works)
  - get_data()      → smart dispatch: real if flag+creds, else mock
"""

from abc import ABC, abstractmethod
from datetime import datetime


class BaseConnector(ABC):
    connector_id: str = "base"      # matches feature flag suffix, e.g. "GSC" → USE_REAL_GSC
    display_name: str = "Base"

    @abstractmethod
    def is_available(self) -> bool:
        """Return True when all required credentials are present in env."""

    @abstractmethod
    def fetch(self, **kwargs) -> list[dict]:
        """Call the real API and return normalised rows."""

    @abstractmethod
    def mock_data(self, **kwargs) -> list[dict]:
        """Return realistic mock rows for development / CI."""

    def get_data(self, **kwargs) -> dict:
        """
        Dispatch to real API or mock based on feature flag + credential check.
        Always returns: {"source": str, "data": list[dict], "fetched_at": str}
        """
        from config.feature_flags import is_enabled
        flag = f"USE_REAL_{self.connector_id}"
        source = "mock"
        error = None

        if is_enabled(flag):
            if self.is_available():
                try:
                    data = self.fetch(**kwargs)
                    source = "real"
                except Exception as exc:
                    data = self.mock_data(**kwargs)
                    source = "mock_fallback"
                    error = str(exc)
            else:
                data = self.mock_data(**kwargs)
                source = "mock_no_creds"
        else:
            data = self.mock_data(**kwargs)

        result: dict = {
            "connector": self.connector_id,
            "source": source,
            "data": data,
            "row_count": len(data),
            "fetched_at": datetime.now().isoformat(),
        }
        if error:
            result["error"] = error
        return result

    def status(self) -> dict:
        from config.feature_flags import is_enabled
        flag = f"USE_REAL_{self.connector_id}"
        return {
            "connector": self.connector_id,
            "display_name": self.display_name,
            "flag_enabled": is_enabled(flag),
            "credentials_present": self.is_available(),
            "mode": "real" if (is_enabled(flag) and self.is_available()) else "mock",
        }
