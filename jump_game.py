import os
import time
import random
from enum import Enum


class GameState(Enum):
    """游戏状态枚举"""
    RUNNING = 1
    GAME_OVER = 2
    WIN = 3


class JumpGame:
    """跳一跳游戏类"""
    
    def __init__(self, width=50, height=10, difficulty=1):
        """初始化游戏
        
        Args:
            width: 游戏窗口宽度
            height: 游戏窗口高度
            difficulty: 难度等级（1-3）
        """
        self.width = width
        self.height = height
        self.difficulty = difficulty
        
        # 玩家位置和状态
        self.player_x = 2
        self.player_y = height - 3
        self.is_jumping = False
        self.jump_velocity = 0
        self.gravity = 0.5
        
        # 游戏对象列表
        self.platforms = []
        self.obstacles = []
        self.score = 0
        self.state = GameState.RUNNING
        
        # 游戏配置
        self.platform_spacing = 8 - difficulty  # 难度越高间距越小
        self.platform_width = max(3, 8 - difficulty)
        self.spawn_distance = 0
        
        # 初始化平台
        self._init_platforms()
    
    def _init_platforms(self):
        """初始化游戏平台"""
        x = 0
        while x < self.width * 3:
            platform_length = random.randint(self.platform_width, self.platform_width + 3)
            y = random.randint(self.height - 4, self.height - 2)
            self.platforms.append({
                'x': x,
                'y': y,
                'length': platform_length,
                'type': 'normal'
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
    
    def _clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _draw(self):
        """绘制游戏画面"""
        self._clear_screen()
        
        # 创建游戏画布
        canvas = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # 绘制平台
        for platform in self.platforms:
            if 0 <= platform['x'] < self.width:
                for i in range(platform['length']):
                    px = platform['x'] + i
                    if 0 <= px < self.width and 0 <= platform['y'] < self.height:
                        canvas[platform['y']][px] = '='
        
        # 绘制障碍物
        for obs in self.obstacles:
            if 0 <= obs['x'] < self.width:
                for i in range(obs['width']):
                    ox = obs['x'] + i
                    if 0 <= ox < self.width and 0 <= obs['y'] < self.height:
                        canvas[obs['y']][ox] = '#'
        
        # 绘制玩家（平滑化坐标）
        player_y = int(self.player_y)
        if 0 <= self.player_x < self.width and 0 <= player_y < self.height:
            canvas[player_y][self.player_x] = '●'
        
        # 打印画面
        print("╔" + "═" * self.width + "╗")
        for row in canvas:
            print("║" + "".join(row) + "║")
        print("╚" + "═" * self.width + "╝")
        
        # 打印游戏信息
        print(f"\n得分: {self.score} | 难度: {self.difficulty}")
        print("操作: 空格键跳跃 | Q键退出")
        print("-" * (self.width + 2))
    
    def _check_collision(self):
        """检查碰撞"""
        player_y = int(self.player_y)
        
        # 检查与平台的碰撞
        for platform in self.platforms:
            if (player_y == platform['y'] and 
                platform['x'] <= self.player_x < platform['x'] + platform['length'] and
                self.jump_velocity >= 0):
                self.is_jumping = False
                self.jump_velocity = 0
                self.score += 1
                return True
        
        # 检查与障碍物的碰撞
        for obs in self.obstacles:
            if (player_y == obs['y'] and 
                obs['x'] <= self.player_x < obs['x'] + obs['width']):
                self.state = GameState.GAME_OVER
                return False
        
        # 掉下去了
        if player_y >= self.height - 1:
            self.state = GameState.GAME_OVER
            return False
        
        return True
    
    def _update_physics(self):
        """更新物理"""
        if self.is_jumping:
            self.jump_velocity -= self.gravity
            self.player_y += self.jump_velocity
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
                self.jump_velocity = 0.5
                self.player_y += self.jump_velocity
    
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
    
    def jump(self):
        """跳跃"""
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_velocity = -8  # 根据难度调整
    
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
    main()
