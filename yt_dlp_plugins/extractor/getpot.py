from __future__ import annotations

import abc
import functools
import io
import json
import typing

from yt_dlp.networking.common import RequestHandler, Response, Request
from yt_dlp.networking.exceptions import UnsupportedRequest, NoSupportingHandlers, RequestError
from yt_dlp.utils import classproperty
from yt_dlp.YoutubeDL import YoutubeDL


__version__ = '0.3.0'
__all__ = ['GetPOTProvider', 'register_provider', 'register_preference', '__version__']


class GetPOTResponse(Response):
    def __init__(self, url, po_token):
        self.po_token = po_token
        super().__init__(
            fp=io.BytesIO(json.dumps({
                'po_token': po_token,
            }).encode('utf-8')),
            headers={'Content-Type': 'application/json'},
            url=url)


class ProviderLogger:
    def __init__(self, provider_name, logger=None):
        self._logger = logger
        self._provider_name = provider_name

    def format(self, message):
        return f'[GetPOT] {self._provider_name}: {message}'

    def debug(self, message):
        if self._logger:
            self._logger.debug(self.format(message))

    def info(self, message):
        if self._logger:
            self._logger.info(self.format(message))

    def warning(self, message, *, once=False):
        if self._logger:
            self._logger.warning(self.format(message), once=once)

    def error(self, message, *, is_error=True):
        if self._logger:
            self._logger.error(self.format(message), is_error=is_error)


class GetPOTProvider(RequestHandler, abc.ABC):
    _SUPPORTED_URL_SCHEMES = ('get-pot',)
    _PROVIDER_NAME = None
    # Supported Innertube clients, as defined in yt_dlp.extractor.youtube.INNERTUBE_CLIENTS
    _SUPPORTED_CLIENTS = ()

    # Support PO Token contexts. "gvs" (Google Video Server) is the default for backwards compatibility.
    _SUPPORTED_CONTEXTS = ['gvs']

    # Version of the provider. Shown in debug output for debugging purposes.
    VERSION = None

    # If your request handler calls out to an external source (e.g. a browser), and not via ydl, you should define
    # these. They can be used to determine if the request handler supports the features and proxies passed to yt-dlp.
    _SUPPORTED_FEATURES = None
    _SUPPORTED_PROXY_SCHEMES = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = ProviderLogger(self.RH_NAME, self._logger)

    @classproperty
    def RH_NAME(cls):
        return cls._PROVIDER_NAME or cls.RH_KEY.lower()

    def _check_extensions(self, extensions):
        super()._check_extensions(extensions)
        extensions.pop('ydl', None)
        extensions.pop('getpot', None)

    def _validate(self, request: Request):
        super()._validate(request)

        if not isinstance(request.extensions.get('ydl'), YoutubeDL):
            raise UnsupportedRequest('YoutubeDL instance not provided')

        pot_request = request.extensions.get('getpot')
        if not isinstance(pot_request, dict) or 'client' not in pot_request:
            raise UnsupportedRequest('Malformed GetPOT Request')

        pot_request = pot_request.copy()
        client = pot_request.pop('client')

        if client not in self._SUPPORTED_CLIENTS:
            raise UnsupportedRequest(f'Client "{client}" is not supported. Supported clients: {", ".join(self._SUPPORTED_CLIENTS)}')

        context = pot_request.get('context')
        if context and self._SUPPORTED_CONTEXTS and context not in self._SUPPORTED_CONTEXTS:
            raise UnsupportedRequest(f'PO Token context "{context}" is not supported. Supported contexts: {", ".join(self._SUPPORTED_CONTEXTS)}')

        self._validate_get_pot(
            client=client,
            ydl=request.extensions.get('ydl'),
            **pot_request
        )

    def _send(self, request: Request):
        pot_request = request.extensions.get('getpot').copy()
        try:
            pot = self._get_pot(
                client=pot_request.pop('client'),
                ydl=request.extensions.get('ydl'),
                **pot_request
            )
            return GetPOTResponse(request.url, po_token=pot)
        except NoSupportingHandlers as e:
            raise RequestError(cause=e) from e

    def _validate_get_pot(
            self,
            client: str,
            ydl: YoutubeDL,
            visitor_data=None,
            data_sync_id=None,
            session_index=None,
            player_url=None,
            context=None,
            video_id=None,
            ytcfg=None,
            **kwargs
    ):
        """
        Validate and check the GetPOT request is supported.
        :param client: Innertube client, from yt_dlp.extractor.youtube.INNERTUBE_CLIENTS.
        :param ydl: YoutubeDL instance.
        :param visitor_data: Visitor Data.
        :param data_sync_id: Data Sync ID. Only provided if yt-dlp is running with an account.
        :param session_index: Session Index.
        :param player_url: Player URL. Only provided if the client is BotGuard based (requires JS player).
        :param context: PO Token context. "gvs" or "player".
        :param video_id: Video ID.
        :param ytcfg: The ytcfg yt-dlp will use for the client to make Innertube requests.
        :param kwargs: Additional arguments that may be passed in the future.
        :raises UnsupportedRequest: If the request is unsupported.
        """

    @abc.abstractmethod
    def _get_pot(
            self,
            client: str,
            ydl: YoutubeDL,
            visitor_data=None,
            data_sync_id=None,
            session_index=None,
            player_url=None,
            context=None,
            video_id=None,
            ytcfg=None,
            **kwargs
    ) -> str:
        """
        Get a PO Token
        :param client: Innertube client, from yt_dlp.extractor.youtube.INNERTUBE_CLIENTS.
        :param ydl: YoutubeDL instance.
        :param visitor_data: Visitor Data.
        :param data_sync_id: Data Sync ID. Only provided if yt-dlp is running with an account.
        :param session_index: Session Index.
        :param player_url: Player URL. Only provided if the client is BotGuard based (requires JS player).
        :param context: PO Token context. "gvs" or "player".
        :param video_id: Video ID.
        :param ytcfg: The ytcfg yt-dlp will use for the client to make Innertube requests.
        :param kwargs: Additional arguments that may be passed in the future.
        :returns: PO Token
        :raises RequestError: If the request fails.
        """


if typing.TYPE_CHECKING:
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
