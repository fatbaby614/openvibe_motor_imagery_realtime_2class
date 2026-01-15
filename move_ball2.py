import pygame
import sys
from pylsl import StreamInlet, resolve_streams

# ================= 配置 =================
STREAM_NAME = "BCI_Control_Signal"  # 必须和 OpenViBE 里的名字一模一样
SCREEN_W, SCREEN_H = 800, 600
BALL_RADIUS = 25
SPEED_SCALE = 4.0     # 速度敏感度：如果球动太慢，把这个改大 (比如 10.0)
SMOOTH_FACTOR = 0.1   # 平滑系数：0.05(极平滑/高延迟) ~ 0.5(灵敏/抖动)
# =======================================

def find_lsl_stream():
    """ 专门处理 Python 3.13 pylsl 兼容性的查找函数 """
    print(f"正在扫描局域网内的 LSL 流 (目标: {STREAM_NAME})...")
    
    # 获取所有流 (等待 1 秒)
    streams = resolve_streams(wait_time=1.0)
    
    for s in streams:
        if s.name() == STREAM_NAME:
            print(f">>> 成功连接到 OpenViBE 流: {s.name()} <<<")
            return StreamInlet(s)
            
    print(f"[错误] 未找到名为 '{STREAM_NAME}' 的流！")
    print("请检查：\n1. OpenViBE 是否点击了 Play？\n2. OpenViBE Python 盒子里的名字是否被改了？")
    sys.exit(1)

def main():
    # 1. 先连接 BCI
    inlet = find_lsl_stream()

    # 2. 初始化游戏
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("BCI Motor Imagery - Realtime Feedback")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 24)

    # 3. 变量初始化
    ball_x = SCREEN_W // 2
    ball_y = SCREEN_H // 2
    smooth_val = 0.0  # 用于平滑 LDA 的输出值

    running = True
    while running:
        # --- 事件处理 ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # --- BCI 数据读取 ---
        # timeout=0.0 非阻塞读取
        sample, timestamp = inlet.pull_sample(timeout=0.0)

        raw_val = 0.0
        if sample:
            raw_val = sample[0]
            
            # [算法] 指数移动平均 (EMA) 滤波
            smooth_val = (1 - SMOOTH_FACTOR) * smooth_val + (SMOOTH_FACTOR * raw_val)
            
            # [物理] 更新位置 (负值向左，正值向右)
            # 如果方向反了，把 += 改成 -=
            ball_x += smooth_val * SPEED_SCALE

        # --- 边界限制 ---
        if ball_x < BALL_RADIUS: ball_x = BALL_RADIUS
        if ball_x > SCREEN_W - BALL_RADIUS: ball_x = SCREEN_W - BALL_RADIUS

        # --- 渲染 ---
        screen.fill((30, 30, 30)) # 深灰背景
        
        # 画中心线
        pygame.draw.line(screen, (100, 100, 100), (SCREEN_W//2, 0), (SCREEN_W//2, SCREEN_H), 2)
        
        # 画球 (根据用力大小变色: 绿色->黄色)
        color_intensity = min(255, int(abs(smooth_val) * 100))
        ball_color = (color_intensity, 255 - color_intensity, 0)
        pygame.draw.circle(screen, (0, 255, 0), (int(ball_x), int(ball_y)), BALL_RADIUS)

        # 显示数值
        info_text = f"LDA Out: {raw_val:.3f} | Smooth: {smooth_val:.3f}"
        screen.blit(font.render(info_text, True, (255, 255, 255)), (10, 10))
        
        # 提示文字
        screen.blit(font.render("<- Left Hand", True, (0, 200, 255)), (50, SCREEN_H//2))
        screen.blit(font.render("Right Hand ->", True, (0, 200, 255)), (SCREEN_W - 200, SCREEN_H//2))

        pygame.display.flip()
        clock.tick(60) # 锁帧 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()