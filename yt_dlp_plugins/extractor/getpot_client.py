from __future__ import annotations

import base64
import json
import typing

from yt_dlp.extractor.youtube import YoutubeIE
from yt_dlp.networking import Request
from yt_dlp.networking.exceptions import NoSupportingHandlers, RequestError
from yt_dlp.utils import update_url_query, ExtractorError

if typing.TYPE_CHECKING:
    from yt_dlp.YoutubeDL import YoutubeDL
    from yt_dlp.networking.common import RequestDirector


class _GetPOTClient(YoutubeIE, plugin_name='GetPOT'):
    """
    Plugin to inject GetPOT request into the YouTube extractor.
    """

    def set_downloader(self, downloader: YoutubeDL):
        super().set_downloader(downloader)
        if downloader:
            self._provider_rd: RequestDirector = self._downloader.build_request_director(
                YoutubeIE._GETPOT_PROVIDERS.values(), YoutubeIE._GETPOT_PROVIDER_PREFERENCES)
            downloader.write_debug(
                f'PO Token Providers: {", ".join(rh.RH_NAME for rh in self._provider_rd.handlers.values())}',
                only_once=True)

    def _fetch_po_token(self, client, visitor_data=None, data_sync_id=None, player_url=None, **kwargs):
        # use any existing implementation
        pot = super()._fetch_po_token(
            client=client,
            visitor_data=visitor_data,
            data_sync_id=data_sync_id,
            player_url=player_url,
            **kwargs
        )

        if pot:
            return pot

        params = {
            'client': client,
            'visitor_data': visitor_data,
            'data_sync_id': data_sync_id,
            'player_url': player_url,
            **kwargs
        }

        try:
            self.to_screen(f'GetPOT: Fetching PO Token for {client} client')
            pot_response = self._parse_json(
                self._provider_rd.send(Request('get-pot:', extensions={'ydl': self._downloader, 'getpot': params})).read(),
                video_id='GetPOT')

        except NoSupportingHandlers:
            self.write_debug(f'No GetPOT handler available for client {client}')
            return

        except (ExtractorError, RequestError) as e:
            self.report_warning(f'Failed to fetch PO Token for {client} client: {e}')
            return

        pot = pot_response.get('po_token')
        if not pot:
            self.report_warning(f'Invalid GetPOT Response: Missing po_token. {pot_response}')
            return

        return pot
