import logging
import re

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.discovery_cache.file_cache import Cache

logger = logging.getLogger(__name__)


def parse_row_from_range(range_str: str) -> int:
    row_id_str = range_str.split('!')[-1].split(':')[0]
    return int(re.sub(r'[a-zA-Z]', '', row_id_str))


class GoogleSheetsApiService:
    def __init__(
        self,
        creds_file: str,
        discovery_url: str,
        service_name: str,
        version: str,
        scopes: list[str],
    ):
        self.creds_file = creds_file
        self.scopes = scopes
        self.discovery_url = discovery_url
        self.service_name = service_name
        self.version = version
        self.creds = self.get_creds()

    def get_creds(self):
        creds = service_account.Credentials.from_service_account_file(
            self.creds_file,
            scopes=self.scopes,
        )
        return creds

    def build_service(self):
        try:
            service = build(
                self.service_name,
                self.version,
                credentials=self.creds,
                cache=Cache(max_age=30),
            )
        except Exception as exc:
            logger.exception(exc)
            service = build(
                self.service_name,
                self.version,
                discoveryServiceUrl=self.discovery_url,
                credentials=self.creds,
                cache=Cache(max_age=30),
            )
        return service.spreadsheets()

    def get_range(self, spreadsheet_id: str, sheet_name: str, sheet_range: str) -> list[str]:
        try:
            service = self.build_service()
            result = service.values().get(
                spreadsheetId=spreadsheet_id,
                range=sheet_name + '!' + sheet_range,
            ).execute()
            return result.get('values', [])
        except Exception as exc:
            logger.exception(exc)
            return []

    def get_ranges(self, spreadsheet_id: str, ranges: list[tuple[str, str]]) -> list[list[str]]:
        try:
            service = self.build_service()
            result = service.values().batchGet(
                spreadsheetId=spreadsheet_id,
                ranges=[k + '!' + v for k, v in ranges]
            ).execute()
            values_ranges = []
            for values_range in result.get('valueRanges', []):
                values = values_range.get('values', [])
                values_list = [v for v in values if v != []]
                values_ranges.append(values_list)
            return values_ranges
        except Exception as exc:
            logger.exception(exc)
            return []

    def update_one(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        sheet_range: str,
        data: list[list[str]],
    ) -> bool:
        try:
            service = self.build_service()
            body = {'values': [data]}
            service.values().update(
                spreadsheetId=spreadsheet_id,
                range=sheet_name + '!' + sheet_range,
                valueInputOption='USER_ENTERED',
                body=body,
            ).execute()
        except Exception as exc:
            logger.exception(exc)
            return False
        return True

    def update_many(
        self,
        spreadsheet_id: str,
        data: dict[str, dict[str, list[list[str]]]],
    ) -> bool:
        try:
            service = self.build_service()
            body = {'data': [], 'valueInputOption': 'USER_ENTERED'}
            for sheet_name, sheet_data in data.items():
                for sheet_range, sheet_values in sheet_data.items():
                    body['data'].append({
                        'range': sheet_name + '!' + sheet_range,
                        'values': sheet_values,
                    })
            service.values().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body,
            ).execute()
        except Exception as exc:
            logger.exception(exc)
            return False
        return True

    def append(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        sheet_range: str,
        data: list[list[str]],
        return_row_id: bool = False,
    ) -> bool:
        try:
            service = self.build_service()
            body = {'values': data}
            result = service.values().append(
                spreadsheetId=spreadsheet_id,
                range=sheet_name + '!' + sheet_range,
                valueInputOption='USER_ENTERED',
                body=body,
            ).execute()
            if return_row_id:
                return parse_row_from_range(result['updates']['updatedRange'])
        except Exception as exc:
            logger.exception(exc)
            return False
        return True
