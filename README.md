# PhotoPrism 2 Immich
Simple collection of tools and scripts to ease the process of migrating from 
[Photoprism](https://github.com/photoprism/photoprism) to [Immich](https://github.com/immich-app/immich).

## Mirroring Existing Albums
`mirror_albums.py` is a script that mirrors the existing albums from Photoprism to Immich.

If albums are already present in Immich, but don't contain the same photo membership, the script will update the album 
to match the Photoprism album.

### Usage
#### Install Requirements
```bash
pip install -r requirements.txt
```

#### Environment variable options
Required:
- `PHOTOPRISM_API_URL`
- `PHOTOPRISM_API_USER`
- `PHOTOPRISM_API_KEY`
- `IMMICH_API_URL`
- `IMMICH_API_KEY`

Optional: 
- `SOURCE_ALBUM_PATTERN` 

#### Run the script
```bash
./mirror_albums.py
```
