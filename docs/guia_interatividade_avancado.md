
# Guia de Uso da PyEngine: Interatividade e Recursos Avançados

## 3. Adicionando Interatividade: Colisões e UI

Vamos aprimorar nosso jogo adicionando detecção de colisões e elementos de interface de usuário.

### 3.1. Configurando Colisores

Para que as entidades interajam fisicamente, elas precisam de um componente `Collider`. A PyEngine oferece vários tipos de colisores. Vamos adicionar um `RectCollider` ao nosso jogador e criar uma parede com a qual ele possa colidir.

```python
from engine.core.components.collider import RectCollider
from engine.core.entity import Entity
from engine.core.components.physics import Physics
from engine.core.components.keyboard_controller import KeyboardController
from engine.core.components.rectangle_renderer import RectangleRenderer
import pygame

class Player(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.add_component(RectangleRenderer(width=50, height=50, color=(255, 0, 0)))
        self.physics = self.add_component(Physics(mass=1.0, gravity=0.0, friction=0.1))
        self.controller = self.add_component(KeyboardController(
            up_key=pygame.K_w, down_key=pygame.K_s, left_key=pygame.K_a, right_key=pygame.K_d
        ))
        self.speed = 5.0
        
        # Adiciona um colisor retangular ao jogador
        self.collider = self.add_component(RectCollider(width=50, height=50))

    def tick(self):
        super().tick()
        # ... (código de movimento como antes)

class Wall(Entity):
    def __init__(self, x: float, y: float, width: float, height: float):
        super().__init__(x, y)
        self.add_component(RectangleRenderer(width=width, height=height, color=(0, 0, 255))) # Azul
        
        # Adiciona um componente de física estático para a parede (não se move, mas colide)
        self.physics = self.add_component(Physics())
        self.physics.set_static(True)
        
        # Adiciona um colisor retangular à parede
        self.collider = self.add_component(RectCollider(width=width, height=height))

# Atualize sua GameScene para adicionar a parede:
from engine.core.scenes.base_scene import BaseScene

class GameScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.player = None
        self.wall = None

    def initialize(self):
        print("GameScene: Método initialize chamado.")
        self.player = Player(x=100, y=300) # Posição inicial do jogador
        self.add_entity(self.player, "players")
        
        self.wall = Wall(x=400, y=300, width=20, height=200) # Parede no centro
        self.add_entity(self.wall, "walls")

    def tick(self, delta_time: float):
        super().tick(delta_time)
        # A engine automaticamente processa colisões entre entidades com componentes Collider e Physics.
        # A resposta à colisão (como o "empurrão" ou "quique") é gerenciada pelo Physics Component.

    def render(self, screen: pygame.Surface):
        super().render(screen)
        # Exemplo: desenhar um texto simples
        font = pygame.font.Font(None, 74)
        text = font.render("Olá, PyEngine!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.interface.width // 2, self.interface.height // 2))
        screen.blit(text, text_rect)
```

Agora, quando você mover o jogador vermelho em direção à parede azul, ele colidirá e não conseguirá atravessá-la, demonstrando a detecção e resposta à colisão.

### 3.2. Criando Elementos de UI: `Label` e `Button`

A PyEngine possui um sistema de UI robusto. Vamos adicionar um `Label` para exibir uma mensagem e um `Button` para interagir.

```python
from engine.core.components.ui.label import Label
from engine.core.components.ui.button import Button
import pygame

# ... (definição de Player e Wall como antes)

class GameScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.player = None
        self.wall = None
        self.message_label = None
        self.action_button = None

    def initialize(self):
        print("GameScene: Método initialize chamado.")
        self.player = Player(x=100, y=300)
        self.add_entity(self.player, "players")
        
        self.wall = Wall(x=400, y=300, width=20, height=200)
        self.add_entity(self.wall, "walls")
        
        # Cria um Label para exibir mensagens
        self.message_label = Entity(x=self.interface.width // 2, y=50) # Topo central
        self.message_label.add_component(Label("Mova o jogador!", font_size=30, color=(255, 255, 0)))
        self.add_entity(self.message_label, "ui")
        
        # Cria um Botão
        self.action_button = Entity(x=self.interface.width // 2, y=self.interface.height - 100) # Parte inferior central
        button_component = Button("Clique-me!", width=150, height=50, font_size=24, 
                                  bg_color=(0, 150, 0), hover_color=(0, 200, 0), click_color=(0, 100, 0))
        self.action_button.add_component(button_component)
        self.add_entity(self.action_button, "ui")
        
        # Adiciona um callback para o botão
        button_component.on_click = self.on_button_click

    def on_button_click(self):
        # Este método será chamado quando o botão for clicado
        print("Botão clicado!")
        label_comp = self.message_label.get_component(Label)
        if label_comp:
            label_comp.set_text("Botão clicado com sucesso!")

    def tick(self, delta_time: float):
        super().tick(delta_time)
        # A engine automaticamente processa colisões entre entidades com componentes Collider e Physics.
        # A resposta à colisão (como o "empurrão" ou "quique") é gerenciada pelo Physics Component.

    def render(self, screen: pygame.Surface):
        super().render(screen)
        # Exemplo: desenhar um texto simples
        font = pygame.font.Font(None, 74)
        text = font.render("Olá, PyEngine!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.interface.width // 2, self.interface.height // 2))
        screen.blit(text, text_rect)
```

