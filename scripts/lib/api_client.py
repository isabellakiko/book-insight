"""
API 客户端封装

提供 HTTP 和 SSE 调用后端 API 的统一接口
"""

import json
import urllib.request
import urllib.error
import urllib.parse
from typing import Generator, Optional
from dataclasses import dataclass


@dataclass
class SSEEvent:
    """SSE 事件"""
    event: str
    data: dict


class APIClient:
    """Book Insight API 客户端"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")

    # ===== 书籍 API =====

    def list_books(self) -> list[dict]:
        """获取所有书籍列表"""
        return self._get("/api/books")

    def get_book(self, book_id: str) -> Optional[dict]:
        """获取书籍详情"""
        try:
            return self._get(f"/api/books/{book_id}")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise

    # ===== 人物分析 API =====

    def search_character(self, book_id: str, name: str) -> dict:
        """搜索人物出现章节"""
        return self._post(f"/api/analysis/{book_id}/characters/search", {"name": name})

    def get_detailed_character(self, book_id: str, name: str) -> Optional[dict]:
        """获取详细人物分析"""
        try:
            encoded_name = urllib.parse.quote(name)
            return self._get(f"/api/analysis/{book_id}/characters/detailed/{encoded_name}")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise

    def get_detailed_characters(self, book_id: str) -> list[dict]:
        """获取所有详细人物分析"""
        return self._get(f"/api/analysis/{book_id}/characters/detailed")

    def stream_analyze_character(
        self,
        book_id: str,
        name: str,
        timeout: int = 600
    ) -> Generator[SSEEvent, None, None]:
        """流式分析人物（SSE）"""
        encoded_name = urllib.parse.quote(name)
        url = f"{self.base_url}/api/analysis/{book_id}/characters/stream?name={encoded_name}"
        yield from self._sse_request(url, timeout)

    def stream_continue_analysis(
        self,
        book_id: str,
        name: str,
        additional_chapters: int = 100,
        timeout: int = 600
    ) -> Generator[SSEEvent, None, None]:
        """继续分析更多章节（SSE）"""
        encoded_name = urllib.parse.quote(name)
        url = f"{self.base_url}/api/analysis/{book_id}/characters/continue"
        url += f"?name={encoded_name}&additional_chapters={additional_chapters}"
        yield from self._sse_request(url, timeout)

    # ===== 内部方法 =====

    def _get(self, path: str) -> dict:
        """GET 请求"""
        url = f"{self.base_url}{path}"
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/json")

        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _post(self, path: str, data: dict) -> dict:
        """POST 请求"""
        url = f"{self.base_url}{path}"
        body = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")

        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _sse_request(self, url: str, timeout: int) -> Generator[SSEEvent, None, None]:
        """SSE 流式请求"""
        req = urllib.request.Request(url)
        req.add_header("Accept", "text/event-stream")

        with urllib.request.urlopen(req, timeout=timeout) as resp:
            buffer = ""
            event_type = "message"

            for line in resp:
                line = line.decode("utf-8")
                buffer += line

                if line == "\n":
                    # 解析事件
                    if buffer.strip():
                        for buf_line in buffer.split("\n"):
                            if buf_line.startswith("event:"):
                                event_type = buf_line[6:].strip()
                            elif buf_line.startswith("data:"):
                                data_str = buf_line[5:].strip()
                                if data_str:
                                    try:
                                        data = json.loads(data_str)
                                        yield SSEEvent(event=event_type, data=data)
                                    except json.JSONDecodeError:
                                        pass
                    buffer = ""
                    event_type = "message"

    def check_health(self) -> bool:
        """检查 API 健康状态"""
        try:
            self._get("/api/health")
            return True
        except Exception:
            return False
