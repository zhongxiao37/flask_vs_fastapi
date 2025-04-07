# 构建阶段
FROM python:3.12-slim-bookworm AS builder

# 复制 uv 工具
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 设置 uv 的环境变量
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 设置工作目录
WORKDIR /app

# 首先只复制依赖相关文件
COPY uv.lock pyproject.toml /app/

# 安装依赖
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# 复制项目代码和uwsgi配置
COPY . /app

# 安装项目
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# 最终镜像
FROM python:3.12-slim-bookworm

# 从构建阶段复制整个应用（包括虚拟环境）
COPY --from=builder /app /app

# 设置环境变量使虚拟环境生效
ENV PATH="/app/.venv/bin:$PATH"

# 设置工作目录
WORKDIR /app

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["uwsgi", "--ini", "uwsgi.ini"] 