#!/usr/bin/env python3
import os

import urllib3

from photoprism.photo import Photo
from photoprism.session import Session


class PhotoPrismApi:

    def __init__(self):
        self.photoprism_pw = os.getenv("PHOTOPRISM_API_KEY")
        self.photoprism_user = os.getenv("PHOTOPRISM_API_USER")
        self.photoprism_url = os.getenv("PHOTOPRISM_API_URL")
        if any([not self.photoprism_pw, not self.photoprism_user, not self.photoprism_url]):
            raise Exception("PHOTOPRISM_API_KEY, PHOTOPRISM_API_USER, and PHOTOPRISM_API_URL must be set in the "
                            "environment")

        self.pp_session = Session(
            self.photoprism_user,
            self.photoprism_pw,
            self.photoprism_url,
            use_https=True
        )
        self.pp_session.create()
        self.photo = Photo(self.pp_session)

    def search(self, query: str, count: int = 100, offset: int = 0, order: str = "newest"):
        return self.photo.search(query, count, offset, order)

    def get_album_list(self) -> list[dict]:
        return [album for album in self.photo.list_albums() if album["Type"] == "album"]

    def get_albums_matching_pattern(self, pattern: str) -> list[dict]:
        if not pattern:
            return self.get_album_list()
        return [
            category_album for category_album in self.get_album_list() if category_album["Title"].startswith(pattern)
        ]

    def get_album_photo_list(self, album_uid: str) -> list[dict]:
        return self.photo.get_photos_in_album(album_uid)