Ao executar, você verá o texto "Mova o jogador!" no topo e um botão "Clique-me!" na parte inferior. Clicar no botão mudará o texto do label, demonstrando a interatividade da UI.

## 4. Recursos Avançados: Iluminação e Multiplayer

Agora que você tem uma base sólida, vamos explorar algumas das funcionalidades mais avançadas da PyEngine.

### 4.1. Implementando Iluminação Dinâmica

O sistema de iluminação da PyEngine permite criar ambientes visuais ricos com luzes dinâmicas e sombras. Vamos adicionar uma luz ao nosso jogador e uma luz ambiente à cena.

```python
from engine.core.components.light_component import LightComponent

# ... (definição de Player, Wall, GameScene, etc. como antes)

class Player(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.add_component(RectangleRenderer(width=50, height=50, color=(255, 0, 0)))
        self.physics = self.add_component(Physics(mass=1.0, gravity=0.0, friction=0.1))
        self.controller = self.add_component(KeyboardController(
            up_key=pygame.K_w, down_key=pygame.K_s, left_key=pygame.K_a, right_key=pygame.K_d
        ))
        self.speed = 5.0
        self.collider = self.add_component(RectCollider(width=50, height=50))
        
        # Adiciona um componente de luz ao jogador
        self.light = self.add_component(LightComponent(
            color=(255, 255, 150),  # Cor da luz (amarelada)
            intensity=1.0,          # Intensidade da luz
            radius=150              # Raio de alcance da luz
        ))

# Atualize sua GameScene para adicionar uma luz ambiente:
class GameScene(BaseScene):
    def __init__(self):
        super().__init__()
        self.player = None
        self.wall = None
        self.message_label = None
        self.action_button = None

    def initialize(self):
        print("GameScene: Método initialize chamado.")
        self.player = Player(x=100, y=300)
        self.add_entity(self.player, "players")
        
        self.wall = Wall(x=400, y=300, width=20, height=200)
        self.add_entity(self.wall, "walls")
        
        self.message_label = Entity(x=self.interface.width // 2, y=50)
        self.message_label.add_component(Label("Mova o jogador!", font_size=30, color=(255, 255, 0)))
        self.add_entity(self.message_label, "ui")
        
        self.action_button = Entity(x=self.interface.width // 2, y=self.interface.height - 100)
        button_component = Button("Clique-me!", width=150, height=50, font_size=24, 
                                  bg_color=(0, 150, 0), hover_color=(0, 200, 0), click_color=(0, 100, 0))
        self.action_button.add_component(button_component)
        self.add_entity(self.action_button, "ui")
        button_component.on_click = self.on_button_click
        
        # Adiciona uma luz ambiente à cena
        ambient_light_entity = Entity(x=self.interface.width // 2, y=self.interface.height // 2)
        ambient_light_entity.add_component(LightComponent(
            color=(50, 50, 100),  # Cor azulada escura
            intensity=0.3,        # Intensidade baixa
            radius=self.interface.width * 2 # Grande raio para cobrir a tela
        ))
        self.add_entity(ambient_light_entity, "lights") # Adicione a luz em uma camada "lights"

    # ... (tick e render como antes)
```

Ao executar, você notará que a tela estará mais escura, e o jogador emitirá uma luz amarelada que ilumina a área ao seu redor. A parede azul também será afetada pela luz, e você poderá ver sombras sutis se o sistema de iluminação estiver configurado para isso.

### 4.2. Configurando um Jogo Multiplayer Básico

A PyEngine oferece suporte a multiplayer leve para sincronização de entidades. Este é um tópico mais avançado, mas vamos demonstrar como configurar um cliente e um servidor básicos para sincronizar a posição de uma entidade.

