"""
Feature flag system — all real-API and SQLite flags default OFF.
Enable via environment variables before starting the process.

  USE_SQLITE=true          → use SQLite instead of JSON files
  USE_REAL_GSC=true        → call real Google Search Console API
  USE_REAL_GA4=true        → call real Google Analytics 4 API
  USE_REAL_NAVER_ADS=true  → call real Naver Ads API
  USE_REAL_KAKAO=true      → call real Kakao Moment API
  USE_REAL_GOOGLE_ADS=true → call real Google Ads API
  BLOCK_HIGH_RISK=true     → block high-risk actions from auto-approval (default ON)
"""

import os

_DEFAULTS: dict[str, bool] = {
    "USE_SQLITE": False,
    "USE_REAL_GSC": False,
    "USE_REAL_GA4": False,
    "USE_REAL_NAVER_ADS": False,
    "USE_REAL_KAKAO": False,
    "USE_REAL_GOOGLE_ADS": False,
    "BLOCK_HIGH_RISK": True,
}


def is_enabled(flag: str) -> bool:
    env = os.getenv(flag, "").strip().lower()
    if env in ("true", "1", "yes"):
        return True
    if env in ("false", "0", "no"):
        return False
    return _DEFAULTS.get(flag, False)


def get_all() -> dict[str, bool]:
    return {k: is_enabled(k) for k in _DEFAULTS}


def require_flag(flag: str, action: str = "") -> None:
    """Raise PermissionError if a safety-critical flag is off."""
    if not is_enabled(flag):
        raise PermissionError(
            f"Feature flag '{flag}' is disabled"
            + (f" — blocked: {action}" if action else "")
        )
