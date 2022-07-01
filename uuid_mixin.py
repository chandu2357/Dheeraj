import base64
from collections import defaultdict

from dash_common.constants.mgs_mobile_gateway_constants import UuidConstants


def decode_account_uuid(uuid):
    acc_uuid_dict = defaultdict(str)
    if uuid:
        values_string = as_decoded_base64_string(uuid)
        splitted_values = values_string.split(UuidConstants.SPLITTER)

        acc_uuid_dict = {UuidConstants.ACCOUNTID: splitted_values[0],
                         UuidConstants.ACCTTYPE: splitted_values[1],
                         UuidConstants.INSTTYPE: splitted_values[2],
                         "instNumber": splitted_values[3],
                         'symbol': splitted_values[4],
                         UuidConstants.MANAGEDACCOUNTTYPE: splitted_values[5]}
    return acc_uuid_dict


class UuidMixin:
    """
    Mixin of tools related to base64-encoded strings
    """

    def get_uuid(self, **encode_args):
        """Get uuid from encode_args"""
        values = list(encode_args.values())
        values_str = str("|".join(values))
        uuid = self.as_base64_string(values_str)
        return uuid

    def get_account_id_from_uuid(self, uuid):
        uuid_dict = decode_account_uuid(uuid)
        return uuid_dict[UuidConstants.ACCOUNTID]

    def encode_account_uuid(self, id_dict) -> str:
        values = id_dict.values()
        encoded_string = self.encode_from_values_list(values)
        return encoded_string

    def encode_from_values_list(self, values) -> str:
        splitter = UuidConstants.SPLITTER
        prepared_string = splitter.join(values)
        encoded_string: str = self.as_base64_string(prepared_string)
        return encoded_string

    @staticmethod
    def as_base64_string(value: str) -> str:
        byte_string = value.encode()
        base64_byte_string = base64.b64encode(byte_string)
        base64_string: str = base64_byte_string.decode(UuidConstants.CODING)
        return base64_string


def as_decoded_base64_string(value) -> str:
    byte_str = bytes(value, encoding=UuidConstants.CODING)
    bytes_decoded = base64.b64decode(byte_str)
    str_decoded = bytes_decoded.decode(UuidConstants.CODING)
    return str_decoded


def get_uuid(self, **encode_args):
    """Get uuid from encode_args"""
    values = list(encode_args.values())
    values_str = str("|".join(values))
    uuid = self.as_base64_string(values_str)
    return uuid
