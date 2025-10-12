"""Spreadsheet writer.

Supports writing to Google Sheets using a service account (when
`GOOGLE_SERVICE_ACCOUNT_FILE` and `SPREADSHEET_ID` are provided),
and falls back to appending to a local CSV file.
"""
from __future__ import annotations

import os
import csv
import json
import logging
from typing import Optional

logger = logging.getLogger("checkin-bot.sheets")

try:
    import gspread
    from google.oauth2.service_account import Credentials
except Exception:  # pragma: no cover - optional dependency
    gspread = None
    Credentials = None


SERVICE_ACCOUNT_ENV_FIELDS = {
    "type": "GOOGLE_SERVICE_ACCOUNT_TYPE",
    "project_id": "GOOGLE_SERVICE_ACCOUNT_PROJECT_ID",
    "private_key_id": "GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID",
    "private_key": "GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY",
    "client_email": "GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL",
    "client_id": "GOOGLE_SERVICE_ACCOUNT_CLIENT_ID",
    "auth_uri": "GOOGLE_SERVICE_ACCOUNT_AUTH_URI",
    "token_uri": "GOOGLE_SERVICE_ACCOUNT_TOKEN_URI",
    "auth_provider_x509_cert_url": "GOOGLE_SERVICE_ACCOUNT_AUTH_PROVIDER_X509_CERT_URL",
    "client_x509_cert_url": "GOOGLE_SERVICE_ACCOUNT_CLIENT_X509_CERT_URL",
}


class SheetsWriter:
    """Append check-in rows to a Google Spreadsheet only.

    Row format: timestamp (JST), username
    """

    def __init__(self) -> None:
        self.spreadsheet_id = os.getenv("SPREADSHEET_ID")
        self.service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        self.service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        env_service_account, missing_envs = self._load_service_account_from_env()

        if missing_envs:
            raise RuntimeError(
                "Google Sheetsの設定が不足しています。以下の環境変数を設定してください: " + ", ".join(missing_envs)
            )

        if not (self.spreadsheet_id and (self.service_account_file or self.service_account_json or env_service_account) and gspread is not None):
            raise RuntimeError(
                "Google Sheetsの設定が不足しています。SPREADSHEET_ID, GOOGLE_SERVICE_ACCOUNT_FILE/JSONまたは個別環境変数, gspreadが必要です。"
            )

        service_account_info = None
        if self.service_account_json:
            try:
                service_account_info = json.loads(self.service_account_json)
            except json.JSONDecodeError as exc:  # pragma: no cover - configuration error
                logger.exception("Invalid JSON in GOOGLE_SERVICE_ACCOUNT_JSON: %s", exc)
                raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSONの値が不正なJSONです。")
        elif env_service_account:
            service_account_info = env_service_account

        try:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
            if service_account_info:
                creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)
                if self.service_account_json:
                    logger.info("Using service account credentials from GOOGLE_SERVICE_ACCOUNT_JSON")
                else:
                    logger.info("Using service account credentials from individual environment variables")
            else:
                creds = Credentials.from_service_account_file(self.service_account_file, scopes=scopes)
                logger.info("Using service account file: %s", self.service_account_file)
            gc = gspread.authorize(creds)
            spreadsheet = gc.open_by_key(self.spreadsheet_id)
            self.sheet = spreadsheet.worksheet("シート5")
            logger.info("Connected to Google Spreadsheet: %s (シート5)", self.spreadsheet_id)
        except Exception as exc:
            logger.exception("Failed to connect to Google Sheets: %s", exc)
            raise RuntimeError("Google Sheetsへの接続に失敗しました。設定を確認してください。")

    def append_checkin(self, timestamp: str, username: str) -> None:
        """Append a single checkin entry.

        This function is blocking; callers should run it in a thread if used
        inside an async event loop.
        """
        values = [timestamp, username]
        self.sheet.append_row(values, value_input_option="RAW")
        logger.info("Appended row to Google Sheet: %s", values)

    def _load_service_account_from_env(self) -> tuple[Optional[dict], list[str]]:
        """Return service account info from individual env vars, or missing keys list."""
        env_info = {}
        provided_fields = []
        for field, env_var in SERVICE_ACCOUNT_ENV_FIELDS.items():
            value = os.getenv(env_var)
            if value is None:
                continue
            provided_fields.append(field)
            if field == "private_key":
                env_info[field] = value.replace("\\n", "\n")
            else:
                env_info[field] = value

        if not provided_fields:
            return None, []

        missing_envs = [SERVICE_ACCOUNT_ENV_FIELDS[field] for field in SERVICE_ACCOUNT_ENV_FIELDS if field not in provided_fields]
        if missing_envs:
            return None, missing_envs

        return env_info, []
