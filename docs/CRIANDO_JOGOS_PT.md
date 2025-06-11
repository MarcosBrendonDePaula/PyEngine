# Guia Rápido: Criando um Jogo com a PyEngine

Este guia explica como iniciar um pequeno projeto usando a PyEngine. Considere que as dependências do `requirements.txt` já estejam instaladas.

## 1. Estrutura Básica

1. Importe `create_engine` e `BaseScene`:
   ```python
   from engine import create_engine
   from engine.core.scenes.base_scene import BaseScene
   ```
2. Crie uma cena derivando de `BaseScene` e adicione entidades com componentes.
3. Defina uma função `main()` para instanciar a engine, registrar a cena e iniciar o loop principal.

## 2. Exemplo Minimal

```python
import pygame
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.physics import Physics
from engine.core.components.collider import Collider

class Player(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.physics = self.add_component(Physics(mass=1.0))
        self.collider = self.add_component(Collider(40, 40))
        self.speed = 5.0

    def tick(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_d]: dx += self.speed
        if keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_s]: dy += self.speed
        self.physics.set_velocity(dx, dy)

class GameScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.player = Player(400, 300)
        self.add_entity(self.player, "players")


def main():
    engine = create_engine("Meu Jogo", 800, 600)
    engine.set_scene("game", GameScene())
    engine.run()

if __name__ == "__main__":
    main()
```

## 3. Próximos Passos

- Explore os componentes disponíveis em `engine.core.components` para adicionar colisões, partículas, luzes e UI.
- Utilize múltiplas cenas para organizar menus e fases do jogo.
- Consulte o `README.md` para exemplos mais complexos, como jogos de plataforma, puzzles e multiplayer.

