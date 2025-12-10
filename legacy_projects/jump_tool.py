import tkinter as tk
from tkinter import messagebox
import time
import threading
import pyautogui

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("自动点击器 (Auto Clicker)")
        self.root.geometry("300x250")
        
        # Number of clicks
        self.lbl_clicks = tk.Label(root, text="点击次数 (Clicks):")
        self.lbl_clicks.pack(pady=5)
        self.entry_clicks = tk.Entry(root)
        self.entry_clicks.pack(pady=5)
        self.entry_clicks.insert(0, "10")
        
        # Duration
        self.lbl_duration = tk.Label(root, text="限定时间 (Seconds):")
        self.lbl_duration.pack(pady=5)
        self.entry_duration = tk.Entry(root)
        self.entry_duration.pack(pady=5)
        self.entry_duration.insert(0, "5")
        
        # Start Button
        self.btn_start = tk.Button(root, text="开始 (Start)", command=self.start_clicking_thread, bg="#4CAF50", fg="white")
        self.btn_start.pack(pady=20)
        
        # Status Label
        self.lbl_status = tk.Label(root, text="准备就绪 (Ready)")
        self.lbl_status.pack(pady=5)
        
        self.is_running = False

    def start_clicking_thread(self):
        if self.is_running:
            return
        
        try:
            clicks = int(self.entry_clicks.get())
            duration = float(self.entry_duration.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
            
        self.is_running = True
        self.btn_start.config(state=tk.DISABLED)
        
        # Run in a separate thread to keep UI responsive
        thread = threading.Thread(target=self.run_clicker, args=(clicks, duration))
        thread.daemon = True
        thread.start()

    def run_clicker(self, clicks, duration):
        try:
            # Countdown
            for i in range(3, 0, -1):
                self.update_status(f"{i}秒后开始... (Starting in {i}s)")
                time.sleep(1)
            
            self.update_status("正在点击... (Clicking...)")
            
            if clicks <= 0:
                return

            interval = duration / clicks if clicks > 0 else 0
            
            start_time = time.time()
            
            for i in range(clicks):
                pyautogui.click()
                
                # Calculate remaining time and sleep
                elapsed = time.time() - start_time
                expected_elapsed = (i + 1) * interval
                sleep_time = expected_elapsed - elapsed
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            self.update_status("完成! (Done!)")
            messagebox.showinfo("完成", f"已在 {duration}秒内完成 {clicks} 次点击")
            
        except Exception as e:
            self.update_status(f"出错: {str(e)}")
            print(e)
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.btn_start.config(state=tk.NORMAL))

    def update_status(self, text):
        self.root.after(0, lambda: self.lbl_status.config(text=text))

if __name__ == "__main__":
    # Fail-safe: Move mouse to upper-left corner to abort
    pyautogui.FAILSAFE = True
    
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
