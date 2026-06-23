t = btn_font.render("1. Interactive Simulation Mode", True, (255, 255, 255))
        screen.blit(sim_txt, (btn_sim.centerx - sim_txt.get_width()//2, btn_sim.centery - sim_txt.get_height()//2))
        pygame.draw.rect(screen, (155, 89, 182), btn_bench, border_radius=8)
        bench_txt = btn_font.render("2. Algorithm Benchmark Mode", True, (255, 255, 255))
        screen.blit(bench_txt, (btn_bench.centerx - bench_txt.get_width()//2, btn_bench.centery - bench_txt.get_height()//2))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_menu()
