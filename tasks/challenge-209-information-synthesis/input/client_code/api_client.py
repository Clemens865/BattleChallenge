"""API Client for DataStore service (v1 — BROKEN after API migration)."""
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET


class DataStoreClient:
    """Client for the DataStore REST API."""

    BASE_URL = "https://api.datastore.example.com/v1"

    def __init__(self, api_key):
        self.api_key = api_key
        self.rate_limit_remaining = None

    def _build_headers(self):
        return {
            "X-API-Key": self.api_key,
            "Accept": "application/xml",
            "Content-Type": "application/xml",
        }

    def _make_request(self, method, path, data=None):
        url = f"{self.BASE_URL}{path}"
        headers = self._build_headers()
        if data:
            xml_data = self._dict_to_xml(data)
            req = urllib.request.Request(url, data=xml_data.encode(), headers=headers, method=method)
        else:
            req = urllib.request.Request(url, headers=headers, method=method)
        response = urllib.request.urlopen(req)
        self.rate_limit_remaining = response.headers.get("X-RateLimit")
        body = response.read().decode()
        return self._parse_xml(body)

    def _dict_to_xml(self, data):
        root = ET.Element("request")
        for key, value in data.items():
            child = ET.SubElement(root, key)
            child.text = str(value)
        return ET.tostring(root, encoding="unicode")

    def _parse_xml(self, xml_string):
        root = ET.fromstring(xml_string)
        result = {}
        for child in root:
            result[child.tag] = child.text
        return result

    def list_items(self, offset=0, limit=20):
        path = f"/items?offset={offset}&limit={limit}"
        return self._make_request("GET", path)

    def get_item(self, item_id):
        path = f"/items/{item_id}"
        return self._make_request("GET", path)

    def create_item(self, name, description, price):
        data = {"name": name, "description": description, "price": price}
        return self._make_request("POST", "/items", data)

    def update_item(self, item_id, **kwargs):
        return self._make_request("PUT", f"/items/{item_id}", kwargs)

    def delete_item(self, item_id):
        return self._make_request("DELETE", f"/items/{item_id}")
