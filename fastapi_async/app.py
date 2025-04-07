from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/ping")
async def ping():
    return {"message": "pong"}

@app.get("/sleep")
async def sleep_endpoint():
    await asyncio.sleep(5)  # 异步 sleep，不会阻塞其他请求
    return {"message": "Woke up after 5 seconds"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5050) 