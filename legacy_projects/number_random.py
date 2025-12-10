import random


def guess_number_game():
    """随机数猜测游戏"""
    print("=" * 50)
    print("欢迎来到随机数猜测游戏！")
    print("=" * 50)
    
    # 生成 1-100 之间的随机数
    target_number = random.randint(1, 100)
    attempts = 0
    max_attempts = 10
    
    print(f"\n我想了一个 1-100 之间的数字，你有 {max_attempts} 次机会来猜测它。\n")
    
    while attempts < max_attempts:
        try:
            guess = int(input(f"请输入你的猜测（第 {attempts + 1}/{max_attempts} 次）: "))
            
            # 检查输入范围
            if guess < 1 or guess > 100:
                print("❌ 请输入 1-100 之间的数字！\n")
                continue
            
            attempts += 1
            
            # 比较猜测和目标数字
            if guess == target_number:
                print(f"\n🎉 恭喜你！你猜对了！答案是 {target_number}")
                print(f"✨ 你用了 {attempts} 次机会！\n")
                return True
            elif guess < target_number:
                remaining = max_attempts - attempts
                print(f"⬆️  你的猜测太小了！还剩 {remaining} 次机会\n")
            else:
                remaining = max_attempts - attempts
                print(f"⬇️  你的猜测太大了！还剩 {remaining} 次机会\n")
        
        except ValueError:
            print("❌ 请输入一个有效的数字！\n")
            continue
    
    # 如果用尽所有机会
    print(f"\n😢 很遗憾，你没有猜中。答案是 {target_number}")
    print(f"💡 正确答案是: {target_number}\n")
    return False


def play_again():
    """询问是否再玩一次"""
    while True:
        choice = input("是否想再玩一次？(y/n): ").lower()
        if choice == 'y':
            return True
        elif choice == 'n':
            return False
        else:
            print("请输入 'y' 或 'n'")


if __name__ == "__main__":
    while True:
        guess_number_game()
        if not play_again():
            print("感谢游玩！再见！👋\n")
            break
