import base64
import json
from yt_dlp.extractor.youtube import YoutubeIE
from yt_dlp.networking import Request
from yt_dlp.networking.exceptions import NoSupportingHandlers, RequestError
from yt_dlp.utils import update_url_query, ExtractorError


class _GetPOTClient(YoutubeIE, plugin_name='GetPOT'):
    """
    Plugin to inject GetPOT request into the YouTube extractor.
    """
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

        payload = {
            'client': client,
            'visitor_data': visitor_data,
            'data_sync_id': data_sync_id,
            'player_url': player_url,
        }

        url = update_url_query('get-pot:', {
            'q': base64.urlsafe_b64encode(json.dumps(payload).encode('utf-8')).decode('utf-8'),
        })

        try:
            pot_response = self._download_json(
                Request(url, extensions={'ydl': self._downloader}),
                video_id='GetPOT', note=f'Fetching PO Token for {client} client'
            )

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
