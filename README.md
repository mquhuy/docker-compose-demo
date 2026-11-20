# Docker Compose demo — Anh I Tờ

Code đi kèm video **"Docker Compose là gì?"** trên kênh YouTube Anh I Tờ.

Một app nhỏ gồm 3 khối:

```
trình duyệt → web (Nginx, cổng 8080) → app (Python, cổng 8000) → redis (đếm lượt truy cập)
```

## Chạy thử

Cần Docker có sẵn lệnh `docker compose` (Compose v2).

```bash
docker compose up -d --build   # dựng image app và bật cả 3 container
# mở http://localhost:8080 rồi F5 vài lần: số lượt tăng dần
docker compose ps              # chỉ web mở cổng 8080 ra máy ngoài
docker compose logs app        # xem log của service app
docker compose exec redis redis-cli get hits
docker compose down            # tắt và xoá container + mạng, GIỮ volume (số đếm còn)
docker compose down -v         # xoá luôn volume redis-data (số đếm về 1)
```

## Các file

| File | Vai trò |
|---|---|
| `compose.yaml` | Mô tả 3 service, mạng, volume và thứ tự bật (`depends_on`, `healthcheck`) |
| `app/Dockerfile` | Đóng gói app Python |
| `app/app.py` | App đếm lượt, gọi Redis bằng tên service `redis` (biến `REDIS_HOST`) |
| `nginx/default.conf` | Nginx đứng trước, chuyển yêu cầu sang `app:8000` |

Tên file khuyên dùng hiện nay là `compose.yaml`; tên cũ `docker-compose.yaml` vẫn chạy.

Cẩn thận với `docker compose down -v` trên máy thật: lệnh này xoá dữ liệu trong volume.
