import pygame
import math

# Janela
WIDTH, HEIGHT = 1000, 1000
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador de Órbitas v1.0 - FINAL")

# Cores
WHITE = (255, 255, 255)

# Fonte
pygame.font.init()
FONT = pygame.font.SysFont("comicsans", 12)

class Planet:
    AU = 1.496e11
    G = 6.67428e-11
    SCALE = 120 / AU
    
    def __init__(self, nome, x, y, raio_km, color, mass):
        self.nome = nome
        self.x = x
        self.y = y
        self.radius = raio_km * 1000
        self.color = color
        self.mass = mass
        self.orbit = []
        self.sun = False
        self.x_vel = 0
        self.y_vel = 0
        self.orbita_em_torno_de = None
        self.primary_body_obj = None
        self.semi_major_axis = 0

    def draw(self, win, cx, cy, scale):
        fator_visual = 1.0

        if self.primary_body_obj and not self.primary_body_obj.sun:
            RAIO_ORBITA_VISUAL_DESEJADO = 15
            distancia_real_m = self.semi_major_axis
            distancia_projetada_px = distancia_real_m * scale
            if distancia_projetada_px > 0:
                fator_visual = RAIO_ORBITA_VISUAL_DESEJADO / distancia_projetada_px
        
        if len(self.orbit) > 2:
            updated_trail_points = []
            if self.primary_body_obj and not self.primary_body_obj.sun:
                centro_x = self.primary_body_obj.x * scale + cx
                centro_y = self.primary_body_obj.y * scale + cy
                for p_world_x, p_world_y in self.orbit:
                    screen_x = centro_x + p_world_x * scale * fator_visual
                    screen_y = centro_y + p_world_y * scale * fator_visual
                    updated_trail_points.append((screen_x, screen_y))
            else:
                for p_world_x, p_world_y in self.orbit:
                    screen_x = p_world_x * scale + cx
                    screen_y = p_world_y * scale + cy
                    updated_trail_points.append((screen_x, screen_y))
            pygame.draw.lines(win, WHITE, False, updated_trail_points, 1)

        if self.primary_body_obj and not self.primary_body_obj.sun:
            real_relative_x = self.x - self.primary_body_obj.x
            real_relative_y = self.y - self.primary_body_obj.y
            fake_absolute_x = self.primary_body_obj.x + (real_relative_x * fator_visual)
            fake_absolute_y = self.primary_body_obj.y + (real_relative_y * fator_visual)
            current_planet_screen_x = fake_absolute_x * scale + cx
            current_planet_screen_y = fake_absolute_y * scale + cy
        else:
            current_planet_screen_x = self.x * scale + cx
            current_planet_screen_y = self.y * scale + cy

        if self.sun:
            raio_dinamico = 15
        else:
            raio_dinamico = max(1, math.log(self.radius) - 8)

        pygame.draw.circle(win, self.color, (int(current_planet_screen_x), int(current_planet_screen_y)), int(raio_dinamico))

        if not self.sun:
            label_text = f"{self.nome}"
            label = FONT.render(label_text, True, WHITE)
            win.blit(label, (current_planet_screen_x + raio_dinamico + 5, current_planet_screen_y - FONT.get_height() // 2))

    def attraction(self, other):
        distance_x = other.x - self.x
        distance_y = other.y - self.y
        distance = math.sqrt(distance_x**2 + distance_y**2)
        if distance == 0: return 0, 0
        force = self.G * self.mass * other.mass / distance**2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, planets, timestep):
        total_fx = total_fy = 0
        if not self.sun:
            for other_planet in planets:
                if self == other_planet: continue
                fx, fy = self.attraction(other_planet)
                total_fx += fx
                total_fy += fy

        self.x_vel += total_fx / self.mass * timestep
        self.y_vel += total_fy / self.mass * timestep
        self.x += self.x_vel * timestep
        self.y += self.y_vel * timestep
        
        if not self.sun:
            if self.primary_body_obj:
                rel_x = self.x - self.primary_body_obj.x
                rel_y = self.y - self.primary_body_obj.y
                self.orbit.append((rel_x, rel_y))
            else:
                self.orbit.append((self.x, self.y))

        # Limita o tamanho da trilha para não sobrecarregar a memória
        if len(self.orbit) > 20000:
            self.orbit = self.orbit[-20000:]


def carregar_planetas(caminho_arquivo):
    planetas_dict = {}
    planetas_dados_brutos = []
    try:
        with open(caminho_arquivo, 'r') as arquivo:
            for i, linha in enumerate(arquivo):
                if linha.strip().startswith("#") or not linha.strip(): continue
                partes = linha.split()
                if len(partes) < 8: continue
                nome, x_au, y_au, raio_km, cor_str, massa_str, vel_kms, orbita_nome = [p.strip() for p in partes]
                planeta = Planet(nome, float(x_au) * Planet.AU, float(y_au) * Planet.AU, float(raio_km), tuple(map(int, cor_str.split(','))), float(massa_str))
                planeta.orbita_em_torno_de = orbita_nome
                if nome.lower() == "sol": planeta.sun = True
                planetas_dict[nome] = planeta
                planetas_dados_brutos.append({'nome': nome, 'orbita_nome': orbita_nome, 'vel_kms': float(vel_kms), 'x_au': float(x_au), 'y_au': float(y_au)})
    except FileNotFoundError: return []
    for dados in sorted(planetas_dados_brutos, key=lambda p: p['orbita_nome'].lower() != 'sol'):
        planeta_atual = planetas_dict[dados['nome']]
        orbita_nome = dados['orbita_nome']
        if orbita_nome.lower() == "sol":
            planeta_atual.y_vel = dados['vel_kms'] * 1000
        elif orbita_nome != "Nenhum":
            primario = planetas_dict.get(orbita_nome)
            if primario:
                planeta_atual.primary_body_obj = primario
                planeta_atual.x = primario.x + planeta_atual.x
                planeta_atual.y = primario.y + planeta_atual.y
                distancia_relativa_m = math.sqrt((dados['x_au'] * Planet.AU)**2 + (dados['y_au'] * Planet.AU)**2)
                planeta_atual.semi_major_axis = distancia_relativa_m
                tangente_x = -(dados['y_au'] * Planet.AU) / distancia_relativa_m if distancia_relativa_m != 0 else 0
                tangente_y = (dados['x_au'] * Planet.AU) / distancia_relativa_m if distancia_relativa_m != 0 else 1
                vel_relativa_m_s = dados['vel_kms'] * 1000
                planeta_atual.x_vel = primario.x_vel + (tangente_x * vel_relativa_m_s)
                planeta_atual.y_vel = primario.y_vel + (tangente_y * vel_relativa_m_s)
    return list(planetas_dict.values())

def main():
    run = True
    clock = pygame.time.Clock()
    planets = carregar_planetas("Trabalho/planetas_certo.txt")
    
    scale = Planet.SCALE
    offset_x, offset_y = WIDTH // 2, HEIGHT // 2
    dragging = False
    last_mouse_pos = (0, 0)
    
    TIMESTEP_FISICA_SEGUNDOS = 150
    HORAS_A_SIMULAR_POR_QUADRO = 2.0
    SEGUNDOS_POR_HORA = 3600
    sub_passos_por_quadro = int((HORAS_A_SIMULAR_POR_QUADRO * SEGUNDOS_POR_HORA) / TIMESTEP_FISICA_SEGUNDOS)
    if sub_passos_por_quadro == 0: sub_passos_por_quadro = 1
    
    while run:
        clock.tick(60)
        WIN.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: dragging, last_mouse_pos = True, event.pos
                elif event.button == 4: scale *= 1.1
                elif event.button == 5: scale /= 1.1
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    mouse_x, mouse_y = event.pos
                    dx, dy = mouse_x - last_mouse_pos[0], mouse_y - last_mouse_pos[1]
                    offset_x, offset_y = offset_x + dx, offset_y + dy
                    last_mouse_pos = event.pos
        
        for _ in range(sub_passos_por_quadro):
            for planet in planets:
                planet.update_position(planets, TIMESTEP_FISICA_SEGUNDOS)
        
        planetas_principais = [p for p in planets if not p.primary_body_obj or p.primary_body_obj.sun]
        luas = [p for p in planets if p.primary_body_obj and not p.primary_body_obj.sun]
        
        for corpo in planetas_principais:
            corpo.draw(WIN, offset_x, offset_y, scale)
        for corpo in luas:
            corpo.draw(WIN, offset_x, offset_y, scale)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()