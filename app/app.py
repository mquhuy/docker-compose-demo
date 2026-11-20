"""App nho dem luot ghe: chi dung thu vien chuan cua Python, noi Redis qua socket."""
import os
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
LOI_CHAO = "Xin chào từ Docker Compose"


def redis_incr(key: str) -> int:
    """Gui lenh INCR toi Redis, tra ve so moi."""
    lenh = f"*2\r\n$4\r\nINCR\r\n${len(key)}\r\n{key}\r\n".encode()
    with socket.create_connection((REDIS_HOST, REDIS_PORT), timeout=2) as s:
        s.sendall(lenh)
        tra_loi = s.recv(64).decode()
    if not tra_loi.startswith(":"):
        raise RuntimeError(tra_loi.strip())
    return int(tra_loi[1:].strip())


class XuLy(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            return self.tra_ve(200, "text/plain", "ok")
        if self.path not in ("/", "/text"):  # vd. /favicon.ico: khong dem
            return self.tra_ve(404, "text/plain", "không có")
        try:
            so = redis_incr("hits")
        except OSError as loi:
            thong_bao = f"Không kết nối được Redis ở {REDIS_HOST}:{REDIS_PORT} ({loi.strerror or loi})"
            print(f"LOI: {thong_bao}", flush=True)
            return self.tra_ve(500, "text/plain", thong_bao)
        print(f"{self.command} {self.path} -> lượt {so}", flush=True)
        if self.path == "/text":
            return self.tra_ve(200, "text/plain", f"{LOI_CHAO} | Lượt truy cập thứ {so}")
        trang = (
            "<!doctype html><meta charset='utf-8'><title>Demo Compose</title>"
            "<body style='font-family:sans-serif;background:#fafaf7;color:#1f2328;"
            "display:grid;place-items:center;height:100vh;margin:0;text-align:center'>"
            f"<div><h1 style='font-size:64px;margin:0 0 24px'>{LOI_CHAO}</h1>"
            f"<p style='font-size:44px;margin:0'>Bạn là lượt truy cập thứ <b id='dem'>{so}</b></p>"
            f"<p style='font-size:24px;color:#57606a'>container: {socket.gethostname()}</p></div>"
        )
        return self.tra_ve(200, "text/html", trang)

    def tra_ve(self, ma, kieu, noi_dung):
        du_lieu = (noi_dung + ("\n" if kieu == "text/plain" else "")).encode()
        self.send_response(ma)
        self.send_header("Content-Type", f"{kieu}; charset=utf-8")
        self.send_header("Content-Length", str(len(du_lieu)))
        self.end_headers()
        self.wfile.write(du_lieu)

    def log_message(self, *args):  # tat log mac dinh, chi in dong cua minh
        pass


if __name__ == "__main__":
    print(f"App chạy ở cổng 8000, Redis: {REDIS_HOST}:{REDIS_PORT}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8000), XuLy).serve_forever()
