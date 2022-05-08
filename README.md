# Chrome Local Storage

[![Tests](https://github.com/lordjabez/chrome-local-storage/actions/workflows/test.yml/badge.svg)](https://github.com/lordjabez/chrome-local-storage/actions/workflows/test.yml)
[![Linter](https://github.com/lordjabez/chrome-local-storage/actions/workflows/lint.yml/badge.svg)](https://github.com/lordjabez/chrome-local-storage/actions/workflows/lint.yml)
[![Security](https://github.com/lordjabez/chrome-local-storage/actions/workflows/scan.yml/badge.svg)](https://github.com/lordjabez/chrome-local-storage/actions/workflows/scan.yml)
[![PyPI](https://github.com/lordjabez/chrome-local-storage/actions/workflows/publish.yml/badge.svg)](https://github.com/lordjabez/chrome-local-storage/actions/workflows/publish.yml)

This Python package makes it easy to interact with Google Chrome local storage,
either a locally-running browser or any remote browser that supports remote
debugging (e.g. Chrome on Android via `adb` port forwarding).


## Prerequisites

Installation is via `pip`:

```bash
pip install chrome-local-storage
```

Chrome must be running with the debugging port active for the library
to connect. There are various methods to do this, for example, on Windows:

```
chrome.exe --remote-debugging-port=9222
```

And on MacOS:

```
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

The library will also work on any mobile device that supports remote debugging on Chrome,
For example, on Android, use the [Android Debug Bridge](https://developer.android.com/studio/command-line/adb)
to set up a port forward as follows:

```bash
adb forward tcp:9222 localabstract:chrome_devtools_remote
```

In all of the above examples, the debugger will be available at `localhost:9222`
which is what the library expects by default.


## Usage

Basic usage is as follows:

```python3
import chrome_local_storage

local_storage = chrome_local_storage.ChromeLocalStorage()

local_storage.set('example.com', 'my-key', 'my-value')
value = local_storage.get('example.com', 'my-key')
print(value)
```

The first parameter in both `get` and `set` determines the page
whose local storage will be used for the operation. The page must
already be open in the browser, and it does not have to be an exact
match to the whole URL as long as it's unique across open pages.

In a more complex example, two constructors connect to two different
Chrome instances and copy Wordle statistics from one to the other
(the desire to transfer my streak from one device to another was
the original motivation for building this library).

```bash
chrome --remote-debugging-port=9222 "https://nytimes.com/games/wordle"
adb forward tcp:9223 localabstract:chrome_devtools_remote
```

```python3
import chrome_local_storage

laptop_storage = chrome_local_storage.ChromeLocalStorage(port=9222)
phone_storage = chrome_local_storage.ChromeLocalStorage(port=9223)

wordle_stats = laptop_storage.get('games/wordle', 'nyt-wordle-statistics')
phone_storage.set('games/wordle', 'nyt-wordle-statistics', wordle_stats)
```
