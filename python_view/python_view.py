import asyncio
import websockets
import pygame
import json

pygame.init()

WIDTH, HEIGHT = 1300, 720
GAME_WIDTH = 26
GAME_HEIGHT = 14
CELL_SIZE = 50

# Ajuste para el HUD: Las primeras 2 filas son zona prohibida
HUD_HEIGHT = 2  # 2 filas para el HUD
PLAY_AREA_START_Y = HUD_HEIGHT * CELL_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake 2 Jugadores - Corregido")
clock = pygame.time.Clock()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (40, 40, 40)

game_state = {"type": "waiting"}

def draw_game():
    screen.fill(BLACK)
    
    if game_state.get("type") == "waiting":
        font = pygame.font.Font(None, 74)
        text = font.render("Esperando jugadores...", True, WHITE)
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
        screen.blit(text, text_rect)
        
        hint = pygame.font.Font(None, 32).render("Conecta ambos celulares", True, (100, 100, 100))
        hint_rect = hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 52))
        screen.blit(hint, hint_rect)
    
    elif game_state.get("type") == "gameover":
        font = pygame.font.Font(None, 92)
        text = font.render("GAME OVER", True, RED)
        text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
        screen.blit(text, text_rect)
        
        score1 = game_state.get('score1', 0)
        score2 = game_state.get('score2', 0)
        level = game_state.get('level', 1)
        
        result_font = pygame.font.Font(None, 56)
        
        if score1 > score2:
            winner_text = result_font.render("¡Jugador 1 GANA!", True, GREEN)
        elif score2 > score1:
            winner_text = result_font.render("¡Jugador 2 GANA!", True, YELLOW)
        else:
            winner_text = result_font.render("¡EMPATE!", True, BLUE)
        
        winner_rect = winner_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
        screen.blit(winner_text, winner_rect)
        
        score_font = pygame.font.Font(None, 44)
        p1_text = score_font.render(f"Jugador 1: {score1}", True, GREEN)
        p2_text = score_font.render(f"Jugador 2: {score2}", True, YELLOW)
        level_text = score_font.render(f"Nivel: {level}", True, BLUE)
        
        screen.blit(p1_text, (WIDTH//2 - 200, HEIGHT//2 + 40))
        screen.blit(p2_text, (WIDTH//2 - 200, HEIGHT//2 + 85))
        screen.blit(level_text, (WIDTH//2 - 200, HEIGHT//2 + 130))
    
    elif game_state.get("type") == "game":
        # Obstáculos
        obstacles = game_state.get("obstacles", [])
        for (x, y) in obstacles:
            pygame.draw.rect(screen, GRAY, 
                           (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1))
            pygame.draw.rect(screen, WHITE, 
                           (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE-1, CELL_SIZE-1), 2)
        
        # Serpiente 1
        snake1 = game_state.get("snake1", [])
        alive1 = game_state.get("alive1", True)
        
        if alive1:
            for i, (x, y) in enumerate(snake1):
                color = GREEN if i == 0 else BLUE
                pygame.draw.rect(screen, color, 
                               (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE-2, CELL_SIZE-2))
                if i == 0:
                    eye_size = 6
                    pygame.draw.circle(screen, BLACK, 
                                     (x*CELL_SIZE + 16, y*CELL_SIZE + 16), eye_size)
                    pygame.draw.circle(screen, BLACK, 
                                     (x*CELL_SIZE + 34, y*CELL_SIZE + 16), eye_size)
        
        # Serpiente 2
        snake2 = game_state.get("snake2", [])
        alive2 = game_state.get("alive2", True)
        
        if alive2:
            for i, (x, y) in enumerate(snake2):
                color = YELLOW if i == 0 else (200, 200, 0)
                pygame.draw.rect(screen, color, 
                               (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE-2, CELL_SIZE-2))
                if i == 0:
                    eye_size = 6
                    pygame.draw.circle(screen, BLACK, 
                                     (x*CELL_SIZE + 16, y*CELL_SIZE + 16), eye_size)
                    pygame.draw.circle(screen, BLACK, 
                                     (x*CELL_SIZE + 34, y*CELL_SIZE + 16), eye_size)
        
        # Comida
        food = game_state.get("food", [0, 2])  # Y >= 2
        pygame.draw.circle(screen, RED, 
                          (food[0]*CELL_SIZE + CELL_SIZE//2, 
                           food[1]*CELL_SIZE + CELL_SIZE//2), 
                          CELL_SIZE//2 - 6)
        pygame.draw.circle(screen, (255, 150, 150), 
                          (food[0]*CELL_SIZE + CELL_SIZE//2, 
                           food[1]*CELL_SIZE + CELL_SIZE//2), 
                          CELL_SIZE//2 - 10, 2)
        
        # HUD en zona segura
        hud_bg = pygame.Surface((WIDTH, HUD_HEIGHT * CELL_SIZE))
        hud_bg.set_alpha(240)
        hud_bg.fill((20, 20, 20))
        screen.blit(hud_bg, (0, 0))
        
        font = pygame.font.Font(None, 42)
        score1 = game_state.get("score1", 0)
        score2 = game_state.get("score2", 0)
        level = game_state.get("level", 1)
        
        # Jugador 1
        p1_text = font.render(f"🟢 P1: {score1}", True, GREEN if alive1 else RED)
        screen.blit(p1_text, (20, 30))
        
        # Jugador 2
        p2_text = font.render(f"🟡 P2: {score2}", True, YELLOW if alive2 else RED)
        screen.blit(p2_text, (WIDTH//2 - 100, 30))
        
        # Nivel
        level_text = font.render(f"Nivel: {level}", True, BLUE)
        screen.blit(level_text, (WIDTH - 180, 30))
        
        # Línea divisoria
        pygame.draw.line(screen, DARK_GRAY, (0, PLAY_AREA_START_Y), 
                        (WIDTH, PLAY_AREA_START_Y), 3)
    
    pygame.display.flip()

async def handle_websocket(websocket):
    global game_state
    print("ESP32 conectado")
    
    try:
        async for message in websocket:
            game_state = json.loads(message)
    except Exception as e:
        print(f"Error: {e}")

async def game_loop():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
        
        draw_game()
        clock.tick(60)
        await asyncio.sleep(0.01)

async def main():
    async with websockets.serve(handle_websocket, "0.0.0.0", 8765):
        print("=" * 60)
        print("Snake 2 Jugadores - CORREGIDO")
        print("✓ Manzanas no aparecen en obstáculos")
        print("✓ Manzanas no aparecen en HUD")
        print("✓ Serpientes no pueden entrar al HUD")
        print("=" * 60)
        await game_loop()

if __name__ == "__main__":
    asyncio.run(main())
