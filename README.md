# PO Token Plugin Framework for yt-dlp

_[What is a PO Token?](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#po-token-guide)_

A plugin framework for yt-dlp that allows the YouTube extractor to request Proof of Origin (PO) Tokens from an external source when needed. 
It allows for multiple providers to co-exist and provide PO Tokens for different scenarios.

> For example, one plugin could support fetching PO Tokens for logged-out users, while another supports fetching PO Tokens for logged-in users.

To use, a user will need both the client plugin (this plugin) and one or more provider plugins installed.

* [Installing](#installing)
  * [pip/pipx](#pippipx)
  * [Manual install](#manual-install)
* [Developing a Provider plugin](#developing-a-provider-plugin)
  * [Debugging](#debugging)
  * [Tips](#tips)

## Installing

> [!IMPORTANT]
> This repository only contains the **client-side plugin** for yt-dlp!
> It does not contain an implementation to retrieve PO tokens. **You will need to install a provider plugin in addition to this plugin.**
> 
> You may be able to find provider plugins in the [yt-dlp-plugins-get-pot](https://github.com/topics/yt-dlp-plugins-get-pot) topic.

**Requires yt-dlp `NIGHTLY 2024.09.13.232912` or above.**

If yt-dlp is installed through `pip` or `pipx`, you can install the plugin with the following:

### pip/pipx

```
pipx inject yt-dlp yt-dlp-get-pot
```
or

```
python3 -m pip install -U yt-dlp-get-pot
```


### Manual install

1. Download the latest release zip from [releases](https://github.com/coletdjnz/yt-dlp-get-pot/releases) 

2. Add the zip to one of the [yt-dlp plugin locations](https://github.com/yt-dlp/yt-dlp#installing-plugins)

    - User Plugins
        - `${XDG_CONFIG_HOME}/yt-dlp/plugins` (recommended on Linux/macOS)
        - `~/.yt-dlp/plugins/`
        - `${APPDATA}/yt-dlp/plugins/` (recommended on Windows)
    
    - System Plugins
       -  `/etc/yt-dlp/plugins/`
       -  `/etc/yt-dlp-plugins/`
    
    - Executable location
        - Binary: where `<root-dir>/yt-dlp.exe`, `<root-dir>/yt-dlp-plugins/`

For more locations and methods, see [installing yt-dlp plugins](https://github.com/yt-dlp/yt-dlp#installing-plugins) 

If installed correctly, you should see the GetPOT YouTubeIE plugin override in `yt-dlp -v` output:

    [debug] Extractor Plugins: GetPOT (YoutubeIE)

## Developing a Provider plugin

The provider plugin assumes this plugin is installed. You can define it as a Python dependency in your plugin package, or users can install it manually.

1. Create a new plugin (you can use the [yt-dlp sample plugins template](https://github.com/yt-dlp/yt-dlp-sample-plugins)).
2. Create a new python file under `yt_dlp_plugins.extractor` (recommend naming it `getpot_<name>.py`).
3. In the plugin file, define a Provider that extends `yt_dlp_plugins.extractor.getpot.GetPOTProvider`.
4. Implement `_get_pot` method to retrieve the PO Token from your source.

It should look something like:

```python
from yt_dlp_plugins.extractor.getpot import GetPOTProvider, register_provider

@register_provider
class MyProviderRH(GetPOTProvider):
   _PROVIDER_NAME = 'myprovider'
   _SUPPORTED_CLIENTS = ('web', )
   
   def _get_pot(self, client, ydl, visitor_data=None, data_sync_id=None, **kwargs):
        # Implement your PO Token retrieval here
        return 'PO_TOKEN'
```

See [getpot_example.py](examples/getpot_example.py) for a more in-depth example.

When yt-dlp attempts to get a PO Token, it will call out to available providers. This is the `Fetching PO Token for <client> client` line you see in the verbose log.

### Debugging

To check that your provider is being loaded, run yt-dlp with the `-v` flag and a YouTube video, and look for the `PO Token Providers` line in the output.
 You should see your provider listed:
 
    [debug] [GetPOT] PO Token Providers: <PROVIDER_NAME>

You can use `--print-traffic` to see if your provider is being called.

For general plugin debugging tips, consult the [yt-dlp plugin development wiki](https://github.com/yt-dlp/yt-dlp/wiki/Plugin-Development).

### Tips

- Your implementation should consider caching the PO Token for the given parameters to avoid unnecessary requests.
- If publishing to GitHub, add the [yt-dlp-plugins-get-pot](https://github.com/topics/yt-dlp-plugins-get-pot) topic to your repository to help users find your provider plugin.
- If publishing to PyPI, add the `yt-dlp-plugins-get-pot` keyword to your package to help users find your provider plugin.
- The [PO Token Guide](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#po-token-guide) has more information on PO Tokens.
- Advanced: A `Provider` is a customized yt-dlp HTTP Request Handler, so any parameters and functions that are available to the `RequestHandler` are also available to a `Provider`. Check out `yt_dlp.networking.common.RequestHandler` to see more.
