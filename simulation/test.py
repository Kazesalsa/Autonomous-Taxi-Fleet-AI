import pygame
import sys
import math

WIDTH, HEIGHT = 1250, 900
FPS = 60

COLOR_BG = (30, 32, 36)
COLOR_ROAD = (50, 52, 58)
COLOR_ROAD_LINE = (180, 180, 180)
COLOR_NODE = (231, 76, 60)
COLOR_CAR = (241, 196, 15)

nodes_data = {
    'N1': (43, 200), 'N2': (111, 200), 'N3': (110, 322), 'N5': (363, 630), 'N6': (3, 630),
    'N7': (391, 313), 'N8': (391, 129), 'N9': (499, 127), 'N10': (499, 0), 'N12': (915, 322),
    'N13': (1122, 322), 'N14': (363, 322), 'N15': (110, 630), 'N16': (915, 630), 'N17': (46, 220),
    'N20': (1124, 299), 'N21': (91, 302), 'N22': (391, 629), 'N23': (392, 368), 'N24': (468, 0),
    'N25': (468, 110), 'N26': (917, 110), 'N27': (917, 2), 'N28': (363, 111), 'N29': (363, 298),
    'N31': (886, 3), 'N32': (888, 630), 'N33': (885, 651), 'N35': (3, 651), 'N36': (90, 651),
    'N37': (90, 777), 'N38': (220, 862), 'N39': (641, 862), 'N41': (1015, 862), 'N42': (1015, 658),
    'N43': (980, 631), 'N44': (884, 847), 'N45': (1247, 631), 'N46': (1140, 631), 'N47': (1109, 663),
    'N48': (1107, 758), 'N49': (1015, 760), 'N50': (1142, 650), 'N51': (1142, 752), 'N54': (1016, 781),
    'N55': (1119, 774), 'N56': (1074, 781), 'N57': (1247, 650), 'N58': (983, 652), 'N59': (983, 848),
    'N60': (641, 651), 'N61': (641, 847), 'N62': (917, 847), 'N63': (917, 651), 'N64': (113, 650),
    'N65': (888, 323), 'N66': (915, 297), 'N67': (915, 128), 'N68': (885, 110), 'N69': (91, 220),
    'N70': (111, 299), 'N71': (884, 299), 'N72': (608, 861), 'N73': (608, 653), 'N74': (640, 630),
    'N75': (113, 770), 'N76': (222, 847), 'N77': (607, 847), 'N78': (608, 740), 'N79': (608, 899),
    'N80': (640, 899), 'N81': (981, 899), 'N82': (1014, 897), 'N83': (228, 299), 'N84': (640, 541),
    'N85': (741, 541), 'N86': (739, 487), 'N87': (916, 487), 'N88': (887, 474), 'N89': (719, 474),
    'N90': (719, 529), 'N91': (607, 530)
}

