from yt_dlp_plugins.extractor.getpot import GetPOTProvider, register_provider, register_preference
from yt_dlp import YoutubeDL


@register_provider
class ExampleProviderRH(GetPOTProvider):
    _PROVIDER_NAME = 'test'
    _SUPPORTED_CLIENTS = ('web',)

    def _get_pot(self, client: str, ydl: YoutubeDL, visitor_data=None, data_sync_id=None, player_url=None, **kwargs) -> str:
        assert isinstance(ydl, YoutubeDL)
        return 'test' + client + (visitor_data or 'none') + (data_sync_id or 'none' )+ (player_url or 'none')


@register_preference(ExampleProviderRH)
def a_test_preference(_, __):
    return 150


def test_provider_registration():
    with YoutubeDL() as ydl:
        ie = ydl.get_info_extractor('Youtube')
        assert ExampleProviderRH.RH_KEY in ie._provider_rd.handlers


def test_preference_registration():
    with YoutubeDL() as ydl:
        ie = ydl.get_info_extractor('Youtube')
        assert a_test_preference in ie._provider_rd.preferences


def test_get_pot():
    with YoutubeDL() as ydl:
        ie = ydl.get_info_extractor('Youtube')
        pot = ie.fetch_po_token('web', visitor_data='visitor', data_sync_id='sync')
        assert pot == 'testwebvisitorsyncnone'


def test_get_pot_unsupported_client():
    with YoutubeDL() as ydl:
        ie = ydl.get_info_extractor('Youtube')
        pot = ie.fetch_po_token('android')
        assert pot is None
