import requests
from raiblocks.models import Account, Wallet, PublicKey


def preprocess_account(account_string):
    return Account(account_string)


def preprocess_wallet(wallet_string):
    return Wallet(wallet_string)


def preprocess_public_key(public_key_string):
    return PublicKey(public_key_string)


def preprocess_strbool(value):
    return value and 'true' or 'false'


def preprocess_int(integer_string):
    return str(int(integer_string))


class Client(object):
    """ RaiBlocks node RPC client """

    def __init__(self, host=None, session=None):
        """
        Initialize the RaiBlocks RPC client

        :param host: location of the RPC server eg. http://localhost:7076
        :param session: optional `requests` session to use for this client
        """
        if not host:
            host = 'http://localhost:7076'

        if not session:
            session = requests.Session()

        self._session = session
        self.host = host

    def call(self, action, params=None):
        params = params or {}

        params['action'] = action

        try:
            resp = self._session.post(self.host, json=params)
        except Exception:
            raise

        return resp.json()

    def account_balance(self, account):
        """
        Returns how many RAW is owned and how many have not yet been received
        by **account**

        :type account: str

        >>> rpc.account_balance(
        ...     account="xrb_3e3j5tkog48pnny9dmfzj1r16pg8t1e76dz5tmac6iq689wyjfpi00000000"
        ... )
        {
          "balance": 10000,
          "pending": 10000
        }

        """

        account = preprocess_account(account)

        payload = {
            "account": account,
        }

        resp = self.call('account_balance', payload)

        return {
            k: int(v) for k, v in resp.items()
        }

    def account_block_count(self, account):
        """
        Get number of blocks for a specific **account**

        :type account: str

        >>> rpc.account_block_count(account="xrb_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3")
        19

        """

        account = preprocess_account(account)

        payload = {
            "account": account,
        }

        resp = self.call('account_block_count', payload)

        return int(resp['block_count'])

    def account_info(self, account, representative=False, weight=False,
                     pending=False):
        """
        Returns frontier, open block, change representative block, balance,
        last modified timestamp from local database & block count for
        **account**

        :type account: str
        :type representative: bool
        :type weight: bool
        :type pending: bool

        >>> rpc.account_info(
        ...     account="xrb_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3"
        ... )
        {
          "frontier": "FF84533A571D953A596EA401FD41743AC85D04F406E76FDE4408EAED50B473C5",
          "open_block": "991CF190094C00F0B68E2E5F75F6BEE95A2E0BD93CEAA4A6734DB9F19B728948",
          "representative_block": "991CF190094C00F0B68E2E5F75F6BEE95A2E0BD93CEAA4A6734DB9F19B728948",
          "balance": "235580100176034320859259343606608761791",
          "modified_timestamp": "1501793775",
          "block_count": "33"
        }

        """

        account = preprocess_account(account)

        payload = {
            "account": account,
        }

        if representative:
            payload['representative'] = preprocess_strbool(representative)
        if weight:
            payload['weight'] = preprocess_strbool(weight)
        if pending:
            payload['pending'] = preprocess_strbool(pending)

        resp = self.call('account_info', payload)

        for key in ('modified_timestamp', 'block_count', 'balance', 'pending', 'weight'):
            if key in resp:
                resp[key] = int(resp[key])

        return resp

    def account_create(self, wallet):
        """
        Creates a new account, insert next deterministic key in **wallet**

        :type wallet: str

        .. enable_control required

        >>> rpc.account_create(
        ...     wallet="000D1BAEC8EC208142C99059B393051BAC8380F9B5A2E6B2489A277D81789F3F"
        ... )
        "xrb_3e3j5tkog48pnny9dmfzj1r16pg8t1e76dz5tmac6iq689wyjfpi00000000"

        """

        wallet = preprocess_wallet(wallet)

        payload = {
            "wallet": wallet,
        }

        resp = self.call('account_create', payload)

        return resp['account']

    def account_get(self, key):
        """
        Get account number for the **public key**

        :type key: str

        >>> rpc.account_get(
        ...    key="3068BB1CA04525BB0E416C485FE6A67FD52540227D267CC8B6E8DA958A7FA039"
        ... )
        "xrb_1e5aqegc1jb7qe964u4adzmcezyo6o146zb8hm6dft8tkp79za3sxwjym5rx"

        """

        key = preprocess_public_key(key)

        payload = {
            "key": key,
        }

        resp = self.call('account_get', payload)

        return resp['account']

    def account_history(self, account, count):
        """
        Reports send/receive information for a **account**

        :type account: str
        :type count: int

        >>> rpc.account_history(
        ...     account="xrb_3e3j5tkog48pnny9dmfzj1r16pg8t1e76dz5tmac6iq689wyjfpi00000000",
        ...     count=1
        ... )
        [
            {
              "hash": "000D1BAEC8EC208142C99059B393051BAC8380F9B5A2E6B2489A277D81789F3F",
              "type": "receive",
              "account": "xrb_3e3j5tkog48pnny9dmfzj1r16pg8t1e76dz5tmac6iq689wyjfpi00000000",
              "amount": 100000000000000000000000000000000
            }
        ]

        """

        account = preprocess_account(account)
        count = preprocess_int(count)

        payload = {
            "account": account,
            "count": count,
        }

        resp = self.call('account_history', payload)
        history = resp.get('history') or []

        for entry in history:
            entry['amount'] = int(entry['amount'])

        return history

    def account_list(self, wallet):
        """
        Lists all the accounts inside **wallet**

        :type wallet: str

        >>> rpc.account_list(
        ...     wallet="000D1BAEC8EC208142C99059B393051BAC8380F9B5A2E6B2489A277D81789F3F"
        ... )
        [
            "xrb_3e3j5tkog48pnny9dmfzj1r16pg8t1e76dz5tmac6iq689wyjfpi00000000"
        ]

        """

        wallet = preprocess_wallet(wallet)

        payload = {
            "wallet": wallet,
        }

        resp = self.call('account_list', payload)

        return resp.get('accounts') or []

    def version(self):
        """
        Returns the node's RPC version

        >>> rpc.version()
        {
            "rpc_version": 1,
            "store_version": 10,
            "node_vendor": "RaiBlocks 9.0"
        }

        """

        resp = self.call('version')

        for key in ('rpc_version', 'store_version'):
            resp[key] = int(resp[key])

        return resp

    def stop(self):
        """
        Stop the node

        .. enable_control required

        >>> rpc.stop()
        True

        """

        resp = self.call('stop')

        return 'success' in resp
