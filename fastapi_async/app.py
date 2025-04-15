from fastapi import FastAPI, Request
import asyncio
from contextlib import asynccontextmanager
import uuid
import time
from context import request_id_var, setup_logging

# 初始化日志，设置 sql_echo=False 避免冗余的 SQL 日志
logger = setup_logging(sql_echo=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Application startup and shutdown logic
    # We no longer need to create tables here since we'll use Alembic migrations
    yield

app = FastAPI(lifespan=lifespan)

# 添加中间件来生成请求 ID 并将其添加到日志上下文
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    # 生成一个唯一的请求ID
    request_id = str(uuid.uuid4())
    
    # 将请求 ID 设置到上下文变量中
    token = request_id_var.set(request_id)
    
    # 将请求 ID 绑定到请求状态
    request.state.request_id = request_id
    
    try:
        # 记录请求开始
        logger.info(f"Request started: {request.method} {request.url.path}")
        
        # 记录处理时间
        start_time = time.time()
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 记录请求结束
        logger.info(f"Request completed: {request.method} {request.url.path} - "
                    f"Took: {process_time:.4f}s - Status: {response.status_code}")
        
        # 将请求 ID 添加到响应头
        response.headers["X-Request-ID"] = request_id
        
        return response
    except Exception as e:
        logger.exception(f"Error processing request: {str(e)}")
        raise
    finally:
        # 重置上下文变量，避免泄漏到其他请求
        request_id_var.reset(token)

# 导入 routers
from routers import users, orders

# Include routers
app.include_router(users.router)
app.include_router(orders.router)

@app.get("/ping")
async def ping():
    logger.info("Ping request received")
    return {"message": "pong"}

@app.get("/sleep")
async def sleep_endpoint():
    logger.info("Sleep request received, waiting for 5 seconds")
    await asyncio.sleep(5)  # 异步 sleep，不会阻塞其他请求
    logger.info("Sleep completed")
    return {"message": "Woke up after 5 seconds"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5050)