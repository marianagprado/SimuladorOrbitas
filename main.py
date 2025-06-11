import pygame
import math

# Janela
WIDTH, HEIGHT = 1000, 1000
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulador de Órbitas")

# Cores
WHITE = (255, 255, 255)
# Outras cores podem ser definidas aqui se necessário, ex: YELLOW, BLUE, GREY

# Fonte
pygame.font.init()
FONT = pygame.font.SysFont("comicsans", 12) # Você pode mudar para 16 para melhor leitura

class Planet:
    AU = 1.496e11  # Unidade Astronômica em metros
    G = 6.67428e-11 # Constante gravitacional
    SCALE = 250 / AU # Escala inicial: 250 pixels por AU
    TIMESTEP = 3600 # Passo de tempo da simulação (ex: 6 horas para órbitas lunares mais suaves)a

    def __init__(self, nome, x, y, raio_km, color, mass):
        self.nome = nome
        self.x = x # Posição X inicial (absoluta para Sol/planetas, relativa para luas no arquivo)
        self.y = y # Posição Y inicial
        self.radius = raio_km * 1000 # Raio do planeta em metros
        
        # display_radius pode ser usado para um tamanho mais fixo na tela se desejado
        # self.display_radius = max(4, raio_km / 1000) # Exemplo: raio em pixels = raio_km / 1000
        # Se usar display_radius fixo, ajuste o valor de raio_km no planetas.txt ou a fórmula aqui
        # Por ora, manteremos o raio_dinamico como no original para o corpo do planeta

        self.color = color
        self.mass = mass

        self.orbit = [] # Lista para armazenar pontos da trajetória
        self.sun = False # É o Sol?
        self.x_vel = 0 # Velocidade inicial em X
        self.y_vel = 0 # Velocidade inicial em Y

        self.peso_70kg = 0 # Para calcular peso na superfície (se aplicável)
        self.orbita_em_torno_de = None # Nome do corpo que este planeta orbita
        self.primary_body_obj = None  # Referência ao objeto do corpo primário (para luas)

    def draw(self, win, cx, cy, scale):
        # Posição atual do planeta na tela (para desenhar o corpo do planeta)
        current_planet_screen_x = (self.x * scale + cx)
        current_planet_screen_y = (self.y * scale + cy)

        # Desenhar a trilha da órbita
        if len(self.orbit) > 2:
            updated_trail_points = []
            
            is_orbit_relative = False
            # Ponto central na tela para desenhar a trilha da órbita
            # Por padrão, é o centro da câmera (cx, cy) para órbitas absolutas (ao redor do Sol)
            orbit_trail_center_screen_x = cx 
            orbit_trail_center_screen_y = cy

            # Verifica se este planeta é uma lua e tem um primário definido
            if self.primary_body_obj and self.orbita_em_torno_de == self.primary_body_obj.nome:
                is_orbit_relative = True
                # A órbita é relativa, então seu centro de desenho é a posição atual do primário na tela
                orbit_trail_center_screen_x = (self.primary_body_obj.x * scale + cx)
                orbit_trail_center_screen_y = (self.primary_body_obj.y * scale + cy)

            for point_data in self.orbit:
                # point_data são coordenadas (x,y) em unidades do MUNDO
                # Se is_orbit_relative = True, são relativas ao primário
                # Se is_orbit_relative = False, são absolutas
                p_world_x, p_world_y = point_data 

                if is_orbit_relative:
                    # p_world_x, p_world_y são relativos ao primário.
                    # Adicionamos à posição de tela ATUAL do primário após escalar.
                    # Aumentar apenas a órbita visual (não afeta a física)
                    fator_visual_orbita = 10 if self.orbita_em_torno_de and self.orbita_em_torno_de.lower() == "terra" else 1
                    screen_trail_point_x = orbit_trail_center_screen_x + p_world_x * scale * fator_visual_orbita
                    screen_trail_point_y = orbit_trail_center_screen_y + p_world_y * scale * fator_visual_orbita

                else:
                    # p_world_x, p_world_y são absolutos. 
                    # Convertemos para tela usando o offset global (cx,cy) e escala.
                    # orbit_trail_center_screen_x/y aqui são efetivamente cx, cy.
                    screen_trail_point_x = p_world_x * scale + orbit_trail_center_screen_x
                    screen_trail_point_y = p_world_y * scale + orbit_trail_center_screen_y
                
                updated_trail_points.append((screen_trail_point_x, screen_trail_point_y))
            
            # Desenha a trilha da órbita (usando cor BRANCA para o estilo da imagem de referência)
            pygame.draw.lines(win, WHITE, False, updated_trail_points, 1)

        # Desenhar o corpo do planeta em sua posição ATUAL
        velocidade_mag = math.sqrt(self.x_vel**2 + self.y_vel**2)
        # O raio dinâmico pode fazer os planetas pequenos demais. Considere usar um display_radius mais fixo.
        raio_dinamico = max(3, min(10, velocidade_mag * 1e-4)) # Ajustado o fator de velocidade
        if self.sun : raio_dinamico = 20 # Sol maior
        elif self.nome == "Terra": raio_dinamico = 10
        elif self.nome == "Lua": raio_dinamico = 7
        
        pygame.draw.circle(win, self.color, (int(current_planet_screen_x), int(current_planet_screen_y)), int(raio_dinamico))

        # Desenhar rótulos
        if not self.sun:
            label_text = f"{self.nome}" # Simplificado, pode adicionar peso ou outros dados
            # label_text = f"{self.nome}: {self.peso_70kg:.1f}N" 
            if self.orbita_em_torno_de and self.orbita_em_torno_de != "Nenhum":
                label_text += f" (órbita de {self.orbita_em_torno_de})"
            
            label = FONT.render(label_text, True, WHITE)
            # Posiciona o rótulo próximo ao planeta
            win.blit(label, (current_planet_screen_x + raio_dinamico + 5, current_planet_screen_y - FONT.get_height()//2))
        
        # Desenhar vetor de velocidade (opcional, pode ser grande demais visualmente)
        # if not self.sun:
        #     vx_screen = self.x_vel * scale * 0.01 # Ajuste o multiplicador para visualização
        #     vy_screen = self.y_vel * scale * 0.01
        #     pygame.draw.line(win, WHITE, 
        #                      (current_planet_screen_x, current_planet_screen_y), 
        #                      (current_planet_screen_x + vx_screen, current_planet_screen_y + vy_screen), 1)

    def attraction(self, other):
        distance_x = other.x - self.x
        distance_y = other.y - self.y
        distance = math.sqrt(distance_x**2 + distance_y**2)

        if distance == 0: # Evita divisão por zero se os planetas estiverem no mesmo lugar
            return 0, 0

        force = self.G * self.mass * other.mass / distance**2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, planets):
        total_fx = total_fy = 0
        if not self.sun: # Sol é fixo
            for other_planet in planets:
                if self == other_planet:
                    continue
                fx, fy = self.attraction(other_planet)
                total_fx += fx
                total_fy += fy

        # Atualiza velocidades
        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        # Atualiza posições
        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        
        # Armazenamento dos pontos da órbita
        if not self.sun:
            if self.primary_body_obj and self.orbita_em_torno_de == self.primary_body_obj.nome:
                # É uma lua, armazena a posição relativa ao seu primário.
                # (Importante: a ordem de atualização no loop principal deve ser Sol -> Primários -> Luas,
                # ou então primary_body_obj.x/y podem não ser os mais recentes deste timestep)
                # Assumindo que a ordem de 'planets' (Sol, Terra, Lua) garante isso.
                rel_x = self.x - self.primary_body_obj.x
                rel_y = self.y - self.primary_body_obj.y
                self.orbit.append((rel_x, rel_y))
            else:
                # É um planeta orbitando o Sol (ou sem primário definido)
                # Armazena a posição absoluta
                self.orbit.append((self.x, self.y))

def carregar_planetas(caminho_arquivo):
    planetas = []
    # dados_brutos agora armazena os objetos Planet e seus dados de carregamento originais
    # para referência no segundo loop (especialmente x_au, y_au para cálculo de velocidade relativa)
    dados_para_processamento_secundario = [] 

    with open(caminho_arquivo, 'r') as arquivo:
        for linha in arquivo:
            if linha.strip().startswith("#") or not linha.strip():
                continue
            partes = linha.split()
            nome = partes[0]
            x_au_rel = float(partes[1]) # Para luas, esta é a posição X relativa ao primário
            y_au_rel = float(partes[2]) # Para luas, esta é a posição Y relativa ao primário
            raio_km = float(partes[3])
            try: # Tratamento para cores
                cor_rgb_str = partes[4].split(",")
                if len(cor_rgb_str) == 3:
                    cor_rgb = tuple(map(int, cor_rgb_str))
                else:
                    cor_rgb = (255,255,255) # Cor padrão em caso de erro
            except:
                cor_rgb = (255,255,255) # Cor padrão

            massa = float(partes[5])
            # vel_y_kms agora é interpretada como a magnitude da velocidade orbital RELATIVA para luas
            # Para planetas orbitando o Sol, é a componente Y da velocidade orbital (com X_vel = 0)
            vel_orbital_kms = float(partes[6]) 
            orbita_em_torno_de_nome = partes[7] if len(partes) > 7 else "Nenhum"

            # Posição inicial em metros. Para Sol/planetas é absoluta. Para luas, será ajustada.
            x_m = x_au_rel * Planet.AU 
            y_m = y_au_rel * Planet.AU

            planeta = Planet(nome, x_m, y_m, raio_km, cor_rgb, massa)
            planeta.orbita_em_torno_de = orbita_em_torno_de_nome
            
            if nome.lower() == "sol":
                planeta.sun = True
            else: # Cálculo de gravidade superficial e peso_70kg
                if planeta.radius > 0: # Evitar divisão por zero
                    g_superficie = Planet.G * planeta.mass / (planeta.radius ** 2)
                    planeta.peso_70kg = 70 * g_superficie
                else:
                    planeta.peso_70kg = 0


            # Adiciona à lista principal de planetas
            planetas.append(planeta)
            # Adiciona aos dados para o segundo loop, incluindo o objeto planeta
            dados_para_processamento_secundario.append({
                'obj': planeta, 
                'x_au_rel': x_au_rel, # Relativo ao primário, ou absoluto se orbita Sol/Nenhum
                'y_au_rel': y_au_rel, 
                'vel_orbital_kms': vel_orbital_kms, 
                'orbita_nome': orbita_em_torno_de_nome
            })

    # Ajusta posição e velocidade relativas para luas (e define velocidade para planetas orbitando o Sol)
    for data in dados_para_processamento_secundario:
        planeta_atual = data['obj']
        orbita_nome = data['orbita_nome']

        if planeta_atual.sun: # Sol não tem velocidade orbital inicial definida desta forma
            continue

        if orbita_nome != "Nenhum" and orbita_nome.lower() != "sol": # É uma lua orbitando um planeta
            corpo_alvo_obj = next((p for p in planetas if p.nome == orbita_nome), None)
            if corpo_alvo_obj:
                planeta_atual.primary_body_obj = corpo_alvo_obj # Define o objeto primário

                # Posição absoluta da lua = posição absoluta do primário + posição relativa da lua (já em metros)
                planeta_atual.x = corpo_alvo_obj.x + planeta_atual.x # planeta_atual.x era x_au_rel * AU
                planeta_atual.y = corpo_alvo_obj.y + planeta_atual.y # planeta_atual.y era y_au_rel * AU
                
                # Cálculo da velocidade orbital inicial para luas
                # dx_rel_mundo, dy_rel_mundo são as coordenadas relativas INICIAIS da lua em relação ao primário, em metros
                dx_rel_mundo = data['x_au_rel'] * Planet.AU 
                dy_rel_mundo = data['y_au_rel'] * Planet.AU
                dist_rel_mundo = math.sqrt(dx_rel_mundo**2 + dy_rel_mundo**2)

                tx, ty = 0, 1 # Direção padrão (para cima) se dist_rel_mundo for 0
                if dist_rel_mundo != 0:
                    # Vetor tangencial (-dy, dx) para órbita anti-horária
                    tx = -dy_rel_mundo / dist_rel_mundo 
                    ty = dx_rel_mundo / dist_rel_mundo
                
                velocidade_orbital_relativa_m_s = data['vel_orbital_kms'] * 1000

                planeta_atual.x_vel = corpo_alvo_obj.x_vel + tx * velocidade_orbital_relativa_m_s
                planeta_atual.y_vel = corpo_alvo_obj.y_vel + ty * velocidade_orbital_relativa_m_s
            else: # Não encontrou o corpo alvo
                print(f"AVISO: Corpo alvo '{orbita_nome}' não encontrado para '{planeta_atual.nome}'.")
                # Define uma velocidade para evitar que fique parado, ou trate como erro
                planeta_atual.y_vel = data['vel_orbital_kms'] * 1000 


        elif orbita_nome.lower() == "sol": # Planeta orbitando o Sol
            # Assume que a posição X,Y no arquivo é a posição inicial absoluta
            # e vel_orbital_kms é a componente Y da velocidade (X_vel = 0 para órbita circular começando em (X,0))
            planeta_atual.x_vel = 0 
            planeta_atual.y_vel = data['vel_orbital_kms'] * 1000
            # Se a posição inicial for (0, Y), então X_vel seria -vel_orbital_kms e Y_vel = 0.
            # A configuração atual (X=1AU, Y=0, X_vel=0, Y_vel=vel) é comum para iniciar.

    return planetas

def main():
    run = True
    clock = pygame.time.Clock()

    planets = carregar_planetas("planetas.txt")

    # Inicializa a escala e o offset da câmera
    # Se houver planetas, centraliza no primeiro planeta não-Sol ou no Sol
    initial_focus_x, initial_focus_y = 0, 0
    if planets:
        non_sun_planets = [p for p in planets if not p.sun]
        if non_sun_planets:
            # Tenta focar na Terra se existir, senão no primeiro não-Sol
            earth = next((p for p in non_sun_planets if p.nome == "Terra"), None)
            if earth:
                initial_focus_x = earth.x
                initial_focus_y = earth.y
            else:
                initial_focus_x = non_sun_planets[0].x
                initial_focus_y = non_sun_planets[0].y
        else: # Só tem o Sol
            initial_focus_x = planets[0].x
            initial_focus_y = planets[0].y
            
    # Ajusta o offset para centralizar a visualização inicial
    # (cx, cy) é o ponto do mundo que estará no centro da tela (WIDTH/2, HEIGHT/2)
    # Então, cx_offset = WIDTH/2 - initial_focus_x_scaled
    # E scale = Planet.SCALE
    scale = Planet.SCALE 
    offset_x = WIDTH // 2 - initial_focus_x * scale
    offset_y = HEIGHT // 2 - initial_focus_y * scale
    
    dragging = False
    last_mouse_pos = (0, 0)

    while run:
        clock.tick(60) # Limita a 60 FPS
        WIN.fill((0, 0, 0)) # Fundo preto

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Botão esquerdo para arrastar
                    dragging = True
                    last_mouse_pos = pygame.mouse.get_pos()
                elif event.button == 4: # Scroll para cima (zoom in)
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    world_x_before_zoom = (mouse_x - offset_x) / scale
                    world_y_before_zoom = (mouse_y - offset_y) / scale
                    scale *= 1.1
                    offset_x = mouse_x - world_x_before_zoom * scale
                    offset_y = mouse_y - world_y_before_zoom * scale

                elif event.button == 5: # Scroll para baixo (zoom out)
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    world_x_before_zoom = (mouse_x - offset_x) / scale
                    world_y_before_zoom = (mouse_y - offset_y) / scale
                    scale /= 1.1
                    offset_x = mouse_x - world_x_before_zoom * scale
                    offset_y = mouse_y - world_y_before_zoom * scale

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: # Soltar botão esquerdo
                    dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    mouse_x, mouse_y = event.pos
                    dx = mouse_x - last_mouse_pos[0]
                    dy = mouse_y - last_mouse_pos[1]
                    offset_x += dx
                    offset_y += dy
                    last_mouse_pos = (mouse_x, mouse_y)

        # Atualiza a posição de todos os planetas
        for planet in planets:
            planet.update_position(planets)
        
        # Desenha todos os planetas
        for planet in planets:
            planet.draw(WIN, offset_x, offset_y, scale)

        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()