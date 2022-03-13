from aiohttp import ClientSession, ClientResponse
from .exceptions import InvalidResponse, ApiError, InternalError, Throttle, UnknownError


def splitter(data: list):
    if data is None:
        return None
    return ','.join(data)


class Client:
    def __init__(self, api_key, api_version=2):
        self.__session = ClientSession(base_url='https://block.io')
        self.base_path = f'/api/v{api_version}/'
        self.api_key = api_key

    @staticmethod
    def __check_errors(response: dict, status: int):
        if 'status' not in response.keys():
            raise InvalidResponse("Failed, invalid response received from Block.io", response)
        elif response['status'] == 'fail':
            exception = ApiError('Request failed! See param error in ApiError exception', response)
            exception.error = response['data']['error_message']
            raise exception
        elif 500 <= status <= 599:
            raise InternalError('API call to Block.io failed externally')
        elif 419 <= status <= 420:
            raise Throttle("API call got throttled by rate limits at Block.io", response)
        elif not (200 <= status <= 299):
            raise UnknownError("Unknown error occurred when querying Block.io", response)

    @staticmethod
    async def __prepare_response(response: ClientResponse) -> dict:
        status = response.status
        response = await response.json()

        Client.__check_errors(response, status)

        return response

    async def __get(self, url, params: dict = None):
        if params is None:
            params = {}
        for key in list(params):
            if params[key] is None:
                params.pop(key)

        params['api_key'] = self.api_key

        return await self.__prepare_response(
            await self.__session.get(self.base_path + url, params=params)
        )

    async def __post(self, url, data: dict):
        return await self.__prepare_response(
            await self.__session.post(self.base_path + url, params={'api_key': self.api_key}, json=data)
        )

    async def get_new_address(self, label: str = None, address_type: str = None):
        return await self.__get(
            'get_new_address',
            {
                'label': label,
                'address_type': address_type
            }
        )

    async def get_balance(self):
        return await self.__get(
            'get_balance'
        )

    async def get_my_addresses(self, page: int = None):
        return await self.__get(
            'get_my_addresses',
            {
                'page': page
            }
        )

    async def get_address_balance(self, addresses: list = None, labels: list = None):
        return await self.__get(
            'get_address_balance',
            {
                'addresses': splitter(addresses),
                'labels': splitter(labels)
            }
        )

    async def prepare_transaction(self, amounts: list, to_addresses: list = None,
                                  to_labels: list = None, priority: str = None, custom_network_fee: str = None,
                                  from_addresses: list = None, from_labels: list = None):

        return await self.__get(
            'prepare_transaction',
            {
                'amounts': splitter(amounts),
                'to_addresses': splitter(to_addresses),
                'to_labels': splitter(to_labels),
                'priority': priority,
                'custom_network_fee': custom_network_fee,
                'from_addresses': splitter(from_addresses),
                'from_labels': splitter(from_labels),

            }
        )

    async def decode_raw_transaction(self, tx_hex: str):
        return await self.__get(
            'decode_raw_transaction',
            {
                'tx_hex': tx_hex
            }
        )

    async def get_account_info(self):
        return await self.__get(
            'get_account_info'
        )

    async def is_valid_address(self, address: str):
        return await self.__get(
            'is_valid_address',
            {
                'address': address
            }
        )

    async def get_raw_transaction(self, txid):
        return await self.__get(
            'get_raw_transaction',
            {
                'txid': txid
            }
        )

    async def get_transactions(self, _type: str = 'received', before_tx=None, addresses: list = None,
                               user_ids: list = None, labels: list = None):
        return await self.__get(
            'get_transactions',
            {
                'type': _type,
                'before_tx': before_tx,
                'addresses': splitter(addresses),
                'user_ids': splitter(user_ids),
                'labels': splitter(labels)
            }
        )

    async def get_current_price(self, price_base=None):
        return await self.__get(
            'get_current_price',
            {
                'price_base': price_base
            }
        )

    async def get_my_archived_addresses(self, page: int = None):
        return await self.__get(
            'get_my_archived_addresses',
            {
                'page': page
            }
        )

    async def unarchive_addresses(self, addresses: list = None, labels: list = None):
        return await self.__get(
            'unarchive_addresses',
            {
                'addresses': splitter(addresses),
                'labels': splitter(labels)
            }
        )

    async def archive_addresses(self, addresses: list = None, labels: list = None):
        return await self.__get(
            'archive_addresses',
            {
                'addresses': splitter(addresses),
                'labels': splitter(labels)
            }
        )

    async def get_network_fee_estimate(self, amounts: list, to_addresses: list):
        return await self.__get(
            'get_network_fee_estimate',
            {
                'amounts': splitter(amounts),
                'to_addresses': splitter(to_addresses)
            }
        )

    async def func_name(self, tx_type: str, tx_hex: str, signatures: list):
        return await self.__post(
            'submit_transaction',
            {
                'tx_type': tx_type,
                'tx_hex': tx_hex,
                'signatures': signatures
            }
        )
