import json
import pytest
from yt_dlp.networking import Request
from yt_dlp.networking.exceptions import UnsupportedRequest, RequestError, NoSupportingHandlers
from yt_dlp_plugins.extractor.getpot import GetPOTProvider, register_provider, register_preference, __version__
from yt_dlp import YoutubeDL


class FakeLogger:
    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass

    def to_stdout(self, *args, **kwargs):
        pass


@register_provider
class ExampleProviderRH(GetPOTProvider):
    _PROVIDER_NAME = 'test'
    _SUPPORTED_CLIENTS = ('web',)

    def _get_pot(self, client: str, ydl: YoutubeDL, visitor_data=None, data_sync_id=None, player_url=None, **kwargs):
        if kwargs.get('error_scenario') == 'network':
            raise RequestError('Network Error')
        elif kwargs.get('error_scenario') == 'no_supported_handlers':
            ydl.urlopen(Request('invalid://example.com/get_pot'))

        return json.dumps({
            'client': client,
            'visitor_data': visitor_data,
            'data_sync_id': data_sync_id,
            'player_url': player_url,
            **kwargs
        })

    def _validate_get_pot(self, client, ydl, error_scenario=None, **kwargs):
        if error_scenario == 'custom_validation':
            raise UnsupportedRequest('Custom Validation Failed')


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


def test_imports():
    assert isinstance(__version__, str)
    assert GetPOTProvider
    assert register_provider
    assert register_preference


class TestClient:
    def test_get_pot(self):
        with YoutubeDL() as ydl:
            ie = ydl.get_info_extractor('Youtube')
            pot = json.loads(ie.fetch_po_token('web', visitor_data='visitor', data_sync_id='sync', extra_params='extra'))
            assert pot['client'] == 'web'
            assert pot['visitor_data'] == 'visitor'
            assert pot['data_sync_id'] == 'sync'
            assert pot['extra_params'] == 'extra'
            assert pot['player_url'] is None

    def test_get_pot_unsupported_client(self):
        with YoutubeDL() as ydl:
            ie = ydl.get_info_extractor('Youtube')
            pot = ie.fetch_po_token('android')
            assert pot is None

    def test_get_pot_request_error(self):
        with YoutubeDL() as ydl:
            ie = ydl.get_info_extractor('Youtube')
            pot = ie.fetch_po_token('web', error_scenario='network')
            assert pot is None


class TestProviderValidation:
    def test_validate_supported_clients(self):
        with YoutubeDL() as ydl, ExampleProviderRH(logger=FakeLogger()) as provider:
            provider.validate(Request('get-pot:', extensions={'getpot': {'client': 'web'}, 'ydl': ydl}))

            with pytest.raises(UnsupportedRequest, match=r'^Client android is not supported$'):
                provider.validate(Request('get-pot:', extensions={'getpot': {'client': 'android'}, 'ydl': ydl}))

    @pytest.mark.parametrize('extensions', [
        {'getpot': 'invalid'},
        {'getpot': {'visitor_data': 'xyz'}},
        {}
    ])
    def test_validate_malformed_request(self, extensions):
        with YoutubeDL() as ydl, ExampleProviderRH(logger=FakeLogger()) as provider:
            with pytest.raises(UnsupportedRequest, match=r'^Malformed GetPOT Request$'):
                provider.validate(Request('get-pot:', extensions={'ydl': ydl, **extensions}))

    def test_custom_validation_interface(self):
        with YoutubeDL() as ydl, ExampleProviderRH(logger=FakeLogger()) as provider:
            with pytest.raises(UnsupportedRequest, match=r'^Custom Validation Failed$'):
                provider.validate(Request(
                    'get-pot:', extensions={'ydl': ydl, 'getpot': {'client': 'web', 'error_scenario': 'custom_validation'}}))

    def test_missing_ydl(self):
        with ExampleProviderRH(logger=FakeLogger()) as provider:
            with pytest.raises(UnsupportedRequest, match=r'^YoutubeDL instance not provided$'):
                provider.validate(Request('get-pot:', extensions={'getpot': {'client': 'web'}}))

    def test_params_copy(self):
        with YoutubeDL() as ydl, ExampleProviderRH(logger=FakeLogger()) as provider:
            params = {'client': 'web'}
            provider.validate(Request('get-pot:', extensions={'getpot': params, 'ydl': ydl}))
            assert params.get('client') == 'web'


class TestProvider:
    def test_no_supporting_handlers_wrap(self):
        # If calling ydl.urlopen in a provider plugin and no handlers support the request, NoSupportingHandlers is
        # raised. We should catch this exception and turn it into a plain RequestError

        with YoutubeDL() as ydl, ExampleProviderRH(logger=FakeLogger()) as provider:
            with pytest.raises(RequestError) as exc_info:
                provider.send(Request('get-pot:', extensions={
                    'getpot': {'client': 'web', 'error_scenario': 'no_supported_handlers'}, 'ydl': ydl}))

            assert type(exc_info.value) is not NoSupportingHandlers
