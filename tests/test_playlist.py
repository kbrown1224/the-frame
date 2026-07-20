import logging

import pytest

from the_frame.playlist import ImageItem, Playlist, QuoteItem

_QUOTES = [
    {"text": "Hello world", "author": "Author One"},
    {"text": "Foo bar", "author": "Author Two"},
]


class TestPlaylistItems:
    def test_returns_image_item_from_dir(self, tmp_path):
        (tmp_path / "photo.jpg").touch()
        item = Playlist(image_dir=tmp_path, quotes=[]).next()
        assert isinstance(item, ImageItem)
        assert item.path.name == "photo.jpg"

    def test_returns_quote_item(self, tmp_path):
        item = Playlist(image_dir=tmp_path, quotes=[_QUOTES[0]]).next()
        assert isinstance(item, QuoteItem)
        assert item.text == "Hello world"
        assert item.author == "Author One"

    def test_deck_contains_both_images_and_quotes(self, tmp_path):
        (tmp_path / "photo.jpg").touch()
        playlist = Playlist(image_dir=tmp_path, quotes=_QUOTES)
        items = [playlist.next() for _ in range(3)]
        assert any(isinstance(i, ImageItem) for i in items)
        assert any(isinstance(i, QuoteItem) for i in items)

    def test_all_image_suffixes_accepted(self, tmp_path):
        for name in ["a.jpg", "b.jpeg", "c.png", "d.bmp"]:
            (tmp_path / name).touch()
        playlist = Playlist(image_dir=tmp_path, quotes=[])
        items = [playlist.next() for _ in range(4)]
        assert all(isinstance(i, ImageItem) for i in items)

    def test_non_image_files_excluded(self, tmp_path):
        (tmp_path / "notes.txt").touch()
        (tmp_path / "photo.jpg").touch()
        playlist = Playlist(image_dir=tmp_path, quotes=[])
        item = playlist.next()
        assert item.path.suffix == ".jpg"

    def test_subdirectories_excluded(self, tmp_path):
        # A subdir with an image-like name must not become an ImageItem
        (tmp_path / "vacation.jpg").mkdir()
        (tmp_path / "real.jpg").touch()
        playlist = Playlist(image_dir=tmp_path, quotes=[])
        item = playlist.next()
        assert item.path.name == "real.jpg"


class TestPlaylistDeck:
    def test_reshuffles_after_exhaustion(self, tmp_path):
        (tmp_path / "photo.jpg").touch()
        playlist = Playlist(image_dir=tmp_path, quotes=[_QUOTES[0]])
        # Two items per cycle; run three full cycles without raising
        for _ in range(6):
            playlist.next()

    def test_empty_playlist_raises(self, tmp_path):
        with pytest.raises(RuntimeError, match="empty"):
            Playlist(image_dir=tmp_path, quotes=[]).next()

    def test_missing_image_dir_logs_warning(self, tmp_path, caplog):
        missing = tmp_path / "nonexistent"
        playlist = Playlist(image_dir=missing, quotes=_QUOTES)
        with caplog.at_level(logging.WARNING, logger="the_frame.playlist"):
            playlist.next()
        assert caplog.records

    def test_missing_image_dir_still_yields_quotes(self, tmp_path):
        missing = tmp_path / "nonexistent"
        playlist = Playlist(image_dir=missing, quotes=_QUOTES)
        item = playlist.next()
        assert isinstance(item, QuoteItem)
