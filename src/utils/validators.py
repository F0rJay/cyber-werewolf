"""
验证器工具
"""
from typing import Any, Type
from pydantic import BaseModel, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def validate_with_retry(data: Any, schema: Type[BaseModel]) -> BaseModel:
    """
    带重试的验证函数
    
    Args:
        data: 待验证的数据
        schema: Pydantic Schema
    
    Returns:
        验证后的模型实例
    
    Raises:
        ValidationError: 验证失败（重试3次后）
    """
    try:
        if isinstance(data, dict):
            return schema(**data)
        elif isinstance(data, str):
            # 如果是 JSON 字符串，需要先解析
            import json
            data_dict = json.loads(data)
            return schema(**data_dict)
        else:
            return schema(data)
    except ValidationError as e:
        # 最后一次重试仍然失败
        raise e

