from __future__ import annotations

import typing

from yt_dlp.extractor.youtube import YoutubeIE
from yt_dlp.networking import Request
from yt_dlp.networking.exceptions import NoSupportingHandlers, RequestError
from yt_dlp.utils import join_nonempty

if typing.TYPE_CHECKING:
    from yt_dlp.YoutubeDL import YoutubeDL
    from yt_dlp.networking.common import RequestDirector

from yt_dlp_plugins.extractor.getpot import __version__


class _GetPOTClient(YoutubeIE, plugin_name='GetPOT'):
    """
    Plugin to inject GetPOT request into the YouTube extractor.
    """

    def set_downloader(self, downloader: YoutubeDL):
        super().set_downloader(downloader)
        if downloader:
            downloader.write_debug(f'GetPOT plugin version {__version__}', only_once=True)
            self._provider_rd: RequestDirector = self._downloader.build_request_director(
                YoutubeIE._GETPOT_PROVIDERS.values(), YoutubeIE._GETPOT_PROVIDER_PREFERENCES)

            display_list = ", ".join(
                join_nonempty(rh.RH_NAME, rh.VERSION) for rh in self._provider_rd.handlers.values()
            ) or "none"

            downloader.write_debug(f'[GetPOT] PO Token Providers: {display_list}', only_once=True)

    def _fetch_po_token(
            self,
            client,
            context=None,
            **kwargs
        ):
        # use any existing implementation
        pot = super()._fetch_po_token(
            client=client,
            context=context,
            **kwargs
        )

        if pot:
            return pot

        # default to gvs for compatibility with older yt-dlp versions
        context = (context or 'gvs').lower()

        params = {
            'client': client,
            'context': context,
            **kwargs
        }

        try:
            self._downloader.write_debug(f'[GetPOT] Fetching {context} PO Token for {client} client')
            pot_response = self._parse_json(
                self._provider_rd.send(Request('get-pot:', extensions={'ydl': self._downloader, 'getpot': params})).read(),
                video_id='GetPOT')

        except NoSupportingHandlers:
            self._downloader.write_debug(f'[GetPOT] No {context} PO Token provider available for {client} client')
            return

        except RequestError as e:
            self._downloader.report_warning(f'[GetPOT] Failed to fetch {context} PO Token for {client} client: {e}')
            return

        pot = pot_response.get('po_token')
        if not pot:
            self._downloader.report_warning(f'[GetPOT] Invalid GetPOT Response: Missing po_token')
            return

        return pot
