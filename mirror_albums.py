import os

from immich.client import ImmichApi
from photoprism.client import PhotoPrismApi


def get_photoprism_album_structure(photoprism_client: PhotoPrismApi, album_name_pattern: str) -> dict:
    matching_albums = photoprism_client.get_albums_matching_pattern(album_name_pattern)
    return {
        album['Title']: photoprism_client.get_album_photo_list(album['UID']) for album in matching_albums
    }


if __name__ == "__main__":
    # Initialize api clients
    photoprism = PhotoPrismApi()
    immich = ImmichApi()

    # Get existing Photoprism album structure
    album_pattern = os.getenv("SOURCE_ALBUM_PATTERN", None)
    if album_pattern:
        print(f"Getting Photoprism albums that match the following pattern to mirror to Immich: {album_pattern}")
    else:
        print("Getting all Photoprism albums to mirror to Immich")

    photoprism_album_structure = get_photoprism_album_structure(photoprism, album_pattern)
    print(f"Found {len(photoprism_album_structure)} albums in Photoprism:"
          f" [{', '.join(photoprism_album_structure.keys())}]")

    # Get existing albums from Immich
    immich_albums = immich.get_albums()

    # For album in PhotoPrism, attempt to mirror those albums in Immich
    for album_name, photo_list in photoprism_album_structure.items():
        print(f"Processing album {album_name}")
        # If the album doesn't exist in Immich yet, create it
        try:
            existing_immich_album = next((album for album in immich_albums if album['albumName'] == album_name), None)
        except StopIteration:
            existing_immich_album = None

        if not existing_immich_album:
            print(f"Creating album {album_name} in Immich")
            immich_album_id = immich.create_album(album_name)['id']
        else:
            immich_album_id = existing_immich_album['id']
            print(f"Album {album_name} already exists in Immich")

        # Get all details of the immich album
        immich_album = immich.get_album_details(immich_album_id)
        immich_photo_list = [os.path.splitext(photo['originalFileName'])[0].replace(".MP", "") for photo in immich_album['assets']]

        # Get a list of photos that are not already in the album
        photos_to_add = [photo for photo in photo_list if photo not in immich_photo_list]
        print(f"Source album has {len(photo_list)} photos, Immich album has {len(immich_photo_list)} photos, "
              f"photos to add: {len(photos_to_add)}")

        if not photos_to_add:
            print(f"Immich album already has all photos from Photoprism source, nothing to add!")
            continue

        # For each photo, attempt to find it via Immich API
        immich_photo_ids_to_add = []
        for photo in photos_to_add:
            immich_photo = immich.find_photo_by_name(photo)

            if immich_photo:
                immich_photo_ids_to_add.append(immich_photo['id'])

        if not immich_photo_ids_to_add:
            print(f"Could not find any photos from Photoprism in Immich, skipping album {album_name}")
            continue

        # Add the found photos to the album
        immich.add_photos_to_album(immich_album_id, immich_photo_ids_to_add)
        print(f"Added {len(immich_photo_ids_to_add)} photos to album {album_name}")
