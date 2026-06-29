import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
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
