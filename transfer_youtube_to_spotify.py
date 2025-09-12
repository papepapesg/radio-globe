"""Transfer liked tracks from YouTube Music to a Spotify playlist.

This script uses `ytmusicapi` to fetch the authenticated user's liked songs
from YouTube Music and `spotipy` to create/fill a playlist on Spotify with
matching tracks. Authentication credentials for both services are expected to
be provided via environment variables or local auth files.

Usage:
    python transfer_youtube_to_spotify.py --playlist "My YT Likes" --headers headers_auth.json

Required environment variables for Spotify authentication:
    - SPOTIFY_CLIENT_ID
    - SPOTIFY_CLIENT_SECRET
    - SPOTIFY_REDIRECT_URI

The YouTube Music authentication headers file can be generated with
`ytmusicapi.setup_oauth()` and is referenced via the --headers argument.

Note: This script performs best-effort matching of songs between platforms and
only adds tracks found on Spotify.
"""

from __future__ import annotations

import argparse
from typing import List

try:
    from ytmusicapi import YTMusic
except ImportError as e:  # pragma: no cover - dependency missing at runtime
    YTMusic = None  # type: ignore

try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
except ImportError as e:  # pragma: no cover - dependency missing at runtime
    spotipy = None  # type: ignore
    SpotifyOAuth = None  # type: ignore


def create_or_get_playlist(sp: "spotipy.Spotify", user_id: str, playlist_name: str) -> str:
    """Return the Spotify playlist ID, creating the playlist if necessary."""
    playlists = sp.current_user_playlists()
    for playlist in playlists.get("items", []):
        if playlist.get("name") == playlist_name:
            return playlist.get("id")
    created = sp.user_playlist_create(user_id, playlist_name, public=False)
    return created["id"]


def transfer_yt_likes_to_spotify(playlist_name: str, headers_path: str) -> List[str]:
    """Transfer liked tracks from YouTube Music to Spotify.

    Args:
        playlist_name: Name of the Spotify playlist to create or update.
        headers_path: Path to the YouTube Music headers auth JSON file.

    Returns:
        A list of Spotify track IDs that were added to the playlist.
    """
    if YTMusic is None or spotipy is None or SpotifyOAuth is None:
        raise RuntimeError("Required libraries not installed. Ensure ytmusicapi and spotipy are installed.")

    ytm = YTMusic(headers_path)
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="playlist-modify-private playlist-modify-public"))
    user_id = sp.current_user()["id"]
    playlist_id = create_or_get_playlist(sp, user_id, playlist_name)

    liked = ytm.get_liked_songs(limit=500)
    track_ids: List[str] = []

    for track in liked.get("tracks", []):
        artists = track.get("artists", [])
        artist_name = artists[0]["name"] if artists else ""
        title = track.get("title", "")
        query = f"{artist_name} {title}".strip()
        if not query:
            continue
        results = sp.search(query, type="track", limit=1)
        items = results.get("tracks", {}).get("items", [])
        if items:
            track_ids.append(items[0]["id"])

    # Add tracks in batches of 100 to comply with Spotify's API limits
    for i in range(0, len(track_ids), 100):
        sp.playlist_add_items(playlist_id, track_ids[i : i + 100])

    return track_ids


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playlist", default="YouTube Liked", help="Spotify playlist name")
    parser.add_argument(
        "--headers",
        default="headers_auth.json",
        help="Path to YouTube Music authentication headers JSON",
    )
    args = parser.parse_args()
    added = transfer_yt_likes_to_spotify(args.playlist, args.headers)
    print(f"Added {len(added)} tracks to Spotify playlist '{args.playlist}'.")


if __name__ == "__main__":  # pragma: no cover - manual execution entry point
    main()
