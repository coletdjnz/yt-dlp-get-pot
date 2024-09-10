# Example GetPOT Provider Plugin

import json
from yt_dlp import YoutubeDL

from yt_dlp.networking.common import Request
from yt_dlp.networking.exceptions import RequestError, UnsupportedRequest
from yt_dlp_plugins.extractor.getpot import GetPOTProvider, register_provider, register_preference


@register_provider
class ExampleGetPOTProviderRH(GetPOTProvider):  # ⚠ The class name must end in "RH"
    # Define a unique display name for the provider
    _PROVIDER_NAME = 'example'

    # Supported Innertube clients, as defined in yt_dlp.extractor.youtube.INNERTUBE_CLIENTS
    _SUPPORTED_CLIENTS = ('web', 'web_embedded', 'web_music')

    # Optional: Define the version of the provider. Shown in debug output for debugging purposes.
    VERSION = '0.0.1'

    # ℹ️ If you implementation calls out to an external source not via ydl.urlopen (e.g. through a browser),
    # you should define proxy support with:
    # _SUPPORTED_PROXY_SCHEMES = ('http', ...)
    # _SUPPORTED_FEATURES = (Features.ALL_PROXY, ...)
    # This prevents IP leakage if your implementation does not support proxies or a specific proxy type.
    # You can get the proxies for the request with `self._get_proxies(request)`

    # Optional
    def _validate_get_pot(self, client: str, ydl: YoutubeDL, visitor_data=None, data_sync_id=None, player_url=None, **kwargs):
        # ℹ️ If you need to validate the request before making the request to the external source, do it here.
        # Raise yt_dlp.networking.exceptions.UnsupportedRequest if the request is not valid.
        if data_sync_id:
            raise UnsupportedRequest('Fetching PO Token for accounts is not supported')

    # ℹ️ Implement this method
    def _get_pot(self, client: str, ydl: YoutubeDL, visitor_data=None, data_sync_id=None, player_url=None, **kwargs) -> str:
        # You should use the ydl instance to make requests where possible,
        # as it will handle cookies and other networking settings passed to yt-dlp.
        response = ydl.urlopen(Request('https://example.com/get_pot', data=json.dumps({
            'client': client,
            'visitor_data': visitor_data
        }).encode()))

        # If you need access to the YoutubeIE instance
        # ydl.get_info_extractor('youtube')

        response_json = json.loads(response.read().decode('utf-8'))

        if 'po_token' not in response_json:
            # Any error that is thrown must be a subclass of yt_dlp.networking.exceptions.RequestError
            raise RequestError('Server did not respond with a po_token')

        # Access the logger
        self._logger.debug(f'Got PO Token: {response_json["po_token"]}')

        # return the po_token string
        return response_json['po_token']


# If there are multiple GetPOTProvider request handlers that can handle the same request,
# you can define a preference function to increase/decrease the priority of request handlers.
# By default, all GetPOTProvider request handlers are prioritized when a get-pot: request is made.
@register_preference(ExampleGetPOTProviderRH)
def example_getpot_preference(rh, request):
    # return 100  # add +100 to the priority of this request handler
    return 0  # default priority
