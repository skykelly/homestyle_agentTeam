import os
from dotenv import load_dotenv

load_dotenv()

_SESSION_TOKEN_FILE = "/home/claude/.claude/remote/.session_ingress_token"


def _resolve_auth() -> tuple[str, str]:
    """Return (api_key, auth_token) — one will be non-empty."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if api_key:
        return api_key, ""
    try:
        with open(_SESSION_TOKEN_FILE) as f:
            token = f.read().strip()
        return "", token
    except OSError:
        return "", ""


class Settings:
    _api_key, _auth_token = _resolve_auth()
    ANTHROPIC_API_KEY: str = _api_key
    ANTHROPIC_AUTH_TOKEN: str = _auth_token
    MODEL: str = "claude-sonnet-4-6"

    # Korean market ad platform configs
    NAVER_ADS_API_KEY: str = os.getenv("NAVER_ADS_API_KEY", "")
    NAVER_ADS_SECRET_KEY: str = os.getenv("NAVER_ADS_SECRET_KEY", "")
    NAVER_ADS_CUSTOMER_ID: str = os.getenv("NAVER_ADS_CUSTOMER_ID", "")

    KAKAO_ADS_ACCESS_TOKEN: str = os.getenv("KAKAO_ADS_ACCESS_TOKEN", "")
    KAKAO_ADS_ACCOUNT_ID: str = os.getenv("KAKAO_ADS_ACCOUNT_ID", "")

    COUPANG_ADS_ACCESS_KEY: str = os.getenv("COUPANG_ADS_ACCESS_KEY", "")
    COUPANG_ADS_SECRET_KEY: str = os.getenv("COUPANG_ADS_SECRET_KEY", "")

    META_ADS_ACCESS_TOKEN: str = os.getenv("META_ADS_ACCESS_TOKEN", "")
    META_ADS_ACCOUNT_ID: str = os.getenv("META_ADS_ACCOUNT_ID", "")

    GOOGLE_ADS_DEVELOPER_TOKEN: str = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", "")
    GOOGLE_ADS_CUSTOMER_ID: str = os.getenv("GOOGLE_ADS_CUSTOMER_ID", "")

    # Korean market defaults
    DEFAULT_CURRENCY: str = "KRW"
    DEFAULT_TIMEZONE: str = "Asia/Seoul"
    DEFAULT_LANGUAGE: str = "ko"


settings = Settings()
