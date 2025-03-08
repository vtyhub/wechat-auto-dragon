from pywinauto import Application
import pyperclip
import re
import time
import random


# 窗口默认标题
window_title = "测试"
# 轮询间隔时间，单位为秒
refresh = 2
# 轮询时间随机值
random_refresh = 1
# 窗口时间
window_time = 0.5
# 随机窗口时间
random_window_time = 0.1
# 默认接龙内容
content = "测试"


class WechatAutoDragon:
    def __init__(self, title, log_out=True):
        self.title = title
        self.app = Application(backend='uia').connect(title_re=self.title )
        self.window = self.app.window(title_re=self.title )
        self.last_message = ""
        self.content = ""
        self.log_out = log_out
        

    def monitor_messages(self):
        """监控聊天窗口新消息"""
        message_list = self.window.child_window(control_type='List', found_index=0)
        messages = message_list.descendants(control_type='ListItem')

        
        if messages:
            latest_msg_item = messages[-1]            
            return latest_msg_item
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
        return self.content
    
    def click_button(self, item):
        """点击指定标题的按钮"""
        try:
            buttons = item.descendants(control_type="Button")
            target_button = None
            
            if self.log_out:
                print("找到的按钮列表：")
            for idx, btn in enumerate(buttons):
                if self.log_out:
                    print(f"按钮 {idx}: {btn.window_text()}")
                if btn.window_text() == "":  # 指定需要点击的按钮标题
                    target_button = btn
                    break
            if self.log_out:
                print("\n")
        
            if target_button:
                target_button.set_focus()
                target_button.click_input()
                time.sleep(random.uniform(window_time-random_window_time, window_time+random_window_time))
            else:
                print("未找到指定标题的按钮\n")
        except Exception as e:
            print(f"点击按钮失败: {str(e)}\n")
                
        
    
    def run(self, content):
        while True:
            self.content = content
            temp_random_time = random.uniform(refresh-random_refresh, refresh+random_refresh)
            try:
                last_msg_item = self.monitor_messages()
                current_msg_list = last_msg_item.descendants(control_type='Text')
                
                if self.log_out:
                    print("找到的文本列表：")
                    for idx, msg in enumerate(current_msg_list):
                        print(f"文本 {idx}: {msg.window_text()}")
                    print("\n")
                
                current_msg = current_msg_list[0].window_text()


                if current_msg and current_msg != self.last_message:
                    if self.is_dragon_message(current_msg):
                        self.click_button(last_msg_item)
                        reply = self.generate_reply(current_msg)
                        self.send_message(reply)
                        print(f"已发送接龙：\n{reply}")
                        self.last_message = current_msg
                        break
                print(f"等待中...{temp_random_time:.2f}s")
                time.sleep(temp_random_time)
            except Exception as e:
                print(f"发生错误：{str(e)}\n")
                time.sleep(temp_random_time)
        time.sleep(random.uniform(window_time-random_window_time, window_time+random_window_time))
            

if __name__ == "__main__":
    auto_dragon = WechatAutoDragon(window_title)
    auto_dragon.run(content)
    