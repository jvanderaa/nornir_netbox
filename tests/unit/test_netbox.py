import json
import os

from nornir.core.deserializer.inventory import Inventory
from nornir_netbox.inventory.netbox import NBInventory, NetboxInventory2

# We need import below to load fixtures
import pytest  # noqa


BASE_PATH = os.path.dirname(__file__)

def get_inv(requests_mock, plugin, pagination, **kwargs):
    if not pagination:
        with open(f"{BASE_PATH}/mocked/devices.json", "r") as f:
            requests_mock.get(
                "http://localhost:8080/api/dcim/devices/?limit=0",
                json=json.load(f),
                headers={"Content-type": "application/json"},
            )
    else:
        for offset in range(3):
            with open(f"{BASE_PATH}/mocked/devices-{offset}.json", "r") as f:
                url = "http://localhost:8080/api/dcim/devices/?limit=0"
                requests_mock.get(
                    f"{url}&offset={offset}" if offset else url,
                    json=json.load(f),
                    headers={"Content-type": "application/json"},
                )
    return plugin.deserialize(**kwargs)

class TestNBInventory(object):
    plugin = NBInventory

    def test_inventory(self, requests_mock):
        inv = get_inv(requests_mock, self.plugin, False)
        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/expected.json", "r"
        ) as f:
            expected = json.load(f)
        assert expected == Inventory.serialize(inv).dict()

    def test_inventory_pagination(self, requests_mock):
        inv = get_inv(requests_mock, self.plugin, False)
        with open(
            f"{BASE_PATH}/{self.plugin.__name__}/expected.json", "r"
        ) as f:
            expected = json.load(f)
        assert expected == Inventory.serialize(inv).dict()

    def test_inventory_transform_function(self, requests_mock):
        inv = get_inv(
            requests_mock,
            self.plugin,
            False,
            transform_function=self.transform_function,
        )
        with open(
            (
                f"{BASE_PATH}/{self.plugin.__name__}/"
                "expected_transform_function.json"
            ),
            "r",
        ) as f:
            expected = json.load(f)
        assert expected == Inventory.serialize(inv).dict()

    @staticmethod
    def transform_function(host):
        vendor_map = {"Cisco": "ios", "Juniper": "junos"}
        host["platform"] = vendor_map[host["vendor"]]


class TestNetboxInventory2(TestNBInventory):
    plugin = NetboxInventory2

    @staticmethod
    def transform_function(host):
        vendor_map = {"Cisco": "ios", "Juniper": "junos"}
        host.platform = vendor_map[host["device_type"]["manufacturer"]["name"]]