import httpx

from src.core.config import get_settings


class GitHubService:
    def __init__(self):
        self.settings = get_settings()
        self.base_url = "https://api.github.com"

    def _headers(self):
        headers = {"Accept": "application/vnd.github+json"}
        if self.settings.GITHUB_TOKEN:
            headers["Authorization"] = f"Bearer {self.settings.GITHUB_TOKEN}"
        return headers

    def _get(self, path: str, params: dict | None = None):
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=30) as client:
            response = client.get(url, headers=self._headers(), params=params)
            if response.status_code == 202:
                return []
            response.raise_for_status()
            return response.json()

    def fetch_commits(self, owner: str, repo: str):
        return self._get(f"/repos/{owner}/{repo}/commits", params={"per_page": 100})

    def fetch_pull_requests(self, owner: str, repo: str):
        return self._get(
            f"/repos/{owner}/{repo}/pulls", params={"state": "all", "per_page": 100}
        )

    def fetch_contributors(self, owner: str, repo: str):
        return self._get(f"/repos/{owner}/{repo}/contributors", params={"per_page": 100})

    def fetch_code_frequency(self, owner: str, repo: str):
        return self._get(f"/repos/{owner}/{repo}/stats/code_frequency")
