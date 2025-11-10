# Snake Game con ESP32, BLE y WebSocket

Implementación del juego Snake con control BLE (Flutter), ejecución en ESP32 y renderizado en Pygame mediante WebSocket. Arquitectura modular (OOP) y concurrencia con FreeRTOS.

## Arquitectura

- Entrada: D‑Pad en Flutter 
- Lógica: ESP32 (C++), actualización discreta, serialización JSON.
- Transporte: WebSocket TCP a host local.
- Salida: Pygame (30 FPS).

Core 0: BLE + síntesis de audio.  
Core 1: WiFi/WebSocket + bucle de juego.

## Hardware

- ESP32 DevKit, buzzer pasivo (GPIO 25), smartphone, PC, WiFi 2.4 GHz.
## Diagrama de Bloques

<img width="2758" height="1054" alt="Tablero en blanco (5)" src="https://github.com/user-attachments/assets/cf73cff8-0deb-4c39-9f3d-a7f0dff9ee6a" />

## Diagama de Flujo

<img width="3886" height="2375" alt="Untitled diagram-2025-10-30-230145" src="https://github.com/user-attachments/assets/f8808f49-d7a5-4183-8efc-735ee2011731" />

[Diagrama mejor detalle](https://www.mermaidchart.com/app/projects/0542caf0-e896-42bc-b68c-5f48cefa6bfd/diagrams/23053415-8e8d-46c5-a64c-cd7e2fbb70e9/share/invite/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkb2N1bWVudElEIjoiMjMwNTM0MTUtOGU4ZC00NmM1LWE2NGMtY2Q3ZTJmYmI3MGU5IiwiYWNjZXNzIjoiRWRpdCIsImlhdCI6MTc2MTg2NTcyNH0.s-A2ioB3Efc04KntoUcELk56ARWmQcSbYS-Q3Sc9O7I)
## Dependencias

Arduino:
- Core ESP32, WebSockets.  
- Partición: Huge APP (3MB No OTA).

Flutter:
- flutter_blue_plus (≥1.14.0).  
- Permisos BLE/ubicación según plataforma.

Python:
- pygame (2.5.x), websockets (13.x).

## Configuración mínima

Config.h:
- WIFI_SSID, WIFI_PASSWORD, WS_HOST, WS_PORT, BUZZER_PIN.
- GAME_WIDTH, GAME_HEIGHT, GAME_SPEED.

snake_game.py:
- WIDTH, HEIGHT, CELL_SIZE coherentes con Config.h.

## Flujo

1. Flutter publica dirección (byte).  
2. ESP32 ajusta vector de movimiento; actualiza cuerpo y colisiones.  
3. Se emite estado JSON (serpiente, comida, score, flags).  
4. Pygame visualiza; música se gestiona en tarea dedicada.

## Música

Tres temas: intro (idle), in‑game (loop), game‑over (one‑shot). Reproducción no bloqueante.

## Rendimiento esperado

- Latencia extremo a extremo: 60–120 ms.  
- Visualización: 30 FPS estable.  
- Memoria: ~200 KB RAM; ~1.2 MB flash.


## Licencia

MIT.
