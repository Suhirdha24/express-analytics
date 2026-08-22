import re
import requests
from pathlib import Path
from typing import Dict, Any
from bs4 import BeautifulSoup
from app.core.logging import logger


class DocumentLoader:
    """Loads text, markdown, HTML files or web content from URLs."""

    @staticmethod
    def load_from_file(file_path: Path) -> Dict[str, Any]:
        """Reads file content from local disk and extracts metadata."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = file_path.suffix.lower()
        content = file_path.read_text(encoding="utf-8")

        title = file_path.stem.replace("_", " ").replace("-", " ").title()
        
        # Try extracting title from markdown top header
        if ext == ".md":
            header_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if header_match:
                title = header_match.group(1).strip()
        elif ext in [".html", ".htm"]:
            soup = BeautifulSoup(content, "html.parser")
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            # Extract plain text from body
            content = soup.get_text(separator="\n")

        cleaned_content = DocumentLoader._clean_text(content)
        return {
            "title": title,
            "content": cleaned_content,
            "source": file_path.name,
            "file_type": ext[1:] if ext.startswith(".") else ext,
        }

    @staticmethod
    def load_from_url(url: str, title_override: str = None) -> Dict[str, Any]:
        """Fetches web page content over HTTP and converts to cleaned text."""
        logger.info(f"Fetching URL: {url}")
        headers = {"User-Agent": "DocuMind-Bot/1.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()

        title = title_override
        if not title:
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
            else:
                title = url.split("/")[-1] or url

        text = soup.get_text(separator="\n")
        cleaned_content = DocumentLoader._clean_text(text)

        return {
            "title": title,
            "content": cleaned_content,
            "source": url,
            "file_type": "url",
        }

    @staticmethod
    def _clean_text(text: str) -> str:
        """Normalizes irregular whitespace while keeping paragraph breaks."""
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
