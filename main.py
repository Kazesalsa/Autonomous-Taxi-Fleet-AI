import os
import sys
import ctypes
import pygame

if os.name == 'nt':
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulation.taxi_sim import run_simulation

if __name__ == "__main__":
    pygame.init()
    run_simulation()
    pygame.quit()