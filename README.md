# Get PO Token Client for yt-dlp

_[what is a PO Token?](https://github.com/yt-dlp/yt-dlp/wiki#po-token-guide)_

A simple plugin and framework for yt-dlp that allows the YouTube extractor to request PO Tokens from an external source when needed. 
It makes use <sup>(abuse)</sup> of the yt-dlp HTTP Request Handler framework to allow multiple implementations to co-exist.

For example, one plugin could support fetching PO Tokens for logged-out users, while another supports fetching PO Tokens for logged-in users.

To use, a user will need both the client plugin (this plugin) and one or more provider plugins installed.

## Installing

> Note: this repository only contains the client-side plugin for yt-dlp! It does not contain an implementation to retrieve PO tokens. You will need to install a provider plugin in addition to this plugin.

Requires yt-dlp `2024.08.XX` or above.

If yt-dlp is installed through `pip` or `pipx`, you can install the plugin with the following:

**pip or pipx**

```
pipx inject yt-dlp yt-dlp-get-pot
```
or

```
python3 -m pip install -U yt-dlp-get-pot
```


Alternatively, you can install directly from the repo with `https://github.com/coletdjnz/yt-dlp-get-pot/archive/refs/heads/master.zip`

**Manual install**

1. Download the latest release zip from [releases](https://github.com/coletdjnz/yt-dlp-get-pot/releases) 

2. Add the zip to one of the [yt-dlp plugin locations](https://github.com/yt-dlp/yt-dlp#installing-plugins)

    - User Plugins
        - `${XDG_CONFIG_HOME}/yt-dlp/plugins` (recommended on Linux/MacOS)
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
3. In the plugin file, define a GetPOT Request Handler that extends `yt_dlp_plugins.extractor.getpot.GetPOTRequestHandler`.
4. Follow the example below and implement the `_get_pot` method to retrieve the PO Token from your source.

When yt-dlp attempts to get a PO Token, it will call out to the request handler. This is the `Fetching PO Token for <client> client` line you see in the log.

### Example

See [getpot_example.py](examples/getpot_example.py) for an example implementation.

### Debugging

To check that your Request Handler is being loaded, run yt-dlp with the `-v` flag and look for the `[debug] Request Handlers` section in the output.
 You should see your request handler listed with the `RH_NAME`:
 
    [debug] Request Handlers: ..., getpot-<name>

For general plugin debugging tips, consult the [yt-dlp plugin development wiki](https://github.com/yt-dlp/yt-dlp/wiki/Plugin-Development).

### Implementation Tips

- Your implementation should consider caching the PO Token for the given parameters to avoid unnecessary requests.
- See the [PO Token Guide](https://github.com/yt-dlp/yt-dlp/wiki#po-token-guide) for more information on the PO Tokens.