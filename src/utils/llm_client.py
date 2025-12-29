"""
LLM 客户端封装（支持 DeepSeek-V3 和 OpenAI）
"""
import os
import json
from typing import Optional, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """LLM 客户端（优先使用 DeepSeek-V3）"""
    
    def __init__(
        self, 
        provider: Literal["deepseek", "openai"] = "deepseek",
        model: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        初始化 LLM 客户端
        
        Args:
            provider: LLM 提供商，"deepseek" 或 "openai"
            model: 模型名称，如果为 None 则使用默认值
            temperature: 温度参数
        """
        self.provider = provider
        
        if provider == "deepseek":
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
            
            # DeepSeek-V3 默认配置
            default_model = model or "deepseek-chat"
            base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
            
            self.llm = ChatOpenAI(
                model=default_model,
                temperature=temperature,
                api_key=api_key,
                base_url=base_url
            )
        else:  # OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
            
            default_model = model or "gpt-4"
            self.llm = ChatOpenAI(
                model=default_model,
                temperature=temperature,
                api_key=api_key
            )
    
    async def call(self, system_prompt: str, user_prompt: str) -> str:
        """调用 LLM"""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = await self.llm.ainvoke(messages)
        return response.content
    
    def get_structured_llm(self, schema):
        """
        获取支持结构化输出的 LLM
        
        注意：DeepSeek API 目前不支持 response_format 参数，
        所以对于 DeepSeek，我们使用 JSON Mode + 手动解析的方式
        """
        if self.provider == "deepseek":
            # DeepSeek 不支持 with_structured_output，使用 JSON Mode
            # 返回一个包装的 LLM，它会自动处理 JSON 解析
            return StructuredLLMWrapper(self.llm, schema)
        else:
            # OpenAI 支持 with_structured_output
            return self.llm.with_structured_output(schema)


class StructuredLLMWrapper:
    """
    为 DeepSeek 提供的结构化输出包装器
    使用 JSON Mode + 手动解析的方式实现结构化输出
    """
    
    def __init__(self, llm, schema):
        self.llm = llm
        self.schema = schema
        
    async def ainvoke(self, messages, **kwargs):
        """
        调用 LLM 并解析为结构化输出
        
        Args:
            messages: LangChain 消息列表
            **kwargs: 其他参数
            
        Returns:
            解析后的 schema 实例
        """
        # 修改 prompt，要求返回 JSON 格式
        enhanced_messages = self._enhance_messages_for_json(messages)
        
        # 调用 LLM
        response = await self.llm.ainvoke(enhanced_messages, **kwargs)
        
        # 解析 JSON 响应
        content = response.content if hasattr(response, 'content') else str(response)
        
        # 尝试提取 JSON（可能包含在代码块中）
        json_str = self._extract_json(content)
        
        # 解析 JSON 并创建 schema 实例
        try:
            data = json.loads(json_str)
            # 字段映射（处理常见的字段名不匹配问题）
            data = self._map_fields(data)
            return self.schema(**data)
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            # 如果解析失败，尝试使用 Pydantic 的验证
            try:
                return self.schema.parse_raw(json_str)
            except:
                # 最后尝试直接构造
                raise ValueError(f"无法解析结构化输出: {e}\n原始内容: {content}")
    
    def _map_fields(self, data):
        """映射字段名，处理常见的字段名不匹配"""
        # 字段名映射表
        field_mapping = {
            'action': 'action_type',
            'actionType': 'action_type',
            'type': 'action_type',
            'reason': 'reasoning',
            'reasoning_text': 'reasoning',
            'text': 'content',  # 对于 SpeakDecision
            'message': 'content',  # 对于 SpeakDecision
        }
        
        # 应用字段映射
        mapped_data = {}
        for key, value in data.items():
            # 映射字段名
            mapped_key = field_mapping.get(key, key)
            
            # 处理 target 字段：如果是字符串，尝试提取数字
            if mapped_key == 'target' and isinstance(value, str):
                # 尝试从字符串中提取数字（如 "玩家1" -> 1）
                import re
                numbers = re.findall(r'\d+', value)
                if numbers:
                    value = int(numbers[0])
                else:
                    # 如果无法提取，设为 None
                    value = None
            
            mapped_data[mapped_key] = value
        
        # 确保必需字段存在
        schema_fields = {}
        if hasattr(self.schema, 'model_fields'):
            schema_fields = self.schema.model_fields
        elif hasattr(self.schema, '__fields__'):
            schema_fields = self.schema.__fields__
        
        # 为缺失的必需字段设置默认值
        for field_name, field_info in schema_fields.items():
            if field_name not in mapped_data:
                # 检查是否有默认值
                if hasattr(field_info, 'default'):
                    default = field_info.default
                    if default is not None:
                        mapped_data[field_name] = default
                    elif hasattr(field_info, 'default_factory'):
                        mapped_data[field_name] = field_info.default_factory()
                # 如果没有默认值且字段是必需的，设置合理的默认值
                elif field_name == 'thought' and 'reasoning' in mapped_data:
                    mapped_data[field_name] = mapped_data.get('reasoning', '')
                elif field_name == 'reasoning' and 'thought' in mapped_data:
                    mapped_data[field_name] = mapped_data.get('thought', '')
                elif field_name == 'confidence':
                    mapped_data[field_name] = 0.5
                elif field_name == 'target' and mapped_data.get('action_type') in ['skip', 'explode']:
                    mapped_data[field_name] = None
        
        return mapped_data
    
    def _enhance_messages_for_json(self, messages):
        """增强消息，要求返回 JSON 格式"""
        enhanced = []
        
        # 获取 schema 的字段信息和示例
        schema_fields = {}
        if hasattr(self.schema, 'model_fields'):
            schema_fields = self.schema.model_fields
        elif hasattr(self.schema, '__fields__'):
            schema_fields = self.schema.__fields__
        
        # 获取示例（如果有）
        example = None
        if hasattr(self.schema, 'Config') and hasattr(self.schema.Config, 'json_schema_extra'):
            example = self.schema.Config.json_schema_extra.get('example')
        
        # 构建字段说明
        field_descriptions = []
        for field_name, field_info in schema_fields.items():
            field_type = "string"
            is_required = True
            default_value = None
            
            if hasattr(field_info, 'annotation'):
                field_type = str(field_info.annotation)
            if hasattr(field_info, 'default'):
                default_value = field_info.default
                if default_value is not None:
                    is_required = False
            
            field_desc = f"- {field_name} ({field_type})"
            if not is_required:
                field_desc += f" [可选，默认: {default_value}]"
            field_descriptions.append(field_desc)
        
        # 构建 JSON 格式指令
        json_format_instruction = f"""

重要：请严格按照以下 JSON 格式返回结果，不要使用其他字段名。

必需字段：
{chr(10).join(field_descriptions)}

JSON 格式要求：
1. 必须使用上述确切的字段名（如 action_type 而不是 action）
2. target 字段必须是整数（玩家ID），不是字符串（如 1 而不是 "玩家1"）
3. 所有必需字段都必须包含
4. 只返回纯 JSON 对象，不要包含任何其他文本、说明或代码块标记
5. 确保 JSON 格式完全正确，可以被直接解析

示例格式：
{json.dumps(example, ensure_ascii=False, indent=2) if example else '{"thought": "...", "action_type": "vote", "target": 1, "confidence": 0.75, "reasoning": "..."}'}
"""
        
        for msg in messages:
            if hasattr(msg, 'content'):
                content = msg.content
                # 如果是 system 消息，添加 JSON 格式要求
                if isinstance(msg, SystemMessage):
                    content += json_format_instruction
                enhanced.append(type(msg)(content=content))
            else:
                enhanced.append(msg)
        return enhanced
    
    def _extract_json(self, text):
        """从文本中提取 JSON"""
        # 尝试直接解析
        text = text.strip()
        
        # 如果包含代码块，提取 JSON 部分
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end != -1:
                text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end != -1:
                text = text[start:end].strip()
        
        # 尝试找到 JSON 对象
        start_idx = text.find('{')
        end_idx = text.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            text = text[start_idx:end_idx + 1]
        
        return text

