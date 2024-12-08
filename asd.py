import pygame
import fluidsynth

# Pygame ve FluidSynth başlat
pygame.init()
pygame.mixer.init()

# Ekran Ayarları
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DAW - SoundFont Desteği")

# Renkler
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# SoundFont Yükle
sf2_file = "example.sf2"  # SoundFont dosyanızın yolu
fs = fluidsynth.Synth()
fs.start(driver="dsound")  # Platforma özel sürücü ayarı
sfid = fs.sfload(sf2_file)
fs.program_select(0, sfid, 0, 0)

# Oynatma Çubuğu
playhead_x = 0
clock = pygame.time.Clock()

running = True
playing = False

while running:
    screen.fill(WHITE)

    # Olayları İşleme
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                playing = not playing
                if playing:
                    # Bir nota çal (Orta Do - C4)
                    fs.noteon(0, 60, 100)
                else:
                    fs.noteoff(0, 60)

    # Zaman Çizelgesini Çiz
    pygame.draw.rect(screen, BLACK, (0, HEIGHT // 2, WIDTH, 5))

    # Oynatma Çubuğu Çiz
    if playing:
        playhead_x += 2  # Oynatma hızı
        if playhead_x > WIDTH:
            playhead_x = 0
            playing = False

    pygame.draw.line(screen, RED, (playhead_x, 0), (playhead_x, HEIGHT), 2)

    # Ekranı Güncelle
    pygame.display.flip()
    clock.tick(60)

fs.delete()
pygame.quit()
