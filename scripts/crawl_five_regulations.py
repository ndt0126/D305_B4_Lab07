#!/usr/bin/env python3
"""Tải đúng 5 trang quy định công khai của *một* trường đại học.

Ví dụ (PowerShell):
    python scripts/crawl_five_regulations.py `
      "https://university.edu/regulations/tuition" `
      "https://university.edu/regulations/scholarships" `
      "https://university.edu/regulations/course-registration" `
      "https://university.edu/regulations/library" `
      "https://university.edu/regulations/dormitory" `
      --output-dir data/quy-dinh-dai-hoc

Chỉ dùng các URL công khai được robots.txt cho phép. Script không đăng nhập,
không vượt CAPTCHA và không crawl lan sang các trang khác.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")

USER_AGENT = "UniversityRegulationsLab/1.0 (educational use)"
BLOCK_TAGS = {"p", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "div", "section", "article"}
SKIP_TAGS = {"script", "style", "nav", "footer", "header", "noscript", "svg", "iframe"}


class PageText(HTMLParser):
    """Trích văn bản cơ bản từ HTML mà không cần cài thư viện ngoài."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self.in_title = False
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in SKIP_TAGS:
            self.skip_depth += 1
        if self.skip_depth:
            return
        if tag == "title":
            self.in_title = True
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
            return
        if self.skip_depth:
            return
        if tag == "title":
            self.in_title = False
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)
            if self.in_title:
                self.title_parts.append(data)

    def result(self) -> tuple[str, str]:
        title = re.sub(r"\s*Page Title\s*$", "", " ".join("".join(self.title_parts).split()))
        content = "".join(self.parts)
        content = content.replace("\r\n", "\n").replace("\r", "\n")
        content = re.sub(r"[ \t]+", " ", content)
        content = re.sub(r"\n[ \t]+", "\n", content)
        content = re.sub(r"\n{3,}", "\n\n", content).strip()
        document_start = re.search(r"(?:^|\n)Số\s*(?:/\s*ký hiệu)?\s*:", content, flags=re.IGNORECASE)
        if document_start:
            content = content[document_start.start():].lstrip()
        content = content.split("\nTừ khóa:", 1)[0].rstrip()
        return title, content


def slugify(value: str) -> str:
    """Tạo tên file ASCII, ổn định từ URL hoặc tiêu đề."""
    value = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return value.strip("-") or "quy-dinh"


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def allowed_by_robots(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        print(f"URL không hợp lệ: {url}", file=sys.stderr)
        return False
    parser = RobotFileParser(f"{parsed.scheme}://{parsed.netloc}/robots.txt")
    try:
        parser.read()
    except (HTTPError, URLError, OSError) as error:
        print(f"Không kiểm tra được robots.txt cho {url}: {error}", file=sys.stderr)
        return False
    return parser.can_fetch(USER_AGENT, url)


def fetch_page(url: str) -> tuple[str, str, str]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,text/plain;q=0.9"})
    with urlopen(request, timeout=20) as response:  # noqa: S310 - URL supplied by the user.
        content_type = response.headers.get_content_type().lower()
        if content_type not in {"text/html", "text/plain"}:
            raise ValueError(f"Không hỗ trợ nội dung {content_type}; hãy dùng trang HTML/text.")
        body = response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")
        # QNU currently labels some UTF-8 pages with a legacy charset.
        if "Ã" in body or "Ä" in body:
            try:
                body = body.encode("latin-1").decode("utf-8")
            except UnicodeError:
                pass
        if content_type == "text/plain":
            return response.geturl(), "", body.strip()
        parser = PageText()
        parser.feed(body)
        parser.close()
        title, content = parser.result()
        return response.geturl(), title, content


def write_markdown(path: Path, doc_id: str, title: str, source_url: str, university: str, content: str) -> None:
    metadata = {
        "doc_id": doc_id,
        "title": title,
        "source_url": source_url,
        "retrieved_at": date.today().isoformat(),
        "document_version": "not-stated",
        "audience": "student",
        "university": university,
        "category": "regulation",
        "language": "vi",
    }
    front_matter = "\n".join(f"{key}: {yaml_quote(value)}" for key, value in metadata.items())
    path.write_text(f"---\n{front_matter}\n---\n\n# {title}\n\n{content}\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Crawl đúng 5 trang quy định công khai của một trường.")
    parser.add_argument("urls", nargs=5, metavar="URL", help="5 URL quy định của cùng một trường")
    parser.add_argument("--output-dir", type=Path, default=Path("data/quy-dinh-dai-hoc"))
    parser.add_argument("--university", help="Tên trường; mặc định lấy từ tên miền")
    args = parser.parse_args()

    domains = {urlparse(url).netloc.lower() for url in args.urls}
    if len(domains) != 1:
        parser.error("Cả 5 URL phải thuộc cùng một tên miền trường đại học.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    university = args.university or next(iter(domains))
    manifest: list[dict[str, str]] = []
    failures = 0

    for index, url in enumerate(args.urls, start=1):
        if index > 1:
            time.sleep(1)  # Giới hạn tối thiểu 1 giây giữa các request.
        if not allowed_by_robots(url):
            print(f"Bỏ qua (robots.txt không cho phép): {url}", file=sys.stderr)
            failures += 1
            continue
        try:
            final_url, page_title, content = fetch_page(url)
            if len(content) < 80:
                raise ValueError("Nội dung quá ngắn; hãy chọn trang quy định khác.")
            doc_id = f"quy-dinh-{index:02d}-{slugify(urlparse(final_url).path.rsplit('/', 1)[-1])}"
            title = page_title or f"Quy định {index}"
            output_path = args.output_dir / f"{doc_id}.md"
            write_markdown(output_path, doc_id, title, final_url, university, content)
            manifest.append({
                "doc_id": doc_id, "file_path": str(output_path), "title": title,
                "source_url": final_url, "retrieved_at": date.today().isoformat(),
                "document_version": "not-stated", "license_or_permission": "public-page",
            })
            print(f"Đã lưu: {output_path}")
        except (HTTPError, URLError, TimeoutError, UnicodeError, ValueError, OSError) as error:
            print(f"Bỏ qua {url}: {error}", file=sys.stderr)
            failures += 1

    with (args.output_dir / "sources.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["doc_id", "file_path", "title", "source_url", "retrieved_at", "document_version", "license_or_permission"])
        writer.writeheader()
        writer.writerows(manifest)
    print(f"Hoàn tất: {len(manifest)}/5 trang đã lưu trong {args.output_dir}.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