Para este exemplo, você precisará de dois scripts Python separados: um para o servidor e outro para o cliente. Você pode executar o servidor em uma janela de terminal e o cliente em outra (ou em máquinas diferentes na mesma rede).

**`server.py` (Servidor Dedicado):**

```python
from engine.multiplayer.server import DedicatedServer

def main():
    server = DedicatedServer(host="127.0.0.1", port=6000) # Escuta na porta 6000
    print(f"Servidor iniciado em {server.host}:{server.port}")
    server.run() # Inicia o loop do servidor

if __name__ == "__main__":
    main()
```

**`client.py` (Cliente com Entidade Sincronizada):**

```python
import pygame
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.physics import Physics
from engine.core.components.keyboard_controller import KeyboardController
from engine.core.components.rectangle_renderer import RectangleRenderer
from engine.multiplayer.client import Client
from engine.multiplayer.sync_component import SyncComponent

class NetworkPlayer(Entity):
    def __init__(self, x: float, y: float, is_local: bool = True):
        super().__init__(x, y)
        self.add_component(RectangleRenderer(width=50, height=50, color=(0, 255, 0) if is_local else (0, 0, 255))) # Verde para local, Azul para remoto
        self.physics = self.add_component(Physics(mass=1.0, gravity=0.0, friction=0.1))
        
        if is_local:
            self.controller = self.add_component(KeyboardController(
                up_key=pygame.K_UP, down_key=pygame.K_DOWN, left_key=pygame.K_LEFT, right_key=pygame.K_RIGHT
            ))
            self.speed = 5.0
        
        # Adiciona o SyncComponent para sincronizar a posição
        # tracked_attrs define quais atributos serão sincronizados
        self.sync_comp = self.add_component(SyncComponent(tracked_attrs=["position.x", "position.y"]))

    def tick(self):
        super().tick()
        if hasattr(self, "controller") and self.controller:
            # Lógica de movimento para o jogador local
            if self.controller.is_key_pressed("up"): 
                self.physics.velocity.y = -self.speed
            elif self.controller.is_key_pressed("down"): 
                self.physics.velocity.y = self.speed
            else:
                self.physics.velocity.y = 0

            if self.controller.is_key_pressed("left"): 
                self.physics.velocity.x = -self.speed
            elif self.controller.is_key_pressed("right"): 
                self.physics.velocity.x = self.speed
            else:
                self.physics.velocity.x = 0

class NetworkScene(BaseScene):
    def __init__(self, client: Client):
        super().__init__()
        self.client = client
        self.local_player = None
        self.remote_players = {}

    def initialize(self):
        print("NetworkScene: Método initialize chamado.")
        
        # Cria o jogador local
        self.local_player = NetworkPlayer(x=200, y=300, is_local=True)
        self.add_entity(self.local_player, "players")
        
        # Conecta o cliente ao servidor
        self.client.connect()
        
        # Registra um callback para quando uma entidade remota for criada/atualizada
        self.client.on_entity_sync = self.handle_remote_entity_sync

    def handle_remote_entity_sync(self, entity_id: str, data: dict):
        # Se a entidade remota ainda não existe, cria-a
        if entity_id not in self.remote_players:
            remote_player = NetworkPlayer(x=data["position.x"], y=data["position.y"], is_local=False)
            self.add_entity(remote_player, "players")
            self.remote_players[entity_id] = remote_player
        else:
            # Atualiza a posição da entidade remota
            remote_player = self.remote_players[entity_id]
            remote_player.position.x = data["position.x"]
            remote_player.position.y = data["position.y"]

    def tick(self, delta_time: float):
        super().tick(delta_time)
        self.client.tick() # Processa a comunicação de rede

    def render(self, screen: pygame.Surface):
        super().render(screen)
        # O RectangleRenderer dos jogadores já cuida do desenho

def main():
    client = Client(host="127.0.0.1", port=6000) # Conecta ao servidor local
    engine = create_engine("Multiplayer Client Demo", 800, 600)
    engine.set_scene("game", NetworkScene(client))
    engine.run()

if __name__ == "__main__":
    main()
```

**Como Executar:**

1.  Abra um terminal e execute o servidor:
    ```bash
    python server.py
    ```
2.  Abra outro terminal e execute o cliente:
    ```bash
    python client.py
    ```
3.  Abra um terceiro terminal e execute outro cliente:
    ```bash
    python client.py
    ```

You verá duas janelas de jogo. Ao mover o jogador em uma janela (o quadrado verde), o quadrado azul na outra janela (o jogador remoto) se moverá de forma sincronizada, demonstrando a funcionalidade multiplayer da PyEngine.


