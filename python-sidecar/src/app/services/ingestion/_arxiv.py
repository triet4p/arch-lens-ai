import os
import re
import httpx
import xml.etree.ElementTree as ET
from datetime import datetime
from src.app.core.constants import ARXIV_API_URL, ARXIV_XML_NAMESPACE
from src.app.core.logger import get_logger
from src.app.core.state import ArxivAPIState
from src.app.models.artifact import ArtifactType
from src.app.dto.internal import IngestedArtifact

_logger = get_logger("[Ingestion - ArXiv]")

class ArxivIngestor:
    def __init__(self, state: ArxivAPIState):
        self.state = state

    def _extract_id(self, url_or_id: str) -> str:
        """Trích xuất ArXiv ID từ URL hoặc chuỗi nhập vào"""
        pattern = r"(\d{4}\.\d{4,5}(?:v\d+)?)"
        match = re.search(pattern, url_or_id)
        return match.group(1) if match else url_or_id

    async def fetch_metadata(self, paper_id: str) -> IngestedArtifact:
        """Gọi API ArXiv để lấy metadata thô"""
        clean_id = self._extract_id(paper_id)
        params = {"id_list": clean_id}
        
        # Đảm bảo rate limit như legacy
        await self.state.wait_for_arxiv()
        
        async with httpx.AsyncClient(headers={"User-Agent": self.state.user_agent}) as client:
            resp = await client.get(ARXIV_API_URL, params=params)
            resp.raise_for_status()
            
            return self._parse_xml(resp.content, clean_id)

    def _parse_xml(self, xml_content: bytes, paper_id: str) -> IngestedArtifact:
        """Logic parse XML Atom feed từ legacy"""
        root = ET.fromstring(xml_content)
        entry = root.find('atom:entry', ARXIV_XML_NAMESPACE)
        
        if entry is None:
            raise ValueError(f"No paper found with ID: {paper_id}")

        title = entry.find('atom:title', ARXIV_XML_NAMESPACE).text.replace('\n', ' ').strip()
        summary = entry.find('atom:summary', ARXIV_XML_NAMESPACE).text.replace('\n', ' ').strip()
        authors = [a.find('atom:name', ARXIV_XML_NAMESPACE).text for a in entry.findall('atom:author', ARXIV_XML_NAMESPACE)]
        
        pdf_link = ""
        for link in entry.findall('atom:link', ARXIV_XML_NAMESPACE):
            if link.attrib.get('title') == 'pdf':
                pdf_link = link.attrib.get('href')
        
        if not pdf_link:
            pdf_link = f"https://arxiv.org/pdf/{paper_id}.pdf"

        return IngestedArtifact(
            type=ArtifactType.PAPER,
            source_url=pdf_link,
            raw_metadata={
                "paper_id": paper_id,
                "title": title,
                "authors": authors,
                "abstract": summary,
                "published": entry.find('atom:published', ARXIV_XML_NAMESPACE).text
            }
        )

    async def download_pdf(self, url: str, storage_dir: str, artifact_id: str) -> str:
        """Tải PDF về thư mục của Workspace"""
        os.makedirs(storage_dir, exist_ok=True)
        # Tạo tên file an toàn
        safe_name = re.sub(r'[^\w\-_\.]', '_', artifact_id)
        file_path = os.path.join(storage_dir, f"{safe_name}.pdf")

        _logger.info(f"⬇️ Downloading PDF: {url}")
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                with open(file_path, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)
        
        return file_path