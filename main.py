import os
import sys
import pygame

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.taxi_sim import run_simulation

if __name__ == "__main__":
    pygame.init()
    run_simulation()
    pygame.quit()