import pygame
from config import WIDTH, HEIGHT, COLOR_BG
from benchmark.experiment_runner import ExperimentRunner

def run_benchmark_ui(screen, contexts):
    font, bold_font, title_font = pygame.font.SysFont("Arial", 15), pygame.font.SysFont("Arial", 15, bold=True), pygame.font.SysFont("Arial", 24, bold=True)
    runner, results, running = ExperimentRunner(), [], True
    btn_run_all, btn_back = pygame.Rect(50, 80, 160, 40), pygame.Rect(230, 80, 160, 40)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if btn_run_all.collidepoint(event.pos): results = runner.run_all(contexts)
                elif btn_back.collidepoint(event.pos): return
        screen.fill(COLOR_BG)
        screen.blit(title_font.render("ALGORITHM BENCHMARK DASHBOARD", True, (255,255,255)), (50, 30))
        pygame.draw.rect(screen, (46, 204, 113), btn_run_all, border_radius=5)
        rall_txt = bold_font.render("Run All Algorithms", True, (0,0,0))
        screen.blit(rall_txt, (btn_run_all.centerx - rall_txt.get_width()//2, btn_run_all.centery - rall_txt.get_height()//2))
        pygame.draw.rect(screen, (231, 76, 60), btn_back, border_radius=5)
        back_txt = bold_font.render("Back to Menu", True, (255,255,255))
        screen.blit(back_txt, (btn_back.centerx - back_txt.get_width()//2, btn_back.centery - back_txt.get_height()//2))
        y = 150
        col_x = [50, 250, 450, 550, 680]
        for i, h in enumerate(["Algorithm", "Group", "Success", "Time (ms)", "Metrics"]):
            screen.blit(bold_font.render(h, True, (241, 196, 15)), (col_x[i], y))
        y += 25
        pygame.draw.line(screen, (100, 100, 100), (50, y), (WIDTH-50, y), 2)
        y += 15
        for res in results:
            screen.blit(font.render(res.algorithm_name, True, (255,255,255)), (col_x[0], y))
            screen.blit(font.render(res.group_name, True, (200,200,200)), (col_x[1], y))
            screen.blit(font.render(str(res.success), True, (46, 204, 113) if res.success else (231, 76, 60)), (col_x[2], y))
            screen.blit(font.render(f"{res.execution_time_ms:.3f}", True, (52, 152, 219)), (col_x[3], y))
            screen.blit(font.render(" | ".join([f"{k}: {v}" for k,v in res.metrics.items()]), True, (180,180,180)), (col_x[4], y))
            y += 28
        pygame.display.flip()
