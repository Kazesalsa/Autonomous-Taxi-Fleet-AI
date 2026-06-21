import os
import sys
import pygame

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import WIDTH, HEIGHT, COLOR_BG
from ui.dashboard_benchmark import run_benchmark_ui
from benchmark.contexts_builder import get_benchmark_contexts

def main_menu():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AI Taxi Fleet Management - Master Control")
    title_font, btn_font = pygame.font.SysFont("Arial", 40, bold=True), pygame.font.SysFont("Arial", 22, bold=True)
    btn_sim = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 60, 300, 50)
    btn_bench = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 20, 300, 50)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if btn_sim.collidepoint(event.pos):
                    try:
                        from simulation.taxi_sim import run_simulation
                        run_simulation()
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))
                    except ImportError:
                        print("Simulation module not found.")
                elif btn_bench.collidepoint(event.pos):
                    run_benchmark_ui(screen, get_benchmark_contexts())
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))
        screen.fill(COLOR_BG)
        title = title_font.render("AI TAXI FLEET MANAGER", True, (255, 255, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3 - 50))
        pygame.draw.rect(screen, (52, 152, 219), btn_sim, border_radius=8)
        sim_txt = btn_font.render("1. Interactive Simulation Mode", True, (255, 255, 255))
        screen.blit(sim_txt, (btn_sim.centerx - sim_txt.get_width()//2, btn_sim.centery - sim_txt.get_height()//2))
        pygame.draw.rect(screen, (155, 89, 182), btn_bench, border_radius=8)
        bench_txt = btn_font.render("2. Algorithm Benchmark Mode", True, (255, 255, 255))
        screen.blit(bench_txt, (btn_bench.centerx - bench_txt.get_width()//2, btn_bench.centery - bench_txt.get_height()//2))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()
