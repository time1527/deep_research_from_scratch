from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import json

console = Console()

def format_message_content(message):
    """将消息内容转换为可展示的字符串"""
    parts = []
    tool_calls_processed = False
    
    # 处理主要内容
    if isinstance(message.content, str):
        parts.append(message.content)
    elif isinstance(message.content, list):
        # 处理复杂内容，例如工具调用（Anthropic 格式）
        for item in message.content:
            if item.get('type') == 'text':
                parts.append(item['text'])
            elif item.get('type') == 'tool_use':
                parts.append(f"\n🔧 工具调用：{item['name']}")
                parts.append(f"   参数：{json.dumps(item['input'], indent=2)}")
                parts.append(f"   ID：{item.get('id', 'N/A')}")
                tool_calls_processed = True
    else:
        parts.append(str(message.content))
    
    # 处理附加在消息上的工具调用（OpenAI 格式）——仅在尚未处理时进行
    if not tool_calls_processed and hasattr(message, 'tool_calls') and message.tool_calls:
        for tool_call in message.tool_calls:
            parts.append(f"\n🔧 工具调用：{tool_call['name']}")
            parts.append(f"   参数：{json.dumps(tool_call['args'], indent=2)}")
            parts.append(f"   ID：{tool_call['id']}")
    
    return "\n".join(parts)


def format_messages(messages):
    """使用 Rich 格式化并展示消息列表"""
    for m in messages:
        msg_type = m.__class__.__name__.replace('Message', '')
        content = format_message_content(m)

        if msg_type == 'Human':
            console.print(Panel(content, title="🧑 用户", border_style="blue"))
        elif msg_type == 'Ai':
            console.print(Panel(content, title="🤖 助手", border_style="green"))
        elif msg_type == 'Tool':
            console.print(Panel(content, title="🔧 工具输出", border_style="yellow"))
        else:
            console.print(Panel(content, title=f"📝 {msg_type}", border_style="white"))


def format_message(messages):
    """format_messages 的别名，保留向后兼容"""
    return format_messages(messages)


def show_prompt(prompt_text: str, title: str = "提示词", border_style: str = "blue"):
    """
    使用 Rich 展示提示词，并高亮 XML 标签。
    
    Args:
        prompt_text: 要展示的提示字符串
        title: 面板标题（默认："提示词"）
        border_style: 面板边框颜色（默认："blue"）
    """
    # 构造提示的格式化展示
    formatted_text = Text(prompt_text)
    formatted_text.highlight_regex(r'<[^>]+>', style="bold blue")  # 高亮 XML 标签
    formatted_text.highlight_regex(r'##[^#\n]+', style="bold magenta")  # 高亮二级标题
    formatted_text.highlight_regex(r'###[^#\n]+', style="bold cyan")  # 高亮三级标题

    # 以面板形式展示，便于阅读
    console.print(Panel(
        formatted_text, 
        title=f"[bold green]{title}[/bold green]",
        border_style=border_style,
        padding=(1, 2)
    ))
