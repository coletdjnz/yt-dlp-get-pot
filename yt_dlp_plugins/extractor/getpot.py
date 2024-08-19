from __future__ import annotations

import abc
import base64
import functools
import io
import json
import typing
import urllib.parse

from yt_dlp.networking.common import RequestHandler, Response, Request
from yt_dlp.networking.exceptions import UnsupportedRequest
from yt_dlp.utils import parse_qs, classproperty

__version__ = '0.0.2'
__all__ = ['GetPOTProvider', 'register_provider', 'register_preference']


class GetPOTResponse(Response):
    def __init__(self, url, po_token):
        self.po_token = po_token
        super().__init__(
            fp=io.BytesIO(json.dumps({
                'po_token': po_token,
            }).encode('utf-8')),
            headers={'Content-Type': 'application/json'},
            url=url)


class GetPOTProvider(RequestHandler, abc.ABC):
    _SUPPORTED_URL_SCHEMES = ('get-pot',)
    _PROVIDER_NAME = None
    # Supported Innertube clients, as defined in yt_dlp.extractor.youtube.INNERTUBE_CLIENTS
    _SUPPORTED_CLIENTS = ()

    # If your request handler calls out to an external source (e.g. a browser), and not via ydl, you should define
    # these. They can be used to determine if the request handler supports the features and proxies passed to yt-dlp.
    _SUPPORTED_FEATURES = None
    _SUPPORTED_PROXY_SCHEMES = None

    @classproperty
    def RH_NAME(cls):
        return f'getpot-{cls._PROVIDER_NAME or cls.RH_KEY.lower()}'

    def _check_extensions(self, extensions):
        super()._check_extensions(extensions)
        extensions.pop('ydl', None)

    def _parse_getpot_request(self, request):
        query = parse_qs(request.url)['q'][0]
        return json.loads(base64.urlsafe_b64decode(query.encode('utf-8')).decode('utf-8'))

    def _validate(self, request):
        super()._validate(request)
        try:
            pot_request = self._parse_getpot_request(request)
        except Exception:
            raise UnsupportedRequest('Malformed GetPOT request')

        if pot_request['client'] not in self._SUPPORTED_CLIENTS:
            raise UnsupportedRequest(f'Client {pot_request["client"]} is not supported')

        self._validate_get_pot(
            client=pot_request.pop('client', None),
            ydl=request.extensions.get('ydl'),
            **pot_request
        )

    def _send(self, request: Request):
        pot_request = self._parse_getpot_request(request)

        pot = self._get_pot(
            client=pot_request.pop('client', None),
            ydl=request.extensions.get('ydl'),
            **pot_request
        )

        return GetPOTResponse(request.url, po_token=pot)

    def _validate_get_pot(self, client: str, ydl: YoutubeDL, visitor_data=None, data_sync_id=None, player_url=None,
                          **kwargs):
        """
        Validate the GetPOT request.
        :param client: Innertube client, from yt_dlp.extractor.youtube.INNERTUBE_CLIENTS.
        :param ydl: YoutubeDL instance.
        :param visitor_data: Visitor Data.
        :param data_sync_id: Data Sync ID. Only provided if yt-dlp is running with an account.
        :param player_url: Player URL. Only provided if the client is BotGuard based (requires JS player).
        :param kwargs: Additional arguments that may be passed in the future.
        :raises UnsupportedRequest: If the request is unsupported.
        """

    @abc.abstractmethod
    def _get_pot(self, client: str, ydl: YoutubeDL, visitor_data=None, data_sync_id=None, player_url=None,
                 **kwargs) -> str:
        """
        Get a PO Token
        :param client: Innertube client, from yt_dlp.extractor.youtube.INNERTUBE_CLIENTS.
        :param ydl: YoutubeDL instance.
        :param visitor_data: Visitor Data.
        :param data_sync_id: Data Sync ID. Only provided if yt-dlp is running with an account.
        :param player_url: Player URL. Only provided if the client is BotGuard based (requires JS player).
        :param kwargs: Additional arguments that may be passed in the future.
        :returns: PO Token
        :raises RequestError: If the request fails.
        """


if typing.TYPE_CHECKING:
    from yt_dlp.YoutubeDL import YoutubeDL

    Preference = typing.Callable[[GetPOTProvider, Request], int]

from yt_dlp.extractor.youtube import YoutubeIE

if not hasattr(YoutubeIE, '_GETPOT_PROVIDER_PREFERENCES'):
    YoutubeIE._GETPOT_PROVIDER_PREFERENCES = set()

if not hasattr(YoutubeIE, '_GETPOT_PROVIDERS'):
    YoutubeIE._GETPOT_PROVIDERS = {}


def register_preference(*handlers: type[GetPOTProvider]):
    assert all(issubclass(handler, GetPOTProvider) for handler in handlers)

    def outer(preference: Preference):
        @functools.wraps(preference)
        def inner(handler, *args, **kwargs):
            if not handlers or isinstance(handler, handlers):
                return preference(handler, *args, **kwargs)
            return 0

        YoutubeIE._GETPOT_PROVIDER_PREFERENCES.add(inner)
        return inner

    return outer


def register_provider(provider):
    """Register a GetPOTProvider class"""
    assert issubclass(provider, GetPOTProvider), f'{provider} must be a subclass of GetPOTProvider'
    assert provider.RH_KEY not in YoutubeIE._GETPOT_PROVIDERS, f'Provider {provider.RH_KEY} already registered'
    YoutubeIE._GETPOT_PROVIDERS[provider.RH_KEY] = provider
    return provider


@register_preference(GetPOTProvider)
def get_pot_preference(_, request):
    if urllib.parse.urlparse(request.url).scheme == 'get-pot':
        return 1000
    return -1000
