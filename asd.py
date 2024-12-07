import pygame

# Pygame başlatma
pygame.init()

# Ana ekran yüzeyi oluştur
screen = pygame.display.set_mode((800, 600))

# Küçük surface oluştur (200x100)
small_surface = pygame.Surface((200, 100))
small_surface.fill((150, 150, 255))  # Küçük surface'i mavi renkle dolduralım

# Rect oluştur (50x50 boyutlarında)
rect = pygame.Rect(0, 0, 50, 50)  # Rect'i küçük surface'in sol üst köşesine yerleştiriyoruz

# Ana oyun döngüsü
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Ekranı temizle
    screen.fill((0, 0, 0))

    # Küçük surface'i ana ekrana yerleştir (ana ekranın ortasında)
    small_surface_rect = small_surface.get_rect(center=(400, 300))  # Ana ekranın ortasında
    screen.blit(small_surface, small_surface_rect)

    # Rect'i küçük surface üzerinde çiz
    pygame.draw.rect(small_surface, (255, 0, 0), rect)  # Rect'i kırmızı yapalım

    # Ekranı güncelle
    pygame.display.flip()

# Pygame'i kapatma
pygame.quit()
