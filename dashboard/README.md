# NFC card game dashboard

This is a live dashboard for the NFC card game. It is built using [Godot](https://godotengine.org/).

Godot can be obtained from:
- <https://godotengine.org/download/>
- <https://store.steampowered.com/app/404790/Godot_Engine>
- <https://github.com/godotengine/godot>

## Usage

Simply start the application using the Godot editor or export it to a platform of your choice.

Keys:
- `M` - Cycle through mines
- `R` - Reconnect and resynchronize
- `F` - Toggle fullscreen
- `Q` - Quit

## Configuration

The dashboard can optionally be configured through some environment variables:

- `NFC_MINE_ID`: ID of the default mine to open, such as `1`
- `NFC_API_URL`: HTTP API URL to connect to, such as `http://localhost:8000/api`
- `NFC_WEBSOCKET_API_URL`: HTTP websocket API URL to connect to, such as `ws://localhost:8000/api/ws`
- `NFC_FULLSCREEN`: whether to start in fullscreen mode, `1` or `0`
- `NFC_DEBUG`: whether to show the debug panel, `1` or `0`

Some additional parameters may need to be configured in [`./Settings.gd`](./Settings.gd).
