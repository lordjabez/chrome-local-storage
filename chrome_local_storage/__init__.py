__version__ = '0.5.1'


import requests
import trio
import trio_cdp


class BrowserConnectionError(Exception):
    """Exception thrown when browser connectivity cannot be established."""
    def __init__(self, host):
        message = f'Could not find tabs on {host} with debugging URLs. Is Chrome running with debugging enabled?'
        super().__init__(message)


class PageNotFoundError(Exception):
    """Exception thrown when no matching URL is found."""
    def __init__(self, url=None):
        message = f'Could not match an open URL to {url}. Is the page open in Chrome?'
        super().__init__(message)


class KeyNotFoundError(Exception):
    """Exception thrown when the key is not found in local storage."""
    def __init__(self, key):
        message = f'Could not find key {key} in local storage.'
        super().__init__(message)


class KeyNotSetError(Exception):
    """Exception thrown when setting the key in local storage fails."""
    def __init__(self, key):
        message = f'Could not set key {key} in local storage.'
        super().__init__(message)


class ChromeLocalStorage():
    """Interact with Google Chrome local storage."""

    def _get_debugger_url(self, host):
        try:
            tabs = requests.get(f'http://{host}/json').json()
            return next(t['webSocketDebuggerUrl'] for t in tabs if 'webSocketDebuggerUrl' in t)
        except Exception:
            raise BrowserConnectionError()

    async def _get_ids(self, connection, target):
        async with connection.open_session(target.target_id):
            resource_tree = await trio_cdp.page.get_resource_tree()
            security_origin = resource_tree.frame.security_origin
            storage_id = trio_cdp.dom_storage.StorageId(security_origin, True)
        return (target.target_id, storage_id)

    async def _build_id_map(self, host, port):
        async with trio_cdp.open_cdp(self._debugger_url) as connection:
            targets = await trio_cdp.target.get_targets()
            targets_with_url = (t for t in targets if hasattr(t, 'url'))
            self._id_map = [(t.url, await self._get_ids(connection, t)) for t in targets_with_url]

    async def _get_ids_for_url(self, url):
        try:
            return next(i for u, i in self._id_map if url in u)
        except Exception:
            raise PageNotFoundError(url)

    async def _get_storage_item(self, url, key):
        target_id, storage_id = await self._get_ids_for_url(url)
        async with trio_cdp.open_cdp(self._debugger_url) as connection:
            async with connection.open_session(target_id):
                try:
                    storage_items = await trio_cdp.dom_storage.get_dom_storage_items(storage_id)
                    return next(i[1] for i in storage_items if i[0] == key)
                except Exception:
                    raise KeyNotFoundError(key)

    async def _set_storage_item(self, url, key, value):
        target_id, storage_id = await self._get_ids_for_url(url)
        async with trio_cdp.open_cdp(self._debugger_url) as connection:
            async with connection.open_session(target_id):
                try:
                    await trio_cdp.dom_storage.set_dom_storage_item(storage_id, key, value)
                except Exception:
                    raise KeyNotSetError(key)

    def get(self, url, key):
        """
        Get an item from local storage.

        :param url: Get item from page whose URL contains this value
        :param key: Key of local storage to get
        :return: Value of local storage item
        """
        return trio.run(self._get_storage_item, url, key)

    def set(self, url, key, value):
        """
        Set an item in local storage.

        :param url: Set item on page whose URL contains this value
        :param key: Key of local storage to set
        :param value: Value to put in local storage
        """
        trio.run(self._set_storage_item, url, key, value)

    def __init__(self, host='localhost', port=9222):
        """
        Construct an instance of the class.

        :param host: hostname running the Chrome debugger, defaults to localhost
        :param port: port running the Chrome debugger, defaults to 9222
        """
        self._debugger_url = self._get_debugger_url(f'{host}:{port}')
        trio.run(self._build_id_map, host, port)