edges_data = [
    ('N7', 'N8'), ('N8', 'N9'), ('N9', 'N10'), ('N3', 'N14'), ('N15', 'N6'), ('N5', 'N15'), 
    ('N22', 'N23'), ('N23', 'N7'), ('N24', 'N25'), ('N26', 'N27'), ('N14', 'N7'), ('N12', 'N13'), 
    ('N32', 'N33'), ('N35', 'N36'), ('N36', 'N37'), ('N37', 'N38'), ('N38', 'N39'), ('N39', 'N41'), 
    ('N42', 'N43'), ('N33', 'N44'), ('N45', 'N46'), ('N48', 'N49'), ('N49', 'N42'), ('N41', 'N54'), 
    ('N54', 'N49'), ('N54', 'N56'), ('N56', 'N55'), ('N55', 'N51'), ('N51', 'N50'), ('N50', 'N57'), 
    ('N47', 'N48'), ('N46', 'N47'), ('N46', 'N43'), ('N43', 'N16'), ('N58', 'N59'), ('N59', 'N44'), 
    ('N39', 'N61'), ('N44', 'N61'), ('N61', 'N60'), ('N60', 'N33'), ('N33', 'N63'), ('N59', 'N62'), 
    ('N62', 'N63'), ('N63', 'N58'), ('N58', 'N50'), ('N32', 'N63'), ('N16', 'N33'), ('N64', 'N15'), 
    ('N36', 'N64'), ('N66', 'N67'), ('N26', 'N67'), ('N9', 'N67'), ('N67', 'N26'), ('N14', 'N65'), 
    ('N65', 'N13'), ('N31', 'N68'), ('N28', 'N29'), ('N29', 'N14'), ('N15', 'N3'), ('N2', 'N1'), 
    ('N17', 'N69'), ('N69', 'N21'), ('N21', 'N36'), ('N25', 'N28'), ('N3', 'N70'), ('N70', 'N2'), 
    ('N20', 'N66'), ('N66', 'N71'), ('N71', 'N29'), ('N68', 'N71'), ('N68', 'N25'), ('N71', 'N12'), 
    ('N65', 'N12'), ('N64', 'N73'), ('N73', 'N60'), ('N60', 'N74'), ('N32', 'N74'), ('N74', 'N22'), 
    ('N22', 'N5'), ('N75', 'N64'), ('N76', 'N75'), ('N77', 'N72'), ('N61', 'N77'), ('N77', 'N76'), 
    ('N72', 'N79'), ('N80', 'N39'), ('N72', 'N61'), ('N73', 'N78'), ('N78', 'N77'), ('N39', 'N77'), 
    ('N59', 'N81'), ('N41', 'N82'), ('N74', 'N84'), ('N84', 'N85'), ('N85', 'N86'), ('N86', 'N87'), 
    ('N16', 'N87'), ('N87', 'N12'), ('N88', 'N89'), ('N89', 'N90'), ('N90', 'N91'), ('N91', 'N73'), 
    ('N65', 'N88'), ('N88', 'N32'), ('N7', 'N29'), ('N29', 'N83'), ('N83', 'N70')
]

class TestCar:
    def __init__(self, start_edge):
        self.u, self.v = start_edge
        self.x, self.y = nodes_data[self.u]
        self.speed = 3.0
        self.progress = 0.0

    def move(self):
        p1 = nodes_data[self.u]
        p2 = nodes_data[self.v]
        
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
            
            new_dist = math.hypot(p2[0] - self.x, p2[1] - self.y)
            if new_dist <= self.speed or math.hypot(self.x - p1[0], self.y - p1[1]) >= dist:
                self.u = self.v
                next_edges = [e for e in edges_data if e[0] == self.u]
                if next_edges:
                    self.v = pygame.compat.raw_choice(next_edges)[1] if hasattr(pygame, 'compat') else next_edges[int(pygame.time.get_ticks() % len(next_edges))][1]
                else:
                    self.u, self.v = edges_data[int(pygame.time.get_ticks() % len(edges_data))]
                self.x, self.y = nodes_data[self.u]

def run_test_tool():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tool Test Chuyển Động Đồ Thị 1 Chiều")
    clock = pygame.time.Clock()

    try:
        img = pygame.image.load("map.png").convert()
        img = pygame.transform.scale(img, (WIDTH, HEIGHT))
    except Exception:
        img = None

    cars = []
    for i in range(12):
        start_edge = edges_data[i % len(edges_data)]
        cars.append(TestCar(start_edge))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        for car in cars:
            car.move()

        screen.fill(COLOR_BG)
        if img:
            screen.blit(img, (0, 0))

        for u, v in edges_data:
            p1 = nodes_data[u]
            p2 = nodes_data[v]
            pygame.draw.line(screen, COLOR_ROAD, p1, p2, 20)
            pygame.draw.line(screen, COLOR_ROAD_LINE, p1, p2, 2)

        for node, pos in nodes_data.items():
            pygame.draw.circle(screen, COLOR_NODE, pos, 6)

        for car in cars:
            pygame.draw.circle(screen, COLOR_CAR, (int(car.x), int(car.y)), 8)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    run_test_tool()