#!/usr/bin/env python3
import os
from re import search

import urllib3
import requests


class ImmichApi:

    def __init__(self):
        self.immich_key = os.getenv("IMMICH_API_KEY")
        self.immich_url = os.getenv("IMMICH_API_URL")
        if any([not self.immich_key, not self.immich_url]):
            raise Exception("IMMICH_API_KEY and IMMICH_API_URL must be set in the "
                            "environment")

    def request(self, endpoint: str, method: str, **kwargs):
        url = f"{self.immich_url}/api{endpoint}"
        headers = {
            'Accept': 'application/json',
            'x-api-key': self.immich_key
        }
        response = requests.request(method, url, headers=headers, **kwargs)
        if response.status_code not in [200, 201]:
            raise (Exception(f"Failed to request {url}, error: {response.text}"))
        return response

    def get_albums(self):
        response = self.request("/albums", "GET")
        return response.json()

    def create_album(self, album_name: str):
        user_id = self.get_current_user()['id']
        response = self.request("/albums", "POST",
                                json={"albumName": album_name, "albumUsers": [{"userId": user_id, "role": "editor"}]})
        return response.json()

    def get_current_user(self):
        response = self.request("/users/me", "GET")
        return response.json()

    def get_album_details(self, immich_album_id: str):
        response = self.request(f"/albums/{immich_album_id}", "GET")
        return response.json()

    def find_photo_by_name(self, photo_name: str):
        response = self.request(f"/search/metadata", "POST", json={"originalFileName": photo_name})
        search_results = response.json()
        if not search_results or search_results['assets']['count'] == 0:
            print(f"Warning, no photo found for {photo_name}")
            manual_id = input("Manually input an ID or leave blank to skip: ")
            if manual_id:
                return {"id": manual_id}
            return None
        if search_results['assets']['count'] > 1:
            print(f"Warning, more than one photo found for {photo_name}:")
            # Have user select which one
            for i, photo in enumerate(search_results['assets']['items']):
                print(f"\t{i}: {photo['originalFileName']}")
            selection = input("Please select one (0): ")
            return search_results['assets']['items'][int(selection)]
        return search_results['assets']['items'][0]

    def add_photos_to_album(self, immich_album_id: str, immich_photo_ids_to_add: list[str]):
        response = self.request(f"/albums/{immich_album_id}/assets", "PUT",
                                json={"ids": immich_photo_ids_to_add})
        return response.json()
