# FastAPI 测试最佳实践指南

本指南概述了在 FastAPI 应用程序中实施测试的最佳实践。

## 架构概述

我们的应用采用了以下分层架构：

1. **Model 层**：数据库模型和 Pydantic 模型（数据验证和序列化）
2. **Services 层**：业务逻辑
3. **Router 层**：API 端点和请求处理

这种架构遵循"胖服务层，瘦路由层"的原则，将业务逻辑从路由处理中分离出来。

## 测试策略

我们的测试策略包括三种类型的测试：

### 1. 单元测试 (Unit Tests)

单元测试针对独立组件，主要是 **Services 层**。这些测试验证：

- 服务函数的正确性
- 错误处理
- 边界条件

**示例：** `tests/test_services.py`

### 2. 集成测试 (Integration Tests)

集成测试验证 API 端点的功能，测试整个请求处理流程，包括：

- HTTP 状态码
- 响应内容
- 异常处理

**示例：** `tests/test_endpoints.py`

### 3. 模型测试 (Model Tests)

测试 Pydantic 模型的验证逻辑，确保：

- 数据验证正确
- 默认值正常工作
- 类型转换按预期进行

## 测试环境

我们的测试环境使用：

- 内存 SQLite 数据库，而不是生产环境的 PostgreSQL
- 异步测试客户端 (AsyncClient)
- Pytest 和 pytest-asyncio 进行异步测试

## 最佳实践

### 依赖注入

- 使用 `app.dependency_overrides` 替换依赖项
- 提供测试专用的数据库会话和其他资源

### 测试隔离

- 每个测试前创建新的数据库表
- 测试后清理数据库
- 使用独立的测试会话

### Mock vs 真实依赖

- 尽可能使用真实依赖（如内存数据库）
- 只 mock 外部服务（如支付网关、第三方 API）

### 异步测试

- 使用 `@pytest.mark.asyncio` 标记异步测试
- 使用 AsyncClient 进行异步请求

## 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_services.py

# 运行特定测试
pytest tests/test_services.py::TestOrdersService::test_create_order_success

# 生成测试覆盖率报告
pytest --cov=app --cov-report=term --cov-report=html
```

## 结论

在 FastAPI 应用中，我们推荐使用"胖服务层"方法，将业务逻辑与 API 处理分离。这种方法提供以下优势：

1. **更好的测试性能**：可以直接测试服务层，无需通过 HTTP 请求
2. **更高的代码复用性**：服务可以被多个路由调用
3. **关注点分离**：路由负责 API 处理，服务负责业务逻辑

通过将测试重点放在服务层，我们可以更有效地测试业务逻辑，同时使用集成测试验证端到端流程。 