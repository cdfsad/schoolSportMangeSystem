# 部署指南

高校体育场馆管理系统全栈部署:Django(DRF)+ Vue SPA + MySQL + Redis + Celery + nginx。

## 架构(6 服务)

```
浏览器 ──80──► nginx ──┬─ /api/, /admin/ ─► web(gunicorn, :8000)
                       ├─ /static/, /media/ ─► 本地 alias
                       └─ / (SPA) ─► Vue dist(构入 nginx 镜像)

web ─► db(MySQL 8.0)
     ─► redis(:6379) ─► celery-worker(异步任务)
                      └─► celery-beat(定时调度,如违约扫描)
```

| 服务 | 作用 | 端口 |
|---|---|---|
| `nginx` | 前端 SPA 托管 + 反代 `/api/` `/admin/` + static/media | 80 |
| `web` | Django + gunicorn(DRF API + SSR 兼容) | 8000 |
| `db` | MySQL 8.0(utf8mb4) | 3306 |
| `redis` | Celery broker + Django cache | 6379 |
| `celery-worker` | 异步执行任务(通知发送) | - |
| `celery-beat` | 定时调度(每 30 分钟扫违约 `scan_no_shows`) | - |

## 一键启动(生产/Docker)

前置:Docker + Docker Compose 已安装。

1. 配置 `.env`(参考 `.env.example`):
   ```ini
   SECRET_KEY=your-django-secret-key
   DEBUG=False
   ALLOWED_HOSTS=localhost,your-domain.com
   DATABASE_URL=mysql://root:INTJ123456@db:3306/mydb1
   DB_PASSWORD=INTJ123456
   REDIS_URL=redis://redis:6379/0   # 容器内必须用真实 redis(覆盖 locmem 兜底)
   ```

2. 构建并启动全栈:
   ```bash
   docker-compose up --build -d
   ```
   - nginx 构建时会跑 `npm run build` 生成 Vue dist(node:20 阶段)
   - web 启动时自动 `migrate` + `collectstatic`
   - 6 个服务全部就绪后,访问 http://localhost 即 Vue 首页

3. 创建管理员:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. 验证:
   - http://localhost → Vue SPA
   - http://localhost/api/v1/auth/me/ → 401(未认证,正确)
   - http://localhost/admin/ → Django admin
   - `docker-compose logs celery-worker` → 无报错
   - `docker-compose logs celery-beat` → `Scheduler: Sending due task scan-no-shows-every-30min`

## 本地开发(免 Docker)

后端(Django runserver)+ 前端(Vite dev)分开跑,Celery 用 EAGER 同步模式(免 Redis broker)。

1. **后端**:
   ```bash
   .venv\Scripts\activate
   pip install -r requirements.txt
   # .env 配 REDIS_URL=locmem://(或留空)→ CELERY_TASK_ALWAYS_EAGER=True,通知同步执行
   python manage.py migrate
   python manage.py runserver
   ```

2. **前端**(另开终端):
   ```bash
   cd frontend
   npm install --registry=https://registry.npmmirror.com
   npm run dev   # 5173,Vite 代理 /api → :8000
   ```

3. 访问 http://localhost:5173

4. **违约扫描**(dev 无 beat,手动跑;prod 由 celery-beat 自动调度):
   ```bash
   python manage.py scan_no_shows              # 默认 30 分钟宽限
   python manage.py scan_no_shows --grace 0    # 立即标记所有已过期
   ```

## Celery 任务清单(`app01/tasks.py`)

| 任务 | 触发 | 作用 |
|---|---|---|
| `send_notification` | `_notify.delay()`(预约 create/approve/reject/cancel 时) | 异步写站内通知 |
| `scan_no_shows` | celery-beat 每 30 分钟 | 已过开始时间+宽限期的已通过预约 → status=5 + 通知 |

dev(EAGER)下 `.delay()` 同步执行;prod 走 Redis broker + 独立 worker/beat。

## 常见问题

- **`ModuleNotFoundError: No module named 'memory'`**:`CELERY_RESULT_BACKEND` 不能用 `memory://`(那是 broker scheme)。用 `cache+memory://`(celery cache 后端)。本项目的 settings 已正确处理。
- **`locmem://` 不是 celery broker**:`locmem://` 是 Django cache scheme。Celery broker 用 `redis://`/`amqp://`/`memory://`。settings 用 `_redis_url.startswith('redis://')` 判断,无真实 Redis 时 EAGER 同步。
- **中文包名 + Celery CLI**:`celery -A 高校体育场馆管理系统 worker` 在 Windows Git Bash 可能因非 ASCII 参数出错。全部 celery 运行走 docker-compose(YAML 解析安全),dev 用 EAGER 免 CLI。
- **时区**:`TIME_ZONE='Asia/Shanghai'`,`CELERY_TIMEZONE=TIME_ZONE`,beat 调度按本地时区。
- **beat 调度持久化**:默认 scheduler 写 `celerybeat-schedule` 本地文件(容器内 ephemeral)。生产若需 DB 持久化 + admin 可编辑,改用 `celery -A 高校体育场馆管理系统 beat -l info -S django_celery_beat.schedulers:DatabaseScheduler`(django_celery_beat 已装)。

## CI

`.github/workflows/ci.yml`:ruff check + ruff format --check + makemigrations --check + check --deploy + pytest --cov-fail-under。推 PR 自动跑。
