# Guia de Uso da PyEngine: Criando Seu Primeiro Jogo

## 1. Introdução à PyEngine

A PyEngine é uma poderosa engine de jogos 2D desenvolvida em Python, construída sobre a biblioteca Pygame. Ela foi projetada para simplificar o desenvolvimento de jogos, oferecendo uma arquitetura modular baseada em Componentes de Entidade (ECS), processamento multi-core para otimização de desempenho, e sistemas avançados para iluminação, física, colisão, animação e interface de usuário (UI). Este guia prático tem como objetivo ensinar desenvolvedores a utilizar a PyEngine para criar seus próprios jogos, desde os conceitos básicos até a implementação de funcionalidades mais complexas.

### 1.1. Por Que Usar a PyEngine?

A PyEngine se destaca por:

- **Modularidade e Flexibilidade:** O sistema ECS permite que você construa objetos de jogo complexos combinando componentes reutilizáveis, facilitando a manutenção e a extensão do seu projeto.
- **Desempenho Otimizado:** Com suporte a processamento multi-core, a engine distribui a carga de trabalho entre os núcleos da CPU, garantindo uma execução mais fluida, mesmo em jogos com muitas entidades.
- **Recursos Abrangentes:** Desde um sistema de física robusto e iluminação dinâmica até um sistema de UI completo e suporte a multiplayer, a PyEngine oferece as ferramentas necessárias para criar jogos ricos em funcionalidades.
- **Facilidade de Uso:** Apesar de sua capacidade, a PyEngine busca ser acessível, com uma API intuitiva e exemplos claros que demonstram seu uso.

### 1.2. Instalação

Para começar a usar a PyEngine, você precisa instalá-la em seu ambiente Python. Recomenda-se criar um ambiente virtual para gerenciar as dependências do projeto.

1.  **Clone o Repositório:**

    Primeiro, clone o repositório da PyEngine do GitHub para o seu sistema local:

    ```bash
    git clone https://github.com/MarcosBrendonDePaula/PyEngine
    cd PyEngine
    ```

2.  **Instale as Dependências:**

    A PyEngine utiliza o Pygame e outras bibliotecas. Você pode instalar todas as dependências e a própria engine em modo editável (o que permite que você faça alterações no código da engine e veja os resultados imediatamente) usando `pip`:

    ```bash
    pip install -e .
    ```

    Se você encontrar problemas com o Pygame, certifique-se de ter as dependências do sistema operacional necessárias. Para sistemas baseados em Debian/Ubuntu, você pode precisar instalar:

    ```bash
    sudo apt-get install python3-dev libsdl1.2-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsmpeg-dev libportmidi-dev libavformat-dev libswscale-dev
    ```

    Após a instalação, você estará pronto para começar a desenvolver com a PyEngine.

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

## 3. Adicionando Interatividade: Colisões e UI

Vamos aprimorar nosso jogo adicionando detecção de colisões e elementos de interface de usuário.

### 3.1. Configurando Colisores

Para que as entidades interajam fisicamente, elas precisam de um componente `Collider`. A PyEngine oferece vários tipos de colisores. Vamos adicionar um `RectCollider` ao nosso jogador e criar uma parede com a qual ele possa colidir.

```python
from engine.core.components.collider import RectCollider

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

    # ... (render como antes)
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

    # ... (tick e render como antes)
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

Você verá duas janelas de jogo. Ao mover o jogador em uma janela (o quadrado verde), o quadrado azul na outra janela (o jogador remoto) se moverá de forma sincronizada, demonstrando a funcionalidade multiplayer da PyEngine.

## 5. Melhores Práticas e Dicas

Para desenvolver jogos eficientes e manuteníveis com a PyEngine, considere as seguintes melhores práticas:

### 5.1. Otimização de Performance

-   **Reutilização de Objetos (Object Pooling):** Para entidades que são criadas e destruídas frequentemente (como projéteis ou partículas), use um pool de objetos para reutilizá-las em vez de criar novas instâncias repetidamente. Isso reduz a sobrecarga do coletor de lixo do Python.
-   **Otimização de Superfícies Pygame:** Ao carregar imagens, use `pygame.image.load("path/to/image.png").convert_alpha()` para imagens com transparência ou `convert()` para imagens sem transparência. Isso otimiza a imagem para o formato de pixel da tela, acelerando a renderização.
-   **Processamento Multi-core:** A PyEngine já utiliza processamento multi-core para entidades. Certifique-se de que suas lógicas de `tick` e `render` em componentes e entidades sejam o mais eficientes possível para aproveitar isso.
-   **Evite Cálculos Desnecessários:** Calcule valores uma vez e armazene-os se forem usados múltiplas vezes. Evite cálculos complexos dentro do loop principal do jogo (`tick` e `render`) se puderem ser feitos com menos frequência.

### 5.2. Estrutura de Projeto

Organizar seu projeto de jogo de forma lógica é crucial para a manutenibilidade:

-   **Separação de Preocupações:** Mantenha a lógica do jogo separada da lógica da engine. Suas entidades e componentes devem focar no comportamento específico do seu jogo.
-   **Diretórios Claros:** Crie diretórios para `assets` (imagens, sons), `scenes` (suas classes de cena), `entities` (suas classes de entidade), `components` (seus componentes personalizados), etc.
-   **Nomenclatura Consistente:** Use uma convenção de nomenclatura clara e consistente para arquivos, classes, métodos e variáveis.

### 5.3. Depuração

-   **`LogComponent`:** Utilize o `LogComponent` da PyEngine para exibir mensagens de depuração na tela do jogo. Isso é útil para rastrear eventos e estados sem precisar de um depurador externo.
-   **Visualização de Colisores:** A PyEngine permite visualizar os colisores das entidades (geralmente em modo de depuração). Ative isso para verificar se seus colisores estão configurados corretamente e se as colisões estão ocorrendo como esperado.
-   **Impressões de Depuração:** Use `print()` para depuração rápida, mas remova-as ou desative-as em builds de produção para evitar impacto no desempenho.
-   **Ferramentas de Depuração Python:** Para problemas mais complexos, utilize um depurador Python (como o do VS Code ou PyCharm) para inspecionar o estado do seu programa passo a passo.

## 6. Conclusão

Este guia forneceu uma introdução abrangente ao uso da PyEngine, cobrindo desde a configuração inicial até a implementação de funcionalidades avançadas como iluminação e multiplayer. A arquitetura baseada em ECS da PyEngine, combinada com seus recursos otimizados, oferece uma base sólida para o desenvolvimento de jogos 2D em Python. Ao seguir as melhores práticas e explorar os exemplos fornecidos, você estará bem equipado para criar jogos inovadores e envolventes.

Lembre-se de que a melhor forma de aprender é praticando. Experimente, modifique os exemplos e crie seus próprios componentes e entidades para entender profundamente como a PyEngine funciona e como você pode adaptá-la às suas necessidades. Boa sorte em sua jornada de desenvolvimento de jogos com a PyEngine!


