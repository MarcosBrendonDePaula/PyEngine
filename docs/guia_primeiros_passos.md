
# Guia de Uso da PyEngine: Primeiros Passos

## 2. Primeiros Passos: Criando um Jogo Simples

Vamos criar um jogo básico onde uma entidade se move na tela. Este exemplo cobrirá a inicialização da engine, a criação de uma cena e a adição de uma entidade com componentes de física e entrada.

### 2.1. Inicializando a Engine

Todo jogo PyEngine começa com a inicialização da classe `Interface`, que gerencia a janela do jogo, o loop principal e as cenas. O método `create_engine` é uma função de conveniência para configurar isso rapidamente.

```python
from engine import create_engine

def main():
    # Inicializa a engine com um título para a janela e dimensões (largura, altura)
    engine = create_engine("Meu Primeiro Jogo PyEngine", 800, 600)
    
    # ... (código para definir cenas e rodar o jogo)
    
    engine.run() # Inicia o loop principal do jogo

if __name__ == "__main__":
    main()
```

### 2.2. Criando uma Cena Básica

Cenas são os diferentes estados do seu jogo (menu principal, nível 1, tela de game over, etc.). Você deve criar uma classe que herde de `BaseScene` para cada cena do seu jogo.

```python
from engine.core.scenes.base_scene import BaseScene
import pygame # Importar pygame para usar pygame.font.Font e pygame.Surface

class GameScene(BaseScene):
    def __init__(self):
        super().__init__()
        print("GameScene inicializada!")

    def initialize(self):
        # Este método é chamado quando a cena é carregada pela engine.
        # É um bom lugar para carregar recursos e configurar entidades iniciais.
        print("GameScene: Método initialize chamado.")

    def tick(self, delta_time: float):
        # Este método é chamado a cada quadro para atualizar a lógica da cena.
        # delta_time é o tempo em segundos desde o último quadro, útil para movimentos baseados em tempo.
        super().tick(delta_time) # Chama o tick dos componentes da cena

    def render(self, screen: pygame.Surface):
        # Este método é chamado a cada quadro para desenhar a cena na tela.
        super().render(screen) # Chama o render dos componentes da cena
        # Exemplo: desenhar um texto simples
        font = pygame.font.Font(None, 74)
        text = font.render("Olá, PyEngine!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.interface.width // 2, self.interface.height // 2))
        screen.blit(text, text_rect)
```

Para que a engine use sua cena, você precisa adicioná-la ao `SceneManager` e defini-la como a cena atual:

```python
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
import pygame # Importar pygame para usar pygame.font.Font e pygame.Surface

# ... (definição da classe GameScene como acima)

def main():
    engine = create_engine("Meu Primeiro Jogo PyEngine", 800, 600)
    
    # Define a cena "game" como uma instância de GameScene
    engine.set_scene("game", GameScene())
    
    engine.run()

if __name__ == "__main__":
    main()
```

Ao executar este código, você verá uma janela Pygame com o título "Meu Primeiro Jogo PyEngine" e o texto "Olá, PyEngine!" centralizado.

### 2.3. Adicionando uma Entidade

Entidades são os objetos do seu jogo (personagens, inimigos, itens, etc.). Na PyEngine, uma `Entity` é um contêiner para `Component`s, que definem seu comportamento e aparência. Vamos criar uma entidade de jogador.

```python
from engine.core.entity import Entity
from engine.core.components.rectangle_renderer import RectangleRenderer

class Player(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y) # Define a posição inicial da entidade
        
        # Adiciona um componente de renderização para que a entidade seja visível
        # Este componente desenha um retângulo na posição da entidade
        self.add_component(RectangleRenderer(width=50, height=50, color=(255, 0, 0))) # Vermelho

# Atualize sua GameScene para adicionar o jogador:
class GameScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.player = None # Inicializa como None

    def initialize(self):
        print("GameScene: Método initialize chamado.")
        # Cria uma instância do Player e a adiciona à cena
        # O segundo argumento "players" é uma camada, útil para organização e renderização
        self.player = Player(x=400, y=300) # Posição central
        self.add_entity(self.player, "players")

    # ... (tick e render como antes)
```

Agora, ao executar, você verá um quadrado vermelho no centro da tela, representando seu jogador.

### 2.4. Movendo uma Entidade: `Physics` e `Input`

Para fazer o jogador se mover, vamos adicionar componentes de `Physics` (física) e `KeyboardController` (controle de teclado) à nossa entidade `Player`.

```python
import pygame
from engine.core.entity import Entity
from engine.core.components.physics import Physics
from engine.core.components.keyboard_controller import KeyboardController
from engine.core.components.rectangle_renderer import RectangleRenderer

class Player(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        
        self.add_component(RectangleRenderer(width=50, height=50, color=(255, 0, 0)))
        
        # Adiciona o componente de Física
        self.physics = self.add_component(Physics(mass=1.0, gravity=0.0, friction=0.1))
        
        # Adiciona o componente de Controle de Teclado
        # Mapeia as teclas WASD para o movimento
        self.controller = self.add_component(KeyboardController(
            up_key=pygame.K_w,
            down_key=pygame.K_s,
            left_key=pygame.K_a,
            right_key=pygame.K_d
        ))
        self.speed = 5.0 # Velocidade de movimento do jogador

    def tick(self):
        super().tick() # Chama o tick dos componentes anexados
        
        # Aplica velocidade baseada na entrada do teclado
        if self.controller.is_key_pressed("up"): 
            self.physics.velocity.y = -self.speed
        elif self.controller.is_key_pressed("down"): 
            self.physics.velocity.y = self.speed
        else:
            self.physics.velocity.y = 0 # Para o movimento vertical se nenhuma tecla for pressionada

        if self.controller.is_key_pressed("left"): 
            self.physics.velocity.x = -self.speed
        elif self.controller.is_key_pressed("right"): 
            self.physics.velocity.x = self.speed
        else:
            self.physics.velocity.x = 0 # Para o movimento horizontal

# A GameScene permanece a mesma, apenas a definição do Player mudou.
```

Agora, ao executar o jogo, você poderá mover o quadrado vermelho usando as teclas WASD. O componente `Physics` cuidará da atualização da posição da entidade com base na sua velocidade.


