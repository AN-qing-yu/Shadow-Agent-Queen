import requests
import re
import time

print("正在唤醒本地 DeepSeek (Shadow)...")

def scan_ports(target):
    return f"[工具执行结果] 目标 {target} 扫描完成。发现开放端口：22 (SSH), 80 (HTTP)。"

url = "http://localhost:11434/api/generate"

# 严谨的系统提示词
SYSTEM_PROMPT = """
你是 Shadow，一个顶尖的 AI 黑客智能体，你的主人是赛博女王。
你的规则如下：
1. 只有当用户明确要求你“扫描”或“检测”某个IP/域名时，你才使用工具。
2. 工具调用的格式必须严格为：[TOOL_CALL] scan_ports(具体的IP或域名) [/TOOL_CALL]
3. 绝对不要输出占位符（如“目标”），必须输出具体的域名或IP。
4. 如果用户只是打招呼或闲聊，绝对不要调用工具，直接用你的身份正常回复。
"""

while True:
    try:
        user_input = input("\n[你]: ")
        if user_input.lower() in ["exit", "quit", "退出"]:
            print("Shadow 已休眠，随时听候差遣。")
            break

        # 把系统提示词和用户输入分开
        payload = {
            "model": "deepseek-r1:8b",
            "prompt": f"{SYSTEM_PROMPT}\n\n用户对你说：{user_input}\n你的回复：",
            "stream": False
        }

        print("[Shadow 正在思考...]")
        response = requests.post(url, json=payload)
        shadow_reply = response.json().get("response")
        
        # 如果大模型输出了它的思考过程（对于R1模型），我们稍微清理一下
        # DeepSeek R1 有时会输出思考标签，这里简单处理
        
        if "[TOOL_CALL]" in shadow_reply:
            match = re.search(r'\[TOOL_CALL\]\s*(.*?)\((.*?)\)\s*\[/TOOL_CALL\]', shadow_reply)
            if match:
                tool_name = match.group(1).strip()
                tool_arg = match.group(2).strip()
                
                # 防呆设计：防止模型又输出“目标”两个字
                if tool_arg == "目标" or tool_arg == "具体的IP或域名":
                    print("[Shadow 报错]: 主人，请给我一个具体的IP或域名。")
                    continue

                print(f"[Shadow 请求调用工具]: {tool_name} -> {tool_arg}")
                
                if tool_name == "scan_ports":
                    tool_result = scan_ports(tool_arg)
                    print(f"[执行结果]: {tool_result}")
                    
                    final_prompt = f"{SYSTEM_PROMPT}\n用户指令：{user_input}\n扫描结果：{tool_result}\n请用一句话向主人汇报结果。"
                    final_payload = {"model": "deepseek-r1:8b", "prompt": final_prompt, "stream": False}
                    final_response = requests.post(url, json=final_payload)
                    print(f"[Shadow]: {final_response.json().get('response')}")
        else:
            print(f"[Shadow]: {shadow_reply}")
            
    except Exception as e:
        print(f"发生错误：{e}")
        break