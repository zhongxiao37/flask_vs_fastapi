# FastAPI 异步应用测试指南

本测试套件为 FastAPI 异步应用提供了全面的 API 测试。

## 测试内容

测试套件包括以下测试：

1. 基础端点测试：
   - `/ping` 端点测试
   - `/sleep` 异步睡眠端点测试

2. 用户模块测试：
   - 创建用户测试
   - 获取用户列表测试

3. 订单模块测试：
   - 创建订单测试
   - 创建订单（用户不存在）测试
   - 获取订单列表测试

## 测试架构

测试套件使用以下组件：

- `pytest`：Python 测试框架
- `pytest-asyncio`：异步测试支持
- `httpx`：异步 HTTP 客户端
- `aiosqlite`：SQLite 异步支持

测试使用内存中的 SQLite 数据库替代了生产环境中的 PostgreSQL，以实现更快的测试执行和隔离。

## 运行测试

### 安装依赖

确保已安装所有依赖：

```bash
pip install -r requirements.txt
```

### 执行测试

运行所有测试：

```bash
pytest -v
```

或者使用提供的测试运行脚本：

```bash
# 运行所有测试
./run_tests.py -v

# 运行特定测试
./run_tests.py -v -t test_ping

# 生成测试覆盖率报告
./run_tests.py -v --cov
```

运行特定测试：

```bash
pytest -v test_app.py::test_ping
```

### 生成测试覆盖率报告

可以使用以下命令生成测试覆盖率报告：

```bash
pytest --cov=app --cov-report=term --cov-report=html
```

这将生成终端输出的覆盖率报告和HTML格式的详细报告（在`htmlcov`目录中）。

## 测试解释

- 每个测试前会创建全新的数据库表结构
- 测试完成后会清理数据库表
- 测试之间互相隔离，不会相互影响
- 使用依赖注入覆盖（dependency override）来控制数据库会话
- 使用 `ASGITransport` 进行异步测试，以确保正确测试异步API 