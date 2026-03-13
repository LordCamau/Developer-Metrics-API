from urllib.parse import urlparse


def parse_repo_url(repo_url: str) -> tuple[str, str]:
    parsed = urlparse(repo_url)
    if not parsed.netloc or not parsed.path:
        raise ValueError("Invalid repository URL")
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2:
        raise ValueError("Invalid repository URL")
    return parts[0], parts[1]
