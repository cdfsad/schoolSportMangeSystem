# 高校体育场馆管理系统

> **Django 5 + Vue 3 全栈 · 工业级开源实践** — 从一个密码明文、零测试的教学项目,改造为具备安全加固、前后端分离、异步任务调度、容器化部署的可商业化系统。

![CI](https://github.com/cdfsad/schoolSportMangeSystem/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![Django](https://img.shields.io/badge/Django-5.1-green.svg)
![Vue](https://img.shields.io/badge/Vue-3.5-brightgreen.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)
![Coverage](https://img.shields.io/badge/覆盖率-76%25-yellow.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

---

## ✨ 项目亮点

- **🔐 安全止血**:配置外置(django-environ)、密码 PBKDF2 哈希 + 渐进迁移、CSRF 修复、RBAC 权限矩阵、IDOR 越权修复、文件上传校验。
- **🧱 services 层 + 行锁**:`booking_service.create_booking` 用 `select_for_update` 防并发重复预约;ViewSet 保持薄,业务逻辑可复用、可测试。
- **🌐 DRF + JWT + Vue 3 SPA**:Session(SSR 兼容)与 JWT(SPA)共存,8 个 ViewSet + 14 个学生/管理页面。
- **⚙️ 规则引擎 + Celery 异步**:BookingRule 三级解析(场地/类型/全局);通知异步发送 + beat 每 30 分钟违约扫描。
- **🧪 64 测试 / 76% 覆盖率 + Docker 全栈一键部署**(6 服务:nginx + web + db + redis + celery-worker + celery-beat)。

---

## 📋 功能特性

### 学生 / 工作人员
- 学号登录(JWT)、场地浏览(校区过滤/搜索)、在线预约、我的预约(取消)、个人中心改密。
- **站内通知**:预约被审批/拒绝时铃铛红点提醒 + 通知列表(30s 轮询未读数)。

### 管理员(8 页管理后台)
| 页面 | 能力 |
|---|---|
| 仪表盘 | ECharts 柱状图 + 总用户/场地/待审批/今日预约统计卡 |
| 用户管理 | CRUD + Excel 批量导入学生 |
| 场地管理 | CRUD(软删除) |
| 校区管理 | CRUD |
| 时段管理 | CRUD(TimePicker) |
| 预约审批 | **通过 / 拒绝(填理由)/ 取消 / 删除** |
| 预约规则 | CRUD(提前天数 / 每日上限 / 取消时限) |
| 审计日志 | 只读,行展开看 detail JSON |

### 系统能力
- **JWT 认证**(access 2h / refresh 7d + 黑名单)、**预约规则校验**(`advance_days` / `daily_limit_per_user` / `cancel_deadline_hours`)、**AuditLog 审计**(approve/reject/cancel/create 全打点)、**Celery 异步**(通知 + 违约扫描)。

---

## 🛠 技术栈

| 层 | 选型 |
|---|---|
| **后端** | Django 5.1 · DRF 3.15 · djangorestframework-simplejwt 5.3 · django-filter · Celery 5.4 · django-celery-beat 2.7 · gunicorn 23 · Python 3.11 |
| **前端** | Vue 3.5 · Vite 5 · TypeScript 5.6 · Pinia · Vue Router · Element Plus 2.8 · vue-echarts · axios |
| **基础设施** | MySQL 8.0 · Redis 7 · nginx · Docker Compose(6 服务)· GitHub Actions CI |

---

## 🏗 架构

```
浏览器 ──:80──► nginx ──┬─ /  /assets  →  Vue SPA dist(构入 nginx 镜像)
                        ├─ /api/  /admin/  →  web(gunicorn :8000)
                        └─ /static/  /media/  →  alias(collectstatic)

web ──► MySQL(db)
     ──► redis ──► celery-worker(异步执行 send_notification)
                  └─► celery-beat(每 30 min 触发 scan_no_shows 扫违约)
```

**请求链路**:浏览器 → nginx(80)按路径分流 → SPA / `/api/` 反代 web(8000) → DRF ViewSet → services 层 → ORM → MySQL。预约状态变更时 `_notify` → `send_notification.delay()` → Redis broker → celery-worker 异步写通知。

---

## 📁 项目结构

```
高校体育场馆管理系统/
├── 高校体育场馆管理系统/        # Django 项目包
│   ├── settings.py            # 配置(environ + REST_FRAMEWORK + CELERY_*)
│   ├── celery.py              # Celery app(autodiscover)
│   └── urls.py
├── app01/                     # 业务 App
│   ├── models.py              # 8 模型(CustomUser/Place/Book/BookingRule/Notification/AuditLog…)
│   ├── api/                   # DRF:serializers/views/urls/filters/permissions(8 ViewSet)
│   ├── services/              # 业务层(booking_service/place_service/account_service)
│   │   └── booking_service.py # create_booking(select_for_update)/规则校验/审计/通知
│   ├── tasks.py               # Celery 任务(send_notification / scan_no_shows)
│   ├── management/commands/   # import_legacy_data / scan_no_shows
│   └── tests/                 # pytest(64 测试,76% 覆盖)
├── frontend/                  # Vue 3 SPA
│   ├── src/views/admin/       # 8 个管理后台页面
│   ├── src/api/               # Axios 封装 + 资源模块
│   ├── src/layouts/           # DefaultLayout / AdminLayout(铃铛+侧边栏)
│   └── Dockerfile             # 多阶段:node 构 dist → nginx 托管
├── docs/DEPLOY.md             # 深度部署指南(6 服务 / .env / 常见问题)
├── Dockerfile                 # Django + gunicorn
├── docker-compose.yml         # name: sports-venue(db/redis/web/worker/beat/nginx)
├── nginx.conf                 # SPA 路由 + /api 反代
└── requirements.txt
```

---

## 🚀 快速开始

### 方式一:本地开发(免 Docker)

> 无 Redis 时 Celery 自动 `EAGER` 同步执行,通知/违约扫描零负担。

```bash
# 后端
python -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # 填 SECRET_KEY / DATABASE_URL
python manage.py migrate
python manage.py runserver    # :8000

# 前端(另开终端)
cd frontend
npm install --registry=https://registry.npmmirror.com
npm run dev                   # :5173(/api 代理到 :8000)
```

访问 **http://localhost:5173**,登录 `2018044743125` / `Admin@12345`。

### 方式二:Docker 全栈一键

```bash
cp .env.example .env          # 至少填 SECRET_KEY、DB_PASSWORD
docker-compose up --build -d  # 构建 + 启动 6 个服务
```

访问 **http://localhost**。详细配置见 [`docs/DEPLOY.md`](docs/DEPLOY.md)。

---

## 📡 API 概览

挂载于 `/api/v1/`,JWT Bearer 认证。

| 端点 | 方法 | 说明 | 权限 |
|---|---|---|---|
| `/auth/login/` | POST | 学号 + 密码 → access/refresh | 公开 |
| `/auth/me/` | GET | 当前用户信息 | 已登录 |
| `/auth/change-password/` | POST | 改密(校验旧密码) | 已登录 |
| `/places/` | GET | 场地列表(校区过滤/搜索) | 已登录 |
| `/books/` | GET/POST | 查/建预约(规则校验 + 行锁) | 已登录 |
| `/books/{id}/approve/` | POST | 审批通过 | 管理员 |
| `/books/{id}/reject/` | POST | 审批拒绝(填理由) | 管理员 |
| `/books/{id}/cancel/` | POST | 取消(校验归属 + 时限) | 本人/管理员 |
| `/notifications/` | GET | 我的通知列表 | 已登录 |
| `/notifications/unread-count/` | GET | 未读数(铃铛轮询) | 已登录 |
| `/statistics/` | GET | 各场地预约数(ECharts) | 已登录 |
| `/audit-logs/` | GET | 审计日志(过滤/分页) | 管理员 |
| `/users/` `/campuses/` `/time-slots/` `/booking-rules/` | CRUD | 管理后台资源 | CUD 管理员 |

---

## 💎 核心设计

### services 层 + `select_for_update` 行锁
`app01/services/booking_service.py::create_booking` 在 `transaction.atomic()` 内对场地行加 `select_for_update()` 锁,并发预约同一时段时由数据库行锁保证唯一性,再叠加应用层冲突校验。ViewSet 仅做参数解析 → 调 service → 返回响应,业务可被 API 与 SSR 视图共用。

### BookingRule 三级解析
`_resolve_rule(place)` 按 **场地特定规则 > 场地类型规则 > 全局兜律** 三级回落;`create_booking` 校验 `advance_days`(不可过早)与 `daily_limit_per_user`(每日上限),`cancel_booking` 校验 `cancel_deadline_hours`(过时限不可取消)。规则由管理后台配置,种子 migration 写入默认全局规则。

### AuditLog 全链路打点
`approve` / `reject` / `cancel` / `create` 在 services 末尾统一 `_log_audit()`,记录操作人/动作/目标/IP/detail。管理后台「审计日志」页可过滤查看,行展开看 detail JSON。

### Celery EAGER 双模式
`settings.py` 用 `_redis_url.startswith('redis://')` 判断:无真实 Redis(本地/测试 `.env` 配 `locmem://` 或空)时 `CELERY_TASK_ALWAYS_EAGER=True`,`.delay()` 同步执行免 broker;生产 docker-compose 注入 `REDIS_URL=redis://redis:6379/0` → 走独立 worker/beat 容器。beat 每 30 分钟跑 `scan_no_shows`,把过期未签到的已通过预约标记为违约(`status=5`)并通知。

---

## 🧪 测试与质量

```bash
pytest                        # 64 passed,覆盖率 76%
ruff check .                  # 0 issues
python manage.py check --deploy   # 仅 HTTPS 预期 warning
```

覆盖:登录/JWT、并发预约冲突(`select_for_update`)、权限矩阵(student→403/admin→200)、IDOR、CSRF、BookingRule 三项校验、通知 producers、违约扫描、Campus/User/BookingRule CRUD。

---

## 📦 部署

生产部署(6 服务全栈、`.env` 配置、Celery worker/beat、中文包名注意事项)详见 **[`docs/DEPLOY.md`](docs/DEPLOY.md)**。

---

## 🗺 开发历程

一个从教学项目到工业级产品的完整改造链路:

| 阶段 | 内容 | 状态 |
|---|---|:---:|
| **P0** | 安全止血:配置外置 / 密码哈希 / CSRF / RBAC / IDOR / 文件校验 | ✅ |
| **P1** | 工程化:AbstractUser 重构 / 8 模型 / services 层 / pytest / Docker / CI | ✅ |
| **P2a** | DRF API:8 ViewSet + JWT + Session 共存 + 优化(N+1/404/审计) | ✅ |
| **P2b** | Vue 3 SPA 核心:登录/场地/预约/我的/个人中心 + Axios + Pinia | ✅ |
| **P2c** | 管理后台:8 页(审批 reject/校区 CRUD/审计日志/规则/统计) | ✅ |
| **P3a** | 商业化:BookingRule 接入 + 站内通知(铃铛) + nginx 生产部署 | ✅ |
| **P3b** | Celery 异步:通知 `.delay()` + 违约定时扫描 + worker/beat 容器 | ✅ |

**可选下一步**:WebSocket 实时通知(替 30s 轮询)、支付/订单、场地图文详情、README 英文版。

---

## 📸 系统截图

> 以下为建议截图位(后续补充,放到 `docs/screenshots/` 下):

| 截图 | 说明 |
|---|---|
| `![](docs/screenshots/login.png)` | 登录页 |
| `![](docs/screenshots/places.png)` | 场地列表(校区过滤 + 表格) |
| `![](docs/screenshots/admin-dashboard.png)` | 管理后台 Dashboard(ECharts 柱状图 + 统计卡) |
| `![](docs/screenshots/admin-bookings.png)` | 预约审批(拒绝填理由弹窗) |
| `![](docs/screenshots/notification-bell.png)` | 顶栏通知铃铛(未读 badge) |

---

## 📄 License

[MIT](LICENSE) · Copyright © 2026 intj
