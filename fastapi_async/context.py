import contextvars
import logging

# 创建请求ID的上下文变量
request_id_var = contextvars.ContextVar("request_id", default="undefined")

# 创建过滤器来添加 request_id
class RequestIdFilter(logging.Filter):
    def filter(self, record):
        # 始终设置 request_id 属性，无论是否已存在
        record.request_id = request_id_var.get()
        return True

# 自定义 Formatter 来处理 request_id
class RequestIdFormatter(logging.Formatter):
    def format(self, record):
        # 确保记录中有 request_id 属性
        if not hasattr(record, 'request_id'):
            record.request_id = request_id_var.get()
        return super().format(record)

# 初始化日志配置
def setup_logging(sql_echo=False):
    # 清除所有已存在的处理器
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    # 创建处理器
    console_handler = logging.StreamHandler()
    
    # 创建格式化器
    formatter = RequestIdFormatter(
        '%(asctime)s - %(levelname)s - [%(request_id)s] - %(name)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # 添加过滤器到处理器
    request_id_filter = RequestIdFilter()
    console_handler.addFilter(request_id_filter)
    
    # 设置根日志记录器
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    # 确保我们的过滤器在根日志记录器上
    if not any(isinstance(f, RequestIdFilter) for f in root_logger.filters):
        root_logger.addFilter(request_id_filter)
    
    # 配置 SQLAlchemy 日志
    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    
    # 根据配置设置 SQLAlchemy 日志级别
    if sql_echo:
        sqlalchemy_logger.setLevel(logging.INFO)
    else:
        sqlalchemy_logger.setLevel(logging.WARNING)  # 只显示警告及以上级别
    
    # 停止 SQLAlchemy 日志向上传播，避免重复
    sqlalchemy_logger.propagate = False
    
    # 清除现有处理器并添加新的处理器
    sqlalchemy_logger.handlers = []
    sqlalchemy_logger.addHandler(console_handler)
    sqlalchemy_logger.addFilter(request_id_filter)
    
    # # 禁用其他库的过多日志
    # logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    # uvicorn_logger = logging.getLogger('uvicorn.error')
    # uvicorn_logger.handlers = []
    # uvicorn_logger.addHandler(console_handler)
    # uvicorn_logger.propagate = False
    
    # 返回根日志记录器以便可以在其他地方使用
    return root_logger 