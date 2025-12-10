from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
import threading
import time
import os

# 注意：
# 1. 此脚本需要在 Android 环境下运行（如 Pydroid 3 或打包成 APK）。
# 2. 模拟点击 (input tap) 通常需要手机拥有 ROOT 权限，或者在特定环境下才能点击其他 APP。
# 3. 如果没有 ROOT 权限，此脚本可能无法点击游戏窗口。

class AutoClickerApp(App):
    def build(self):
        self.title = "Python Auto Clicker"
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 点击次数
        layout.add_widget(Label(text='点击次数 (Clicks):', size_hint_y=None, height=30))
        self.clicks_input = TextInput(text='10', multiline=False, input_filter='int', size_hint_y=None, height=40)
        layout.add_widget(self.clicks_input)
        
        # 时间
        layout.add_widget(Label(text='总时间 (Seconds):', size_hint_y=None, height=30))
        self.duration_input = TextInput(text='5', multiline=False, input_filter='float', size_hint_y=None, height=40)
        layout.add_widget(self.duration_input)
        
        # 坐标 (手机没有鼠标，必须指定坐标)
        layout.add_widget(Label(text='X 坐标 (0-1080):', size_hint_y=None, height=30))
        self.x_input = TextInput(text='500', multiline=False, input_filter='int', size_hint_y=None, height=40)
        layout.add_widget(self.x_input)
        
        layout.add_widget(Label(text='Y 坐标 (0-2400):', size_hint_y=None, height=30))
        self.y_input = TextInput(text='1000', multiline=False, input_filter='int', size_hint_y=None, height=40)
        layout.add_widget(self.y_input)
        
        # 状态标签
        self.status_label = Label(text='准备就绪 (Ready)', size_hint_y=None, height=30)
        layout.add_widget(self.status_label)
        
        # 开始按钮
        self.btn = Button(text='开始 (Start)', size_hint_y=None, height=60, background_color=(0, 1, 0, 1))
        self.btn.bind(on_press=self.start_clicking)
        layout.add_widget(self.btn)
        
        return layout

    def start_clicking(self, instance):
        # 禁用按钮防止重复点击
        self.btn.disabled = True
        threading.Thread(target=self.run_clicker).start()

    def run_clicker(self):
        try:
            clicks = int(self.clicks_input.text)
            duration = float(self.duration_input.text)
            x = int(self.x_input.text)
            y = int(self.y_input.text)
            
            if clicks <= 0:
                return

            interval = duration / clicks
            
            self.update_status(f"3秒后开始... (Starting in 3s)")
            time.sleep(3)
            
            self.update_status("正在运行... (Running...)")
            
            for i in range(clicks):
                # Android 核心点击命令
                # 注意：这通常需要 ROOT 权限才能点击其他 APP
                cmd = f"input tap {x} {y}"
                print(f"Executing: {cmd}")
                os.system(cmd)
                
                time.sleep(interval)
                
            self.update_status("完成! (Done!)")
            
        except Exception as e:
            self.update_status(f"错误: {str(e)}")
        finally:
            # 恢复按钮状态 (需要在主线程执行)
            Clock.schedule_once(lambda dt: setattr(self.btn, 'disabled', False))

    def update_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', text))

if __name__ == '__main__':
    AutoClickerApp().run()
