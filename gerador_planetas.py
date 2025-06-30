import random
import math

# --- Constantes Físicas e de Simulação ---
G = 6.67430e-11  # Constante gravitacional
AU_EM_METROS = 1.496e11  # Unidade Astronômica em metros

# --- Parâmetros da Geração Aleatória (sinta-se à vontade para alterar) ---
NUMERO_MIN_PLANETAS = 4
NUMERO_MAX_PLANETAS = 8
CHANCE_DE_TER_LUAS = 0.6  # 60% de chance para um planeta ter luas
MAX_LUAS_POR_PLANETA = 3

# --- Funções Auxiliares ---

def gerar_cor_aleatoria():
    """Gera uma tupla de cor (R, G, B) e a formata como string."""
    r = random.randint(50, 255)
    g = random.randint(50, 255)
    b = random.randint(50, 255)
    return f"{r},{g},{b}"

def calcular_velocidade_orbital(massa_primario, distancia_em_metros):
    """
    Calcula a velocidade para uma órbita circular estável.
    Fórmula: v = sqrt(G * M / r)
    Retorna a velocidade em km/s.
    """
    if distancia_em_metros <= 0:
        return 0
    
    velocidade_m_s = math.sqrt((G * massa_primario) / distancia_em_metros)
    return velocidade_m_s / 1000  # Converte para km/s

def formatar_linha(nome, x_au, y_au, raio_km, cor, massa_kg, vel_kms, orbita_em_torno_de):
    """Formata os dados em uma string alinhada para o arquivo .txt."""
    return (f"{nome:<15}"
            f"{x_au:<11.4f}"
            f"{y_au:<9.2f}"
            f"{raio_km:<13.1f}"
            f"{cor:<15}"
            f"{massa_kg:<22.4e}"
            f"{vel_kms:<44.3f}"
            f"{orbita_em_torno_de}")

# --- Lógica Principal da Geração ---

def gerar_sistema_solar():
    """Função principal que gera e imprime os dados do sistema solar."""
    
    corpos_celestes = []
    nome_arquivo = "planetas2.txt"

    # 1. Gerar a Estrela Central (Sol)
    massa_sol = random.uniform(1.5e30, 2.5e30) # Massa um pouco variável
    raio_sol = random.uniform(600000, 800000)
    sol = {
        "nome": "Sol", "x_au": 0, "y_au": 0, "raio_km": raio_sol,
        "cor": "255,204,0", "massa_kg": massa_sol, "vel_kms": 0,
        "orbita_em_torno_de": "Nenhum"
    }
    corpos_celestes.append(sol)

    # 2. Gerar os Planetas
    num_planetas = random.randint(NUMERO_MIN_PLANETAS, NUMERO_MAX_PLANETAS)
    distancia_anterior_au = 0.4  # Distância inicial para o primeiro planeta

    for i in range(num_planetas):
        nome_planeta = f"Planeta-{i+1}"
        
        # Define a distância para evitar sobreposição
        distancia_au = distancia_anterior_au + random.uniform(0.5, 4.0)
        distancia_anterior_au = distancia_au
        
        # Gera propriedades do planeta
        raio_planeta = random.uniform(2000, 70000) # De pequenas Terras a gigantes gasosos
        massa_planeta = random.uniform(5e23, 5e27) # Ampla faixa de massas
        
        # Calcula velocidade orbital em torno do Sol
        distancia_m = distancia_au * AU_EM_METROS
        velocidade_planeta = calcular_velocidade_orbital(massa_sol, distancia_m)
        
        planeta = {
            "nome": nome_planeta, "x_au": distancia_au, "y_au": 0, "raio_km": raio_planeta,
            "cor": gerar_cor_aleatoria(), "massa_kg": massa_planeta, "vel_kms": velocidade_planeta,
            "orbita_em_torno_de": "Sol"
        }
        corpos_celestes.append(planeta)

        # 3. Gerar Luas para o Planeta Atual
        if random.random() < CHANCE_DE_TER_LUAS:
            num_luas = random.randint(1, MAX_LUAS_POR_PLANETA)
            dist_lua_anterior_km = 80000 # Distância inicial para a primeira lua
            
            for j in range(num_luas):
                # Distância da lua em relação ao planeta
                dist_lua_km = dist_lua_anterior_km + random.uniform(50000, 200000)
                dist_lua_anterior_km = dist_lua_km
                dist_lua_au = dist_lua_km / (AU_EM_METROS / 1000)

                # Gera propriedades da lua (menores que as do planeta)
                raio_lua = random.uniform(10, raio_planeta / 4)
                massa_lua = random.uniform(1e15, massa_planeta / 1000)
                
                # Calcula velocidade orbital em torno do planeta
                velocidade_lua = calcular_velocidade_orbital(massa_planeta, dist_lua_km * 1000)

                lua = {
                    "nome": f"Lua-{i+1}-{j+1}", "x_au": dist_lua_au, "y_au": 0, "raio_km": raio_lua,
                    "cor": gerar_cor_aleatoria(), "massa_kg": massa_lua, "vel_kms": velocidade_lua,
                    "orbita_em_torno_de": nome_planeta
                }
                corpos_celestes.append(lua)

    # 4. Salvar o resultado formatado em um arquivo
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write("# Nome         X(AU)      Y(AU)    Raio(km)     Cor(R,G,B)     Massa(kg)             Velocidade Orbital Inicial (km/s)    OrbitaEmTornoDe\n")
            for corpo in corpos_celestes:
                linha_formatada = formatar_linha(**corpo)
                f.write(linha_formatada + '\n')
        print(f"Sistema solar gerado com sucesso e salvo no arquivo '{nome_arquivo}'!")
    except IOError as e:
        print(f"Erro ao escrever no arquivo '{nome_arquivo}': {e}")


# --- Ponto de Entrada do Script ---
if __name__ == "__main__":
    gerar_sistema_solar()
