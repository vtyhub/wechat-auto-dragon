from pywinauto import Application
import pyperclip
import re
import time
import random


# 窗口标题，根据实际情况修改
window_title = "群名"
# 轮询间隔时间，单位为秒
refresh = 3
# 轮询时间随机值
random_refresh = 0.8
# 窗口时间
window_time = 0.5
# 随机窗口时间
random_window_time = 0.1
# 接龙内容
content = "内容"

class WechatAutoDragon:
    def __init__(self):
        self.app = Application(backend='uia').connect(title_re=window_title )
        self.window = self.app.window(title_re=window_title )
        self.last_message = ""

    def monitor_messages(self):
        """监控聊天窗口新消息"""
        message_list = self.window.child_window(control_type='List', found_index=0)
        messages = message_list.descendants(control_type='ListItem')

        
        if messages:
            latest_msg_item = messages[-1]
            latest_msg = latest_msg_item.window_text()
            
             # 精确查找最后一条消息中的按钮
            try:
                buttons = latest_msg_item.descendants(control_type="Button")
                
                print("找到的按钮列表：")
                for idx, btn in enumerate(buttons):
                    print(f"按钮 {idx}: {btn.window_text()}")
                if len(buttons) == 2:  # 确保有足够多的按钮
                    button = buttons[0]  # 根据索引选择正确的按钮
                    button.click_input()
                    time.sleep(random.uniform(window_time-random_window_time, window_time+random_window_time))  # 等待弹窗加载

            except Exception as e:
                print(f"点击按钮失败: {str(e)}")
                
            return latest_msg
        return ""

    def is_dragon_message(self, msg):
        """判断是否为接龙消息"""
        pattern = r'#接龙.*?(\d+\. .+?(\n|$)){1,}'
        return re.search(pattern, msg, re.DOTALL)

    def generate_reply(self, msg):
        """生成接龙回复"""
        # 提取最后一条接龙编号
        last_number = max([int(n) for n in re.findall(r'^(\d+)\.', msg, re.M) if n.isdigit()] + [0])
        return f"{last_number + 1}. {self.get_user_name()}"

    def send_message(self, text):
        """发送消息"""
        input_box = self.window.child_window(control_type='Edit', found_index=0)
        
        pyperclip.copy(text)
        # 确保输入框已聚焦
        input_box.set_focus()
        # 使用 set_text 设置文本内容，避免输入法干扰
        input_box.type_keys('^v')
        # 触发回车键发送消息
        input_box.type_keys('{ENTER}')

    def get_user_name(self):
        """获取输入内容"""
        return content
    
    def run(self):
        while True:
            temp_random_time = random.uniform(refresh-random_refresh, refresh+random_refresh)
            try:
                current_msg = self.monitor_messages()
                # print(f"当前消息：\n{current_msg}")
                if current_msg and current_msg != self.last_message:
                    if self.is_dragon_message(current_msg):
                        reply = self.generate_reply(current_msg)
                        self.send_message(reply)
                        print(f"已发送接龙：\n{reply}")
                        self.last_message = current_msg
                        break
                print(f"等待中...{temp_random_time:.2f}s")
                time.sleep(temp_random_time)
            except Exception as e:
                print(f"发生错误：{str(e)}")
                time.sleep(temp_random_time)
            

if __name__ == "__main__":
    auto_dragon = WechatAutoDragon()
    auto_dragon.run()
    