"""Download the official portable Ollama release into this checkout."""
import hashlib
import json
import pathlib
import sys
import zipfile
import httpx

ROOT = pathlib.Path(__file__).resolve().parents[1]
target = ROOT / ".runtime"
target.mkdir(exist_ok=True)
with httpx.Client(follow_redirects=True, timeout=60) as client:
    release = client.get("https://api.github.com/repos/ollama/ollama/releases/tags/v0.40.16")
    release.raise_for_status()
    info = release.json()
    asset = next(x for x in info["assets"] if x["name"] == "ollama-windows-amd64.zip")
    archive = target / asset["name"]
    print(f"Downloading official Ollama {info['tag_name']} ({asset['size']/1024**2:.0f} MB)", flush=True)
    with client.stream("GET", asset["browser_download_url"]) as response:
        response.raise_for_status()
        with archive.open("wb") as stream:
            downloaded = 0
            checkpoint = 0
            digest = hashlib.sha256()
            for chunk in response.iter_bytes(1024*1024):
                stream.write(chunk)
                digest.update(chunk)
                downloaded += len(chunk)
                if downloaded - checkpoint >= 100*1024**2:
                    print(f"{downloaded/1024**2:.0f} MB downloaded", flush=True)
                    checkpoint = downloaded
    expected = asset.get("digest")
    if expected and expected != "sha256:" + digest.hexdigest():
        raise RuntimeError("Ollama archive checksum mismatch")
    with zipfile.ZipFile(archive) as z:
        for member in z.infolist():
            dest = (target / member.filename).resolve()
            if not dest.is_relative_to(target.resolve()):
                raise RuntimeError("Unsafe archive path")
        z.extractall(target)
    (target / "release.json").write_text(json.dumps({"version":info["tag_name"],"sha256":digest.hexdigest(),"source":asset["browser_download_url"]},indent=2))
    archive.unlink()
    print("Portable runtime ready.", flush=True)
