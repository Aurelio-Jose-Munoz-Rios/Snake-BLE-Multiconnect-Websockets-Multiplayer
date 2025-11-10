#include "Config.h"
#include "Point.h"
#include "BLEController.h"
#include "WebSocketManager.h"
#include "MusicPlayer.h"
#include "SnakeGame.h"

BLEController bleController;
WebSocketManager wsManager;
MusicPlayer musicPlayer(DAC_PIN);
SnakeGame game;

void setup() {
  Serial.begin(115200);
  randomSeed(analogRead(0));
  
  Serial.println("\n=== Snake 2 Jugadores ===");
  
  musicPlayer.begin();
  delay(500);
  musicPlayer.playIntro();
  
  bleController.begin();
  wsManager.begin();
  game.init();
  
  Serial.println("Sistema listo - 2 jugadores");
}

void loop() {
  wsManager.loop();
  
  if (!game.hasStarted() && !bleController.bothPlayersConnected()) {
    delay(100);
    return;
  }

  // Get commands from both players
  Direction cmd1 = bleController.getPlayer1Command();
  Direction cmd2 = bleController.getPlayer2Command();
  
  if (cmd1 != DIR_NONE) {
    if (!game.hasStarted()) {
      game.start();
      musicPlayer.playMove();
    }
    game.setPlayer1Direction(cmd1);
  }
  
  if (cmd2 != DIR_NONE) {
    if (!game.hasStarted()) {
      game.start();
      musicPlayer.playMove();
    }
    game.setPlayer2Direction(cmd2);
  }
  
  if (game.hasStarted() && !game.hasEnded()) {
    bool levelUp = false;
    bool p1Ate = false;
    bool p2Ate = false;
    
    game.update(levelUp, p1Ate, p2Ate);
    
    if (p1Ate || p2Ate) {
      musicPlayer.playEat();
    }
    
    if (levelUp) {
      musicPlayer.playLevelUp();
      Serial.printf("¡NIVEL %d!\n", game.getLevel());
    }
    
    wsManager.sendJSON(game.toJSON());
    
    if (game.hasEnded()) {
      musicPlayer.playCrash();
      delay(300);
      musicPlayer.playGameOver();
      
      String msg = "{\"type\":\"gameover\",\"totalScore\":" + String(game.getTotalScore()) + 
                   ",\"level\":" + String(game.getLevel()) + "}";
      wsManager.sendJSON(msg);
      
      Serial.printf("Game Over - Nivel: %d\n", game.getLevel());
      
      delay(3000);
      game.init();
      musicPlayer.playIntro();
    }
    
    delay(game.getSpeed());
  } else {
    delay(100);
  }
}
