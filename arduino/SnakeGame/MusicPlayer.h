#ifndef MUSIC_PLAYER_H
#define MUSIC_PLAYER_H

#include <driver/dac.h>
#include "Config.h"

class MusicPlayer {
private:
  dac_channel_t channel;
  bool playing;
  unsigned long lastTime;
  int phase;
  
  // Tabla de onda cuadrada para sonidos retro arcade
  const uint8_t squareWave[WAVE_SAMPLES] = {
    255, 255, 255, 255, 255, 255, 255, 255,
    255, 255, 255, 255, 255, 255, 255, 255,
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0
  };
  
  // Tabla de onda triangular para efectos suaves
  const uint8_t triangleWave[WAVE_SAMPLES] = {
    0, 16, 32, 48, 64, 80, 96, 112,
    128, 144, 160, 176, 192, 208, 224, 240,
    255, 240, 224, 208, 192, 176, 160, 144,
    128, 112, 96, 80, 64, 48, 32, 16
  };
  
  // Tabla de onda diente de sierra para bajos
  const uint8_t sawtoothWave[WAVE_SAMPLES] = {
    0, 8, 16, 24, 32, 40, 48, 56,
    64, 72, 80, 88, 96, 104, 112, 120,
    128, 136, 144, 152, 160, 168, 176, 184,
    192, 200, 208, 216, 224, 232, 240, 248
  };
  
  void playWave(const uint8_t* wave, int freq, int duration) {
    int samples = (SAMPLE_RATE * duration) / 1000;
    int period = SAMPLE_RATE / freq;
    
    for (int i = 0; i < samples; i++) {
      int index = (i * WAVE_SAMPLES / period) % WAVE_SAMPLES;
      dac_output_voltage(channel, wave[index]);
      delayMicroseconds(1000000 / SAMPLE_RATE);
    }
    dac_output_voltage(channel, 128); // Silencio (mitad del rango)
  }

public:
  MusicPlayer(int pin) : playing(false), lastTime(0), phase(0) {
    channel = (pin == 25) ? DAC_CHANNEL_1 : DAC_CHANNEL_2;
  }
  
  void begin() {
    dac_output_enable(channel);
    dac_output_voltage(channel, 128); // Nivel medio = silencio
    Serial.println("DAC Audio inicializado");
  }
  
  // Sonido de comer (burbuja arcade)
  void playEat() {
    for (int f = 400; f <= 800; f += 50) {
      playWave(triangleWave, f, 15);
    }
  }
  
  // Sonido de subir de nivel (fanfarria ascendente)
  void playLevelUp() {
    int notes[] = {262, 330, 392, 523, 659}; // C4, E4, G4, C5, E5
    for (int i = 0; i < 5; i++) {
      playWave(squareWave, notes[i], 80);
      delay(20);
    }
    playWave(squareWave, 784, 200); // G5 sostenido
  }
  
  // Sonido de game over (descendente trágico)
  void playGameOver() {
    int notes[] = {392, 370, 349, 330, 294, 262}; // G4 -> C4
    for (int i = 0; i < 6; i++) {
      playWave(sawtoothWave, notes[i], 150);
      delay(50);
    }
    // Efecto de explosión
    for (int i = 0; i < 30; i++) {
      playWave(squareWave, random(50, 200), 10);
    }
  }
  
  // Música de inicio (melodía corta arcade)
  void playIntro() {
    int melody[] = {523, 659, 784, 1047}; // C5, E5, G5, C6
    for (int i = 0; i < 4; i++) {
      playWave(squareWave, melody[i], 120);
      delay(30);
    }
  }
  
  // Efecto de movimiento (tick sutil)
  void playMove() {
    playWave(squareWave, 1000, 5);
  }
  
  // Efecto de colisión (crash)
  void playCrash() {
    for (int i = 0; i < 20; i++) {
      playWave(squareWave, random(100, 300), 8);
    }
  }
  
  // Sonido ambiente de nivel (opcional, llamar periódicamente)
  void playAmbient(int level) {
    if (millis() - lastTime < 3000) return; // Cada 3 segundos
    lastTime = millis();
    
    int baseFreq = 100 + (level * 20);
    playWave(sawtoothWave, baseFreq, 50);
  }
};

#endif
