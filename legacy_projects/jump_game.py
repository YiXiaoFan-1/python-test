import tkinter as tk
from tkinter import messagebox
import time
import random
import sys
from enum import Enum
from collections import deque


class GameState(Enum):
    """游戏状态枚举"""
    RUNNING = 1
    GAME_OVER = 2
    PAUSED = 3
    WIN = 4


class Colors:
    """终端颜色"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'


class Particle:
    """粒子特效"""
    def __init__(self, x, y, char='*', lifetime=5):
        self.x = x
        self.y = y
        self.char = char
        self.lifetime = lifetime
        self.age = 0
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-1, -0.5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # 重力
        self.age += 1
        return self.age < self.lifetime


class PowerUp:
    """道具"""
    def __init__(self, x, y, type_='shield'):
        self.x = x
        self.y = y
        self.type = type_
        self.active = True
        self.char = '⚡' if type_ == 'speed' else '🛡️' if type_ == 'shield' else '⭐'


class JumpGame:
    """跳一跳游戏类 - GUI版本"""
    
    def __init__(self, master, width=60, height=15, difficulty=1):
        """初始化游戏"""
        self.master = master
        self.width = width
        self.height = height
        self.difficulty = difficulty
        
        # 游戏窗口大小
        self.cell_size = 30
        self.canvas_width = self.width * self.cell_size
        self.canvas_height = self.height * self.cell_size
        
        # 创建画布
        self.canvas = tk.Canvas(master, width=self.canvas_width, height=self.canvas_height, bg='#87CEEB')
        self.canvas.pack()
        
        # 状态栏
        self.status_frame = tk.Frame(master)
        self.status_frame.pack(fill=tk.X)
        
        self.score_label = tk.Label(self.status_frame, text="得分: 0", font=('Arial', 14, 'bold'))
        self.score_label.pack(side=tk.LEFT, padx=10)
        
        self.difficulty_label = tk.Label(self.status_frame, text=f"难度: {difficulty}", font=('Arial', 14))
        self.difficulty_label.pack(side=tk.LEFT, padx=10)
        
        self.hint_label = tk.Label(self.status_frame, text="长按空格蓄力跳跃", font=('Arial', 12), fg='#0066CC')
        self.hint_label.pack(side=tk.RIGHT, padx=10)
        
        # 玩家状态
        self.player_x = 5
        self.player_y = float(height - 3)
        self.is_jumping = False
        self.jump_velocity = 0
        self.jump_velocity_x = 0  # 水平速度
        # 调低重力，让抛物线更圆、更慢
        self.gravity = 0.3
        self.jump_power = -3.5
        
        # 游戏对象
        self.platforms = []
        self.obstacles = []
        self.powerups = []
        self.particles = []
        self.score = 0
        self.high_score = 0
        self.combo = 0
        self.max_combo = 0
        self.state = GameState.RUNNING
        
        # 特效和状态
        self.shield_active = False
        self.shield_time = 0
        self.speed_boost = False
        self.speed_time = 0
        self.camera_offset = 0
        self.shake_intensity = 0
        
        # 游戏配置
        self.platform_spacing = max(5, 10 - difficulty * 2)
        self.platform_width = max(4, 9 - difficulty)
        self.game_speed = 1 + difficulty * 0.3
        self.frame_count = 0
        
        # 输入缓冲
        self.input_buffer = deque(maxlen=5)
        self.jump_pressed = False
        
        # 蓄力系统
        self.charging = False
        self.charge_power = 0
        self.max_charge_power = 100
        # 调低蓄力速度，让进度条和抛物线生成更平滑
        self.charge_rate = 2  # 每帧增加的蓄力值
        self.trajectory_points = []  # 轨迹预测点（使用浮点坐标）
        
        # 绑定键盘事件
        self.master.bind('<KeyPress-space>', self.on_space_press)
        self.master.bind('<KeyRelease-space>', self.on_space_release)
        
        # 初始化
        self._init_platforms()
        
        # 开始游戏循环
        self.running = True
        self.update()
        
    def on_space_press(self, event):
        """空格键按下 - 开始蓄力"""
        # 只在未蓄力且未在空中时才开始蓄力，避免重复重置
        if (not self.is_jumping 
                and self.state == GameState.RUNNING 
                and not self.charging):
            self.charging = True
            self.charge_power = 0
    
    def on_space_release(self, event):
        """空格键释放 - 执行跳跃"""
        if self.charging:
            self.charging = False
            self.jump(self.charge_power)
            self.charge_power = 0
            self.trajectory_points = []
    
    def _init_platforms(self):
        """初始化游戏平台"""
        # 创建初始平台，确保玩家能站上去
        self.platforms.append({
            'x': 0,
            'y': self.height - 2,
            'length': 8,
            'type': 'normal',
            'landed_on': False,  # 是否已经被踩过（用于加分）
        })
        
        x = 10  # 从第二个平台开始
        while x < self.width * 3:
            platform_length = random.randint(self.platform_width, self.platform_width + 3)
            y = random.randint(self.height - 5, self.height - 2)
            self.platforms.append({
                'x': x,
                'y': y,
                'length': platform_length,
                'type': 'normal',
                'landed_on': False,
            })
            
            # 随机添加障碍物
            if random.random() < 0.3:
                obs_x = x + platform_length + 1
                obs_y = y - 1
                self.obstacles.append({
                    'x': obs_x,
                    'y': obs_y,
                    'width': 2
                })
            
            x += self.platform_spacing + platform_length + 1
    
    def _draw(self):
        """绘制游戏画面"""
        # 清空画布
        self.canvas.delete('all')
        
        # 绘制平台
        for platform in self.platforms:
            if 0 <= platform['x'] < self.width:
                x1 = platform['x'] * self.cell_size
                y1 = platform['y'] * self.cell_size
                x2 = (platform['x'] + platform['length']) * self.cell_size
                y2 = (platform['y'] + 1) * self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill='#8B4513', outline='#654321', width=2)
        
        # 绘制障碍物
        for obs in self.obstacles:
            if 0 <= obs['x'] < self.width:
                x1 = obs['x'] * self.cell_size
                y1 = obs['y'] * self.cell_size
                x2 = (obs['x'] + obs['width']) * self.cell_size
                y2 = (obs['y'] + 1) * self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill='#FF0000', outline='#8B0000', width=2)
        
        # 绘制轨迹预测（如果正在蓄力）
        if self.charging and self.trajectory_points:
            for i in range(len(self.trajectory_points) - 1):
                x1, y1 = self.trajectory_points[i]
                x2, y2 = self.trajectory_points[i + 1]
                # 绘制虚线轨迹
                self.canvas.create_line(
                    x1 * self.cell_size + self.cell_size // 2,
                    y1 * self.cell_size + self.cell_size // 2,
                    x2 * self.cell_size + self.cell_size // 2,
                    y2 * self.cell_size + self.cell_size // 2,
                    fill='#FFFF00', width=2, dash=(5, 3)
                )
            
            # 在终点画一个圆圈标记
            if self.trajectory_points:
                last_x, last_y = self.trajectory_points[-1]
                self.canvas.create_oval(
                    last_x * self.cell_size + 5,
                    last_y * self.cell_size + 5,
                    (last_x + 1) * self.cell_size - 5,
                    (last_y + 1) * self.cell_size - 5,
                    outline='#FF00FF', width=3, dash=(3, 3)
                )
        
        # 绘制玩家
        player_y = int(self.player_y)
        if 0 <= self.player_x < self.width and 0 <= player_y < self.height:
            x1 = self.player_x * self.cell_size + 5
            y1 = player_y * self.cell_size + 5
            x2 = (self.player_x + 1) * self.cell_size - 5
            y2 = (player_y + 1) * self.cell_size - 5
            self.canvas.create_oval(x1, y1, x2, y2, fill='#FFD700', outline='#FFA500', width=3)
        
        # 绘制蓄力条
        if self.charging:
            # 蓄力条背景
            bar_x = 10
            bar_y = 10
            bar_width = 200
            bar_height = 25
            
            self.canvas.create_rectangle(
                bar_x, bar_y, bar_x + bar_width, bar_y + bar_height,
                fill='#333333', outline='#FFFFFF', width=2
            )
            
            # 蓄力进度
            progress = min(self.charge_power / self.max_charge_power, 1.0)
            fill_width = int(bar_width * progress)
            
            # 根据蓄力程度改变颜色
            if progress < 0.33:
                color = '#00FF00'  # 绿色
            elif progress < 0.66:
                color = '#FFFF00'  # 黄色
            else:
                color = '#FF0000'  # 红色
            
            if fill_width > 0:
                self.canvas.create_rectangle(
                    bar_x, bar_y, bar_x + fill_width, bar_y + bar_height,
                    fill=color, outline=''
                )
            
            # 蓄力文本
            self.canvas.create_text(
                bar_x + bar_width // 2, bar_y + bar_height // 2,
                text=f"蓄力: {int(progress * 100)}%",
                fill='#FFFFFF', font=('Arial', 12, 'bold')
            )
        
        # 更新状态栏
        self.score_label.config(text=f"得分: {self.score}")
    
    def _check_collision(self):
        """检查碰撞"""
        player_y = int(self.player_y)
        player_x = int(self.player_x)
        
        # 检查与平台的碰撞（着陆）- 使用更宽松的条件
        for platform in self.platforms:
            # 玩家的脚接近平台顶部且在平台范围内
            if (player_y >= platform['y'] - 1 and 
                player_y <= platform['y'] + 1 and
                platform['x'] - 1 <= player_x < platform['x'] + platform['length'] and
                self.jump_velocity >= 0):  # 向下或静止
                # 着陆在平台上
                self.is_jumping = False
                self.jump_velocity = 0
                self.jump_velocity_x = 0
                self.player_y = platform['y'] - 1
                
                # 只有第一次踩到该平台才加分
                if not platform.get('landed_on', False):
                    platform['landed_on'] = True
                    self.score += 1
                return True
        
        # 检查与障碍物的碰撞
        for obs in self.obstacles:
            if (player_y >= obs['y'] - 1 and 
                player_y <= obs['y'] + 1 and 
                obs['x'] - 1 <= player_x < obs['x'] + obs['width'] + 1):
                self.game_over()
                return False
        
        # 掉下去了
        if player_y >= self.height - 1:
            self.game_over()
            return False
        
        return True
    
    def _update_physics(self):
        """更新物理"""
        if self.is_jumping:
            # 垂直速度受重力缓慢变化
            self.jump_velocity += self.gravity
            self.player_y += self.jump_velocity

            # 水平移动（与垂直一样，每帧小步运动）
            self.player_x += self.jump_velocity_x
            # 限制在屏幕范围内
            if self.player_x < 0:
                self.player_x = 0
            if self.player_x > self.width - 1:
                self.player_x = self.width - 1

            # 限制最大下落速度，避免掉落过快
            if self.jump_velocity > 1.5:
                self.jump_velocity = 1.5
        else:
            # 检查脚下是否有平台
            has_ground = False
            next_y = int(self.player_y + 1)
            
            for platform in self.platforms:
                if (next_y == platform['y'] and 
                    platform['x'] <= self.player_x < platform['x'] + platform['length']):
                    has_ground = True
                    break
            
            # 没有平台就下落
            if not has_ground and self.player_y < self.height - 1:
                self.is_jumping = True
                self.jump_velocity = 0.5
    
    def _calculate_trajectory(self, charge_power):
        """计算跳跃轨迹"""
        self.trajectory_points = []
        
        # 模拟跳跃轨迹
        power_multiplier = 1 + (charge_power / self.max_charge_power) * 1.5
        # 使用与实际跳跃相同的初速度，但整体更柔和
        sim_velocity_y = -1.0 * power_multiplier
        sim_velocity_x = 0.6 * power_multiplier  # 水平速度（向右）
        sim_x = self.player_x
        sim_y = self.player_y
        
        # 模拟更多帧，使轨迹更平滑（更长时间的抛物线）
        for i in range(80):
            sim_velocity_y += self.gravity  # 重力只作用于垂直方向
            sim_y += sim_velocity_y
            sim_x += sim_velocity_x  # 水平匀速运动
            
            # 限制范围
            if sim_y >= self.height or sim_x >= self.width:
                break
            
            if sim_y < 0:
                sim_y = 0

            # 使用浮点坐标记录轨迹点，使线条更顺滑
            self.trajectory_points.append((sim_x, sim_y))
            
            # 检查是否会碰到平台
            for platform in self.platforms:
                if (int(sim_y) >= platform['y'] - 1 and 
                    int(sim_y) <= platform['y'] + 1 and
                    platform['x'] - 1 <= sim_x < platform['x'] + platform['length'] and
                    sim_velocity_y > 0):
                    self.trajectory_points.append((int(sim_x), int(sim_y)))
                    return
    
    def _cleanup_platforms(self):
        """清理超出屏幕的平台"""
        self.platforms = [p for p in self.platforms if p['x'] < self.width + 10]
        self.obstacles = [o for o in self.obstacles if o['x'] < self.width + 10]
        
        # 生成新平台
        if self.platforms:
            last_x = max(p['x'] + p['length'] for p in self.platforms)
            if last_x < self.width * 2:
                platform_length = random.randint(self.platform_width, self.platform_width + 3)
                y = random.randint(self.height - 4, self.height - 2)
                self.platforms.append({
                    'x': last_x + self.platform_spacing,
                    'y': y,
                    'length': platform_length,
                    'type': 'normal'
                })
    
    def jump(self, charge=0):
        """跳跃"""
        if not self.is_jumping and self.state == GameState.RUNNING:
            self.is_jumping = True
            # 根据蓄力值计算跳跃力度（整体偏慢）
            power_multiplier = 1 + (charge / self.max_charge_power) * 1.5
            # 垂直向上速度（减小幅度）
            self.jump_velocity = -1.0 * power_multiplier
            # 水平向右速度（更小，便于观察抛物线）
            self.jump_velocity_x = 0.6 * power_multiplier
    
    def game_over(self):
        """游戏结束"""
        self.state = GameState.GAME_OVER
        self.running = False
        result = messagebox.askyesno("游戏结束", 
                                      f"你的得分: {self.score}\n\n是否再玩一局?")
        if result:
            self.restart()
        else:
            self.master.destroy()
    
    def restart(self):
        """重新开始"""
        self.player_x = 5
        self.player_y = float(self.height - 3)
        self.is_jumping = False
        self.jump_velocity = 0
        self.score = 0
        self.state = GameState.RUNNING
        self.platforms = []
        self.obstacles = []
        self.charging = False
        self.charge_power = 0
        self.trajectory_points = []
        self._init_platforms()
        self.running = True
        self.update()
    
    def update(self):
        """游戏主循环"""
        if self.running and self.state == GameState.RUNNING:
            # 更新蓄力
            if self.charging:
                self.charge_power += self.charge_rate
                if self.charge_power > self.max_charge_power:
                    self.charge_power = self.max_charge_power
                
                # 实时计算轨迹
                self._calculate_trajectory(self.charge_power)
            
            # 更新物理
            self._update_physics()
            
            # 检查碰撞
            self._check_collision()
            
            # 清理和生成新平台
            self._cleanup_platforms()
            
            # 绘制
            self._draw()
            
            # 继续循环（调大时间间隔，让整体运动更慢、更柔和）
            self.master.after(70, self.update)
    
    def run(self):
        """运行游戏"""
        print("跳一跳游戏加载中...")
        time.sleep(1)
        
        try:
            while self.state == GameState.RUNNING:
                self._draw()
                
                # 处理输入（简化版）
                print("\n按下 SPACE 跳跃 (输入后按Enter) 或输入 'q' 退出:")
                user_input = input().strip().lower()
                
                if user_input == 'q':
                    break
                elif user_input == ' ' or user_input == '':
                    self.jump()
                
                # 更新游戏状态
                self._update_physics()
                self._check_collision()
                self._cleanup_platforms()
                
                time.sleep(0.1)
            
            # 游戏结束
            self._clear_screen()
            print("\n" + "=" * 40)
            if self.state == GameState.GAME_OVER:
                print("❌ 游戏结束!")
            print(f"✨ 最终得分: {self.score}")
            print("=" * 40 + "\n")
        
        except KeyboardInterrupt:
            print("\n\n游戏已中断！")


def show_menu():
    """显示游戏菜单"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 显示欢迎对话框
    result = messagebox.showinfo("跳一跳游戏", "欢迎来到跳一跳游戏!\n\n按空格键跳跃，避开障碍物！")
    
    # 选择难度
    difficulty_window = tk.Toplevel(root)
    difficulty_window.title("选择难度")
    difficulty_window.geometry("300x250")
    difficulty_window.resizable(False, False)
    
    # 居中显示
    window_width = 300
    window_height = 250
    screen_width = difficulty_window.winfo_screenwidth()
    screen_height = difficulty_window.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    difficulty_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    selected_difficulty = tk.IntVar(value=1)
    
    tk.Label(difficulty_window, text="选择游戏难度", font=('Arial', 16, 'bold')).pack(pady=20)
    
    tk.Radiobutton(difficulty_window, text="简单 (推荐新手)", variable=selected_difficulty, 
                   value=1, font=('Arial', 12)).pack(pady=5)
    tk.Radiobutton(difficulty_window, text="中等", variable=selected_difficulty, 
                   value=2, font=('Arial', 12)).pack(pady=5)
    tk.Radiobutton(difficulty_window, text="困难", variable=selected_difficulty, 
                   value=3, font=('Arial', 12)).pack(pady=5)
    
    def start_game():
        difficulty = selected_difficulty.get()
        difficulty_window.destroy()
        root.destroy()
        
        # 创建游戏窗口
        game_window = tk.Tk()
        game_window.title(f"跳一跳游戏 - 难度: {difficulty}")
        game_window.resizable(False, False)
        
        # 居中显示游戏窗口
        game = JumpGame(game_window, width=40, height=12, difficulty=difficulty)
        game_window.update_idletasks()
        game_width = game_window.winfo_width()
        game_height = game_window.winfo_height()
        x = (screen_width - game_width) // 2
        y = (screen_height - game_height) // 2
        game_window.geometry(f"+{x}+{y}")
        
        game_window.mainloop()
    
    tk.Button(difficulty_window, text="开始游戏", command=start_game, 
              font=('Arial', 14, 'bold'), bg='#4CAF50', fg='white', 
              width=15, height=2).pack(pady=20)
    
    difficulty_window.mainloop()


def main():
    """主函数"""
    print("=" * 40)
    print("欢迎来到跳一跳游戏！")
    print("=" * 40)
    
    while True:
        print("\n请选择难度:")
        print("1. 简单 (推荐新手)")
        print("2. 中等")
        print("3. 困难")
        print("0. 退出")
        
        choice = input("\n请输入选择 (0-3): ").strip()
        
        if choice == '1':
            game = JumpGame(width=50, height=10, difficulty=1)
            game.run()
        elif choice == '2':
            game = JumpGame(width=50, height=10, difficulty=2)
            game.run()
        elif choice == '3':
            game = JumpGame(width=50, height=10, difficulty=3)
            game.run()
        elif choice == '0':
            print("感谢游玩！再见！👋\n")
            break
        else:
            print("无效选择，请重试！")


if __name__ == "__main__":
    show_menu()
