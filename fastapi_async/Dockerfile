# Use Python 3.11 as base image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Install uv
RUN apt-get update && apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh

# 设置 uv 的环境变量
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 设置工作目录
WORKDIR /app

# 首先只复制依赖相关文件
COPY uv.lock pyproject.toml /app/

# 安装依赖
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

COPY app.py .

# Expose the port the app runs on
EXPOSE 5050

# Command to run the application
CMD ["python", "app.py"] 