# Documentação Técnica da PyEngine

## 1. Visão Geral da Arquitetura

A PyEngine é uma engine de jogos 2D de alto desempenho desenvolvida em Python, utilizando a biblioteca Pygame. Ela foi projetada com uma arquitetura modular e um sistema de Componentes de Entidade (ECS) para oferecer flexibilidade e escalabilidade no desenvolvimento de jogos. A engine se destaca pelo processamento multi-core, sistemas avançados de iluminação, física, colisão, animação de sprites e um sistema de interface de usuário (UI) abrangente, além de suporte a multiplayer.

### Estrutura de Diretórios

O projeto PyEngine é organizado da seguinte forma:

- `PyEngine/`
  - `assets/`: Contém recursos do jogo, como imagens e áudios.
  - `docs/`: Documentação adicional, como o guia de criação de jogos em português.
  - `engine/`: O coração da engine, contendo os módulos principais.
    - `core/`: Módulos fundamentais da engine, como gerenciamento de interface, entidades, componentes, câmera, entrada, etc.
      - `components/`: Contém os diversos componentes que podem ser anexados às entidades (física, colisão, luz, UI, etc.).
        - `ui/`: Componentes específicos para a interface de usuário.
      - `scenes/`: Gerenciamento de cenas do jogo.
    - `multiplayer/`: Módulos relacionados à funcionalidade multiplayer (cliente, servidor, sincronização).
  - `scenes/`: Contém as implementações de cenas de demonstração e exemplos de uso da engine.
  - `tests/`: Módulos para testes da engine.
  - `main.py`: Ponto de entrada principal para a execução de demonstrações ou jogos.
  - `README.md`: Visão geral do projeto, recursos principais e exemplos de uso.
  - Outros arquivos `.py`: Exemplos de demonstração específicos (e.g., `collider_demo_main.py`, `light_demo_main.py`).

### Componentes Principais da Engine

A PyEngine é construída em torno de alguns conceitos chave:

- **Interface (`engine/core/interface.py`):** Gerencia a janela do jogo, o loop principal, eventos do Pygame e a transição entre cenas. É a camada de interação entre a engine e o sistema operacional/usuário.
- **Entidade (`engine/core/entity.py`):** Representa qualquer objeto no jogo (jogador, inimigo, item, etc.). Entidades são basicamente contêineres para componentes e possuem propriedades básicas como posição, velocidade, aceleração, rotação e escala. Elas não contêm lógica de jogo diretamente, mas delegam essa responsabilidade aos seus componentes.
- **Componente (`engine/core/component.py`):** Blocos de construção reutilizáveis que adicionam funcionalidade às entidades. Exemplos incluem `Physics` (para simulação física), `Collider` (para detecção de colisão), `LightComponent` (para iluminação), `KeyboardController` (para entrada do teclado), entre outros. Essa abordagem modular permite grande flexibilidade e facilita a extensão da engine.
- **Cena (`engine/core/scenes/base_scene.py` e `engine/core/scenes/scene_manager.py`):** Cenas são estados do jogo (e.g., menu principal, nível do jogo, tela de game over). O `SceneManager` gerencia a adição, remoção e transição entre essas cenas. Cada cena pode conter suas próprias entidades e lógica de jogo.
- **Input (`engine/core/input.py`):** Gerencia a entrada do usuário (teclado, mouse, gamepad).
- **Multi-core Processing:** A engine utiliza o módulo `multiprocessing` do Python para distribuir o processamento de entidades entre múltiplos núcleos da CPU, otimizando o desempenho.

## 2. Análise Detalhada dos Módulos e Funcionalidades

### 2.1. Sistema de Entidade-Componente (ECS)

O ECS é um padrão de arquitetura de software fundamental na PyEngine, promovendo um design de jogo modular e flexível. Em vez de criar hierarquias de classes complexas, o ECS separa os dados (Componentes) da lógica (Sistemas) e os associa a objetos genéricos (Entidades).

- **Entidades:** São identificadores únicos que não possuem dados ou comportamento intrínsecos. Elas servem como contêineres para Componentes.
- **Componentes:** São estruturas de dados que contêm apenas dados. Por exemplo, um `Physics` Component conteria massa, gravidade, velocidade, etc. Um `Sprite` Component conteria a imagem e informações de animação.
- **Sistemas:** São a lógica que opera sobre Entidades que possuem Componentes específicos. Por exemplo, um sistema de renderização processaria todas as Entidades que possuem um `Sprite` Component e um `Position` Component. Um sistema de física processaria Entidades com `Physics` e `Collider` Components.

**Vantagens do ECS na PyEngine:**
- **Flexibilidade:** Facilita a criação de novos tipos de objetos de jogo combinando diferentes componentes.
- **Reusabilidade:** Componentes podem ser reutilizados em várias entidades.
- **Manutenibilidade:** A lógica é separada dos dados, tornando o código mais fácil de entender e modificar.
- **Desempenho:** A separação de dados pode levar a melhorias de desempenho através de otimizações de cache e processamento paralelo.

### 2.2. Sistema de Física e Colisão

O sistema de física da PyEngine simula o movimento e a interação de objetos no ambiente do jogo. Ele é implementado através do `Physics` Component e do `Collider` Component.

- **`Physics` Component (`engine/core/components/physics.py`):** Gerencia propriedades físicas como massa, gravidade, atrito, restituição (elasticidade) e aplica forças e impulsos. Suporta corpos cinemáticos (objetos que se movem independentemente das forças físicas) e corpos estáticos (não-movíveis, mas colidíveis).
- **`Collider` Component (`engine/core/components/collider.py`):** Responsável pela detecção de colisões. A PyEngine oferece diversos tipos de colliders:
  - `Rectangle Colliders`
  - `Circle Colliders`
  - `Polygon Colliders` (Triângulo, Hexágono, Estrela, Formas em L, Formas Personalizadas)
- **Camadas e Máscaras de Colisão:** Permitem definir quais grupos de objetos interagem entre si, otimizando a detecção de colisão.
- **Resposta à Colisão:** A engine lida com a resposta à colisão, incluindo o efeito de "knockback" (empurrão).

### 2.3. Sistema de Iluminação

O sistema de iluminação da PyEngine adiciona realismo visual aos jogos, permitindo a criação de ambientes dinâmicos e imersivos. Ele é baseado no `LightComponent`.

- **`LightComponent` (`engine/core/components/light_component.py`):** Permite a criação de fontes de luz dinâmicas com cor, intensidade e raio personalizáveis. Suporta múltiplos tipos de luz:
  - **Luzes Pontuais:** Emitem luz de um único ponto em todas as direções.
  - **Luzes Direcionais:** Simulam fontes de luz distantes, como o sol, com raios paralelos.
  - **Luzes de Área:** Simulam fontes de luz maiores e mais difusas.
- **Ray Tracing:** Utiliza ray tracing para um comportamento de luz mais realista, incluindo sombreamento e mistura de cores.
- **Sombras e Mistura de Cores:** Permite a projeção de sombras e a combinação de cores de diferentes fontes de luz.
- **Ajustes de Temperatura de Luz:** Possibilita a configuração de temperaturas de luz quentes/frias para criar diferentes atmosferas.

### 2.4. Sistema de Interface de Usuário (UI)

A PyEngine oferece um sistema de UI abrangente para a criação de menus, HUDs e outros elementos interativos. Ele é construído sobre uma arquitetura hierárquica de componentes.

- **Controles Básicos:** Inclui elementos comuns de UI como `Labels` (rótulos de texto), `Buttons` (botões), `ProgressBar` (barra de progresso), `Slider` (controle deslizante), `Toggle` (alternador), `Input` (campo de texto de linha única) e `MultilineInput` (campo de texto de múltiplas linhas).
- **Componentes de Layout:** Permite organizar os elementos de UI com `Panel` (painel), `TitledPanel` (painel com título), `Grid` (grade), `ScrollView` (área de rolagem) e `Tabs` (abas).
- **Recursos Avançados:** Oferece funcionalidades mais complexas como `HTMLView` (visualização de conteúdo HTML), `Tooltip` (dica de ferramenta), `Modal` (janela modal), `Menu` (menu), `Image` (imagem), `RadioButton` (botão de rádio) e `Select`/`InputSelect` (seleção de opções).
- **Arquitetura da UI:**
  - **Sistema de Componentes Hierárquico:** Os elementos de UI podem ser aninhados, formando uma árvore de componentes.
  - **Propagação de Eventos:** Eventos do usuário (cliques, digitação) são propagados através da hierarquia da UI.
  - **Gerenciamento Automático de Layout:** Ajuda a organizar os elementos na tela de forma responsiva.
  - **Herança de Estilo e Gerenciamento de Estado:** Permite definir estilos para elementos de UI e gerenciar seus estados (e.g., hover, clicado).

### 2.5. Suporte a Multiplayer

A PyEngine inclui utilitários de rede leves para o desenvolvimento de jogos multiplayer, facilitando a comunicação entre clientes e servidores e a sincronização de entidades.

- **`DedicatedServer` (`engine/multiplayer/server.py`):** Usado para hospedar partidas e gerenciar jogadores conectados. Permite que o servidor controle a lógica do jogo e a comunicação.
- **`Client` (`engine/multiplayer/client.py`):** Permite que os clientes se conectem ao servidor e se comuniquem com ele. Um cliente pode ser marcado como `is_host=True` para indicar que ele está atuando como o servidor para outros peers.
- **`SyncComponent` (`engine/multiplayer/sync_component.py`):** Componente que facilita a sincronização de atributos de entidades entre clientes e o servidor. Ele inicia a rede automaticamente quando anexado a uma entidade e pode sincronizar qualquer atributo listado em `tracked_attrs`. Por padrão, ele sincroniza `position.x` e `position.y` para replicar o movimento das entidades com código mínimo.

### 2.6. Gerenciamento de Cenas

O `SceneManager` (`engine/core/scenes/scene_manager.py`) é responsável por organizar e controlar os diferentes estados do jogo. Cada cena (`BaseScene` em `engine/core/scenes/base_scene.py`) representa uma parte distinta do jogo, como um menu, um nível ou uma tela de game over.

- **`BaseScene`:** Classe base para todas as cenas, fornecendo métodos para inicialização, atualização, renderização e manipulação de eventos. As cenas podem conter suas próprias entidades e lógica de jogo.
- **Adição e Troca de Cenas:** O `SceneManager` permite adicionar cenas pelo nome e alternar entre elas de forma suave.
- **Gerenciamento de Recursos:** As cenas podem gerenciar o carregamento e descarregamento de recursos específicos, otimizando o uso de memória.

### 2.7. Outros Módulos Importantes

- **`Camera` e `AdvancedCamera` (`engine/core/camera.py`, `engine/core/advanced_camera.py`):** Controlam a visualização do mundo do jogo na tela, permitindo rolagem, zoom e outras transformações.
- **`Input` (`engine/core/input.py`):** Gerencia a entrada do usuário de teclado, mouse e gamepads, fornecendo uma interface unificada para acessar os estados dos dispositivos de entrada.
- **`AudioManager` (`engine/core/audio_manager.py`):** Gerencia a reprodução de áudio, incluindo música de fundo e efeitos sonoros.
- **`ResourceLoader` (`engine/core/resource_loader.py`):** Ajuda a carregar e gerenciar recursos do jogo, como imagens, sons e fontes.
- **`SaveManager` (`engine/core/save_manager.py`):** Fornece funcionalidades para salvar e carregar o estado do jogo.
- **`Pathfinding` (`engine/core/pathfinding.py`):** Implementa algoritmos de busca de caminho, como A* (`astar`), para navegação de entidades em ambientes de jogo.

## 3. Exemplos de Uso

Os exemplos de uso detalhados no `README.md` do projeto são excelentes pontos de partida para entender como as diferentes funcionalidades da PyEngine podem ser utilizadas. Eles demonstram a criação de jogos com multiplayer local, iluminação dinâmica, colisores avançados e simulações de partículas. Recomenda-se consultar o `README.md` original para os trechos de código completos e executáveis.

## 4. Análise e Sugestões de Melhoria

A PyEngine é um projeto ambicioso e bem estruturado, com uma base sólida para o desenvolvimento de jogos 2D em Python. O uso do ECS é um ponto forte, promovendo modularidade e flexibilidade. Os sistemas de física, iluminação e UI são impressionantes para uma engine em Python/Pygame.

### Pontos Fortes:
- **Arquitetura ECS:** Facilita a extensão e manutenção do código.
- **Processamento Multi-core:** Um diferencial importante para o desempenho em Python.
- **Sistemas Abrangentes:** Física, colisão, iluminação, UI e multiplayer são bem implementados.
- **Organização do Código:** A estrutura de diretórios é clara e lógica.
- **Documentação Inicial:** O `README.md` e o guia `CRIANDO_JOGOS_PT.md` são um bom começo.

### Pontos de Melhoria:

1.  **Documentação Mais Aprofundada:** Embora o `README.md` seja bom, uma documentação mais detalhada para cada módulo e classe seria extremamente útil. Isso incluiria:
    -   **Docstrings:** Adicionar docstrings completos para todas as classes, métodos e funções, explicando seus propósitos, parâmetros, retornos e exceções.
    -   **Tutoriais:** Criar tutoriais passo a passo para funcionalidades específicas (e.g., "Como criar um novo componente", "Como implementar um novo tipo de luz", "Como usar o sistema de UI para criar um menu").
    -   **Diagramas:** Incluir diagramas de arquitetura (UML, fluxo de dados) para visualizar as interações entre os módulos e o ECS.
    -   **Exemplos de Código:** Expandir os exemplos de código, talvez com pequenos projetos completos que demonstrem a integração de várias funcionalidades.

2.  **Sistema de Renderização:** Atualmente, a renderização parece ser feita diretamente pelos componentes. Considerar a implementação de um sistema de renderização centralizado que possa otimizar a ordem de desenho (e.g., por camadas, por material) e aplicar otimizações de desempenho (e.g., batching de sprites).

3.  **Editor de Níveis/Ferramentas:** Para facilitar o desenvolvimento de jogos, a criação de um editor de níveis simples ou ferramentas de depuração visuais seria um grande avanço. Isso poderia ser uma aplicação separada ou integrada à engine.

4.  **Otimização de Performance:** Embora o processamento multi-core seja um bom começo, investigar outras otimizações de desempenho específicas para Pygame e Python, como:
    -   **Otimização de Superfícies:** Uso eficiente de `convert()` e `convert_alpha()` para superfícies.
    -   **Pooling de Objetos:** Reutilização de objetos para evitar a criação e destruição constante, especialmente para partículas ou projéteis.
    -   **Cython/Numba:** Para partes críticas da engine que exigem alta performance, considerar a reescrita em Cython ou o uso de Numba para compilação JIT.

5.  **Sistema de Eventos Mais Robusto:** Embora o Pygame tenha seu próprio sistema de eventos, um sistema de eventos interno da engine mais robusto, com suporte a eventos personalizados e observadores, poderia simplificar a comunicação entre componentes e sistemas.

6.  **Testes Automatizados:** Expandir a cobertura de testes automatizados para garantir a estabilidade e o correto funcionamento de todas as funcionalidades à medida que a engine evolui.

### Futuras Funcionalidades (Features):

1.  **Sistema de Animação Avançado:**
    -   **Animações Baseadas em Esqueletos (Skeletal Animation):** Para personagens mais complexos e animações fluidas.
    -   **Transições de Animação:** Suporte a transições suaves entre diferentes estados de animação.
    -   **Editor de Animações:** Uma ferramenta visual para criar e gerenciar animações.

2.  **Sistema de Partículas Aprimorado:**
    -   **Editor de Partículas:** Uma ferramenta visual para projetar e ajustar sistemas de partículas.
    -   **Efeitos de Partículas 3D (Simulados):** Para efeitos como fumaça, fogo, água, etc., com mais profundidade.

3.  **Suporte a Tilemaps Avançado:**
    -   **Editor de Tilemaps:** Ferramenta para criar e editar mapas baseados em tiles.
    -   **Camadas de Tilemap:** Suporte a múltiplas camadas de tiles (fundo, colisão, primeiro plano).
    -   **Tiles Animados e Autotiles:** Funcionalidades para tiles que mudam ou se conectam automaticamente.

4.  **Inteligência Artificial (IA) Básica:**
    -   **Comportamentos Pré-definidos:** Implementação de comportamentos comuns de IA (e.g., perseguição, patrulha, evasão).
    -   **Sistemas de Tomada de Decisão:** Árvores de comportamento ou máquinas de estado finitas para NPCs.

5.  **Integração com Ferramentas Externas:**
    -   **Tiled Map Editor:** Suporte para importar mapas criados no Tiled.
    -   **Aseprite:** Integração para importar animações e spritesheets.

6.  **Sistema de Efeitos Visuais (VFX):**
    -   **Shaders:** Suporte a shaders personalizados para efeitos gráficos avançados.
    -   **Pós-processamento:** Efeitos como bloom, desfoque de movimento, correção de cor.

7.  **Suporte a Plataformas:**
    -   **Compilação para Executáveis:** Ferramentas para empacotar jogos para distribuição (e.g., PyInstaller).
    -   **Suporte a Mobile:** Adaptação para dispositivos móveis (Android/iOS) se viável com Pygame.

## 5. Conclusão

A PyEngine é uma ferramenta robusta e promissora para o desenvolvimento de jogos 2D em Python. Com sua arquitetura modular e foco em desempenho, ela oferece uma base sólida para a criação de jogos complexos e visualmente ricos. As sugestões de melhoria e futuras funcionalidades visam aprimorar ainda mais a usabilidade, a performance e a capacidade da engine, tornando-a uma escolha ainda mais atraente para desenvolvedores de jogos Python.




- **`AudioListener` e `AudioSource` (`engine/core/components/audio_listener.py`, `engine/core/components/audio_source.py`):** Gerenciam a audição e a emissão de sons no ambiente do jogo, permitindo áudio posicional e efeitos sonoros.
- **`DebugInfo` (`engine/core/components/debug_info.py`):** Fornece informações de depuração em tempo real, como FPS, uso de memória e contagem de entidades.
- **`DirectionalLight` (`engine/core/components/directional_light.py`):** Um tipo específico de componente de luz para simular fontes de luz distantes.
- **`GamepadController` (`engine/core/components/gamepad_controller.py`):** Permite o controle de entidades através de gamepads.
- **`HealthComponent` (`engine/core/components/health_component.py`):** Gerencia a saúde e o dano de entidades.
- **`InventoryComponent` (`engine/core/components/inventory_component.py`):** Permite que entidades possuam um inventário de itens.
- **`LogComponent` (`engine/core/components/log_component.py`):** Usado para registrar mensagens e eventos dentro do jogo.
- **`NetworkComponent` (`engine/core/components/network_component.py`):** Componente genérico para funcionalidades de rede, complementando o `SyncComponent`.
- **`ParticleSystem` (`engine/core/components/particle_system.py`):** Cria e gerencia efeitos visuais baseados em partículas, como fumaça, fogo e explosões.
- **`PositionalAudio` (`engine/core/components/positional_audio.py`):** Permite que sons sejam reproduzidos com base na posição da entidade no mundo do jogo.
- **`RectangleRenderer` (`engine/core/components/rectangle_renderer.py`):** Renderiza retângulos para entidades, útil para depuração ou elementos visuais simples.
- **`SpriteAnimation` (`engine/core/components/sprite_animation.py`):** Gerencia animações de sprites para entidades.
- **`StateMachineComponent` (`engine/core/components/state_machine_component.py`):** Implementa máquinas de estado para controlar o comportamento de entidades.
- **`TextureRenderer` (`engine/core/components/texture_renderer.py`):** Renderiza texturas para entidades.
- **`Tilemap` (`engine/core/components/tilemap.py`):** Gerencia mapas baseados em tiles.
- **`TimerComponent` (`engine/core/components/timer_component.py`):** Permite a criação de temporizadores e atrasos para eventos no jogo.
- **`UIComponent` (`engine/core/components/ui_component.py`):** Componente base para elementos de interface de usuário.




### 2.8. Detalhes da Implementação de Componentes e Módulos

#### 2.8.1. Interface (`engine/core/interface.py`)

A classe `Interface` é o ponto de entrada principal para a aplicação PyEngine, gerenciando a janela do Pygame, o loop do jogo e a transição de cenas. Ela abstrai a complexidade do Pygame, fornecendo uma interface limpa para os desenvolvedores de jogos.

- **Inicialização:** Pode ser inicializada com uma superfície Pygame existente ou com um título e dimensões para criar uma nova janela.
- **Gerenciamento de Cenas:** Utiliza um `SceneManager` interno para adicionar, definir e trocar cenas de forma eficiente. Cada cena é inicializada e tem sua referência de interface definida ao ser adicionada.
- **Loop Principal:** O método `run()` contém o loop principal do jogo, que processa eventos, atualiza a lógica da cena e renderiza o quadro. Ele calcula o `delta_time` para garantir que a lógica do jogo seja independente da taxa de quadros.
- **Controle de FPS:** Permite definir e obter a taxa de quadros alvo (`set_fps`, `get_fps`).
- **Propriedades da Tela:** Fornece acesso fácil à largura e altura da tela (`width`, `height`).

#### 2.8.2. Entidade (`engine/core/entity.py`)

A `Entity` é a base do sistema ECS da PyEngine. Ela é um contêiner genérico que pode ter múltiplos `Component`s anexados, definindo seu comportamento e dados. Entidades não possuem lógica de jogo intrínseca, delegando essa responsabilidade aos seus componentes.

- **Propriedades Básicas:** Cada entidade possui `position` (posição), `velocity` (velocidade), `acceleration` (aceleração), `rotation` (rotação) e `scale` (escala).
- **Gerenciamento de Componentes:** Métodos como `add_component()`, `get_component()`, `remove_component()` permitem a manipulação dinâmica de componentes em tempo de execução.
- **Ciclo de Vida:** Métodos como `tick()` (atualização lógica) e `render()` (renderização) são chamados pela engine, que por sua vez chamam os métodos correspondentes em seus componentes habilitados.
- **Hierarquia:** Entidades podem ter entidades filhas, permitindo a criação de estruturas complexas e relacionamentos pai-filho.

#### 2.8.3. Componente (`engine/core/component.py`)

`Component` é a classe base para todos os componentes na PyEngine. Componentes são blocos de construção reutilizáveis que encapsulam dados e lógica específica, adicionando funcionalidade a uma `Entity`.

- **Anexação a Entidades:** O método `attach()` é chamado quando um componente é adicionado a uma entidade, fornecendo uma referência à entidade pai.
- **Habilitação/Desabilitação:** A propriedade `enabled` permite ativar ou desativar a funcionalidade de um componente dinamicamente.
- **Ciclo de Vida:** Componentes podem implementar métodos `tick()` e `render()` que são chamados pela entidade pai, permitindo que eles atualizem sua lógica e se desenhem.

#### 2.8.4. Sistema de Cenas (`engine/core/scenes/base_scene.py`, `engine/core/scenes/scene_manager.py`)

O sistema de cenas organiza o jogo em diferentes estados lógicos, como menus, níveis e telas de game over. O `SceneManager` gerencia a transição entre essas cenas.

- **`BaseScene`:** A classe base para todas as cenas. Fornece métodos para:
  - `initialize()`: Chamado uma vez quando a cena é carregada.
  - `tick(delta_time)`: Atualiza a lógica de todas as entidades na cena.
  - `render(screen)`: Renderiza todas as entidades na cena na tela.
  - `handle_event(event)`: Processa eventos do Pygame para a cena e suas entidades.
  - `add_entity(entity, layer)`: Adiciona uma entidade a uma camada específica dentro da cena.
  - `remove_entity(entity)`: Remove uma entidade da cena.
- **`SceneManager`:** Gerencia a coleção de cenas e a cena atualmente ativa.
  - `add_scene(name, scene)`: Adiciona uma cena ao gerenciador.
  - `set_scene(name, transition)`: Define a cena ativa, com opção de transição.
  - `get_current_scene()`: Retorna a cena atualmente ativa.
  - `update(delta_time)` e `render(screen)`: Chamam os métodos correspondentes da cena ativa.

#### 2.8.5. Input (`engine/core/input.py`)

O módulo `Input` fornece uma interface unificada para gerenciar a entrada do usuário de teclado, mouse e gamepads. Ele simplifica a detecção de pressionamentos de tecla, cliques do mouse e estados do gamepad.

- **Teclado:** Métodos para verificar se uma tecla está pressionada (`is_key_pressed`), foi pressionada uma vez (`is_key_down`) ou foi liberada (`is_key_up`).
- **Mouse:** Métodos para obter a posição do mouse (`get_mouse_pos`), verificar cliques de botão (`is_mouse_button_pressed`, `is_mouse_button_down`, `is_mouse_button_up`).
- **Gamepad:** Suporte para detecção de botões e eixos de gamepads conectados.

#### 2.8.6. Multiplayer (`engine/multiplayer/client.py`, `engine/multiplayer/server.py`, `engine/multiplayer/sync_component.py`)

O sistema multiplayer da PyEngine é leve e focado na sincronização de entidades e comunicação básica entre clientes e servidores.

- **`DedicatedServer` (`engine/multiplayer/server.py`):** Implementa um servidor de rede que pode hospedar partidas. Ele gerencia conexões de clientes, recebe e envia dados, e pode ser estendido para implementar a lógica de jogo do lado do servidor.
- **`Client` (`engine/multiplayer/client.py`):** Permite que um cliente se conecte a um `DedicatedServer`. Ele lida com o envio e recebimento de mensagens, e pode ser configurado para atuar como host (`is_host=True`) para outros peers.
- **`SyncComponent` (`engine/multiplayer/sync_component.py`):** Um componente crucial para a sincronização de estado de entidades entre clientes e o servidor. Ele pode ser anexado a qualquer entidade e configurado para rastrear atributos específicos (`tracked_attrs`). Quando esses atributos mudam, o `SyncComponent` envia automaticamente atualizações pela rede, garantindo que a posição, por exemplo, de um jogador seja replicada em todos os clientes conectados.

#### 2.8.7. Sistema de Animação (`engine/core/sprite.py`, `engine/core/components/sprite_animation.py`)

O sistema de animação da PyEngine é baseado em spritesheets e oferece controle granular sobre as animações.

- **`Sprite` (`engine/core/sprite.py`):** Representa um sprite individual ou uma folha de sprites. Gerencia o carregamento, corte e acesso a quadros de animação.
- **`SpriteAnimation` (`engine/core/components/sprite_animation.py`):** Um componente que pode ser anexado a uma entidade para gerenciar suas animações. Suporta:
  - **Animações Baseadas em Faixas:** Define animações a partir de linhas específicas em uma folha de sprites.
  - **Tamanhos de Quadro Variáveis:** Permite que os quadros de animação tenham dimensões diferentes.
  - **Múltiplas Animações por Linha:** Suporte para várias sequências de animação em uma única linha da folha de sprites.
  - **Gerenciamento de Estado de Animação:** Animações contínuas, enfileiramento de animações, callbacks de quadro e controle de velocidade.
  - **Inversão de Sprite:** Inversão horizontal de sprites para direções.

#### 2.8.8. Sistema de Partículas (`engine/core/components/particle_system.py`)

O `ParticleSystem` é um componente poderoso para criar efeitos visuais dinâmicos, como fumaça, fogo, explosões, chuva e outros. Ele gera e gerencia um grande número de pequenas partículas que se movem e mudam ao longo do tempo.

- **Configuração Flexível:** Permite configurar a taxa de emissão, tempo de vida das partículas, velocidade inicial, cor, tamanho e comportamento ao longo do tempo.
- **Efeitos Visuais:** Ideal para adicionar detalhes e imersão ao ambiente do jogo.

#### 2.8.9. Tilemap (`engine/core/components/tilemap.py`)

O componente `Tilemap` facilita a criação de mundos de jogo baseados em grades, como jogos de plataforma, RPGs e estratégias. Ele gerencia a renderização de tiles e pode ser usado para definir colisões e outras propriedades do ambiente.

- **Carregamento de Mapas:** Suporta o carregamento de dados de tilemap.
- **Renderização Eficiente:** Otimizado para desenhar grandes mapas de tiles.
- **Colisões Baseadas em Tiles:** Pode ser configurado para gerar colisores automaticamente a partir dos tiles.





## 3. Exemplos de Uso Detalhados

Para ilustrar a aplicação prática dos conceitos e módulos da PyEngine, apresentamos exemplos de código comentados. Estes exemplos demonstram como inicializar a engine, criar entidades, anexar componentes e gerenciar cenas, cobrindo funcionalidades como multiplayer local, iluminação dinâmica, colisões avançadas e simulações de partículas.

### 3.1. Jogo de Combate Multiplayer Local

Este exemplo demonstra a criação de um jogo simples de combate multiplayer local, onde dois jogadores controlam entidades com física e colisão, e um sistema de log exibe mensagens do jogo.

```python
import pygame
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.physics import Physics
from engine.core.components.collider import Collider
from engine.core.components.log_component import LogComponent

class Player(Entity):
    def __init__(self, x: float, y: float, color: tuple, controls: dict, player_num: int):
        super().__init__(x, y)
        # Adiciona componente de física para movimento
        self.physics = self.add_component(Physics(mass=1.0, gravity=0, friction=0.8))
        self.physics.restitution = 0.5  # Adiciona "quique" (bounce)
        
        # Adiciona componente de colisão
        self.collider = self.add_component(Collider(40, 40))
        
        # Configura propriedades do jogador
        self.controls = controls
        self.speed = 8.0
        self.health = 100
        self.player_num = player_num
        
    def tick(self):
        super().tick()
        # Lida com o movimento baseado nos controles
        keys = pygame.key.get_pressed()
        dx = dy = 0
        
        if keys[self.controls["left"]]: dx -= self.speed
        if keys[self.controls["right"]]: dx += self.speed
        if keys[self.controls["up"]]: dy -= self.speed
        if keys[self.controls["down"]]: dy += self.speed
            
        self.physics.set_velocity(dx, dy)

class MultiplayerScene(BaseScene):
    def __init__(self):
        super().__init__()
        
        # Adiciona sistema de log
        logger_entity = Entity(10, 10)
        self.logger = logger_entity.add_component(LogComponent(max_messages=5))
        self.add_entity(logger_entity, "ui")
        
        # Cria Jogador 1 (Azul, controles WASD)
        self.player1 = Player(200, 300, (0, 0, 255), {
            "up": pygame.K_w,
            "down": pygame.K_s,
            "left": pygame.K_a,
            "right": pygame.K_d,
            "attack": pygame.K_SPACE
        }, 1)
        self.add_entity(self.player1, "players")
        
        # Cria Jogador 2 (Verde, controles de seta)
        self.player2 = Player(600, 300, (0, 255, 0), {
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "attack": pygame.K_RETURN
        }, 2)
        self.add_entity(self.player2, "players")
        
        self.logger.log("Game Started!", "info", 3.0)

def main():
    engine = create_engine("Local Multiplayer Demo", 800, 600)
    engine.set_scene("game", MultiplayerScene())
    engine.run()

if __name__ == "__main__":
    main()
```

### 3.2. Jogo de Plataforma com Iluminação Dinâmica

Este exemplo ilustra a criação de um jogo de plataforma simples com um jogador que interage com plataformas e um sistema de iluminação dinâmica, onde o jogador emite luz e há uma luz ambiente.

```python
import pygame
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.physics import Physics
from engine.core.components.collider import RectCollider
from engine.core.components.light_component import LightComponent

class Player(Entity):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        # Física com gravidade
        self.physics = self.add_component(Physics(
            mass=1.0,
            gravity=0.5,
            friction=0.3
        ))
        self.physics.restitution = 0.0  # Sem "quique"
        
        # Colisão
        self.collider = self.add_component(RectCollider(40, 40))
        
        # Luz do jogador
        self.light = self.add_component(LightComponent(
            color=(255, 220, 150),  # Luz quente
            intensity=1.2,
            radius=200
        ))
    
    def jump(self):
        if self.physics.is_grounded:
            self.physics.apply_impulse(0, -12.0)

class Platform(Entity):
    def __init__(self, x: float, y: float, width: float, height: float):
        super().__init__(x, y)
        # Física estática
        self.physics = self.add_component(Physics())
        self.physics.set_kinematic(True)
        
        # Colisão
        self.collider = self.add_component(RectCollider(width, height))

class PlatformerScene(BaseScene):
    def __init__(self):
        super().__init__()
        # Cria jogador
        self.player = Player(400, 300)
        self.add_entity(self.player, "player")
        
        # Cria plataformas
        self._create_platforms()
        
        # Adiciona luz ambiente
        ambient = Entity(400, 300)
        ambient.add_component(LightComponent(
            color=(100, 100, 150),
            intensity=0.5,
            radius=800
        ))
        self.add_entity(ambient, "lights")
    
    def _create_platforms(self):
        # Chão
        self.add_entity(Platform(400, 550, 800, 40), "platforms")
        # Plataformas flutuantes
        self.add_entity(Platform(200, 400, 200, 20), "platforms")
        self.add_entity(Platform(600, 300, 200, 20), "platforms")
        self.add_entity(Platform(400, 200, 200, 20), "platforms")

def main():
    engine = create_engine("Platformer Demo", 800, 600)
    engine.set_scene("game", PlatformerScene())
    engine.run()

if __name__ == "__main__":
    main()
```

### 3.3. Jogo de Quebra-Cabeça com Colisores Avançados

Este exemplo demonstra o uso de diferentes tipos de colisores (círculo, triângulo, estrela) para criar peças de quebra-cabeça que interagem fisicamente.

```python
import math
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.collider import CircleCollider, PolygonCollider
from engine.core.components.physics import Physics

class PuzzlePiece(Entity):
    def __init__(self, x: float, y: float, shape_type: str, size: float):
        super().__init__(x, y)
        # Adiciona física
        self.physics = self.add_component(Physics(
            mass=1.0,
            gravity=0,
            friction=0.8
        ))
        
        # Adiciona colisor específico para a forma
        if shape_type == "circle":
            self.collider = self.add_component(CircleCollider(size))
        elif shape_type == "triangle":
            points = [
                (-size/2, size/2),  # Inferior esquerdo
                (size/2, size/2),   # Inferior direito
                (0, -size/2)        # Superior
            ]
            self.collider = self.add_component(PolygonCollider(points))
        elif shape_type == "star":
            self.collider = self.add_component(PolygonCollider(self._create_star_points(size)))
    
    def _create_star_points(self, size):
        points = []
        for i in range(10):
            angle = math.pi * i / 5 - math.pi/2
            radius = size/2 if i % 2 == 0 else size/4
            px = math.cos(angle) * radius
            py = math.sin(angle) * radius
            points.append((px, py))
        return points

class PuzzleScene(BaseScene):
    def __init__(self):
        super().__init__()
        # Cria peças do quebra-cabeça
        self._create_puzzle_pieces()
    
    def _create_puzzle_pieces(self):
        # Peça circular
        self.add_entity(PuzzlePiece(200, 300, "circle", 40), "pieces")
        # Peça triangular
        self.add_entity(PuzzlePiece(400, 300, "triangle", 50), "pieces")
        # Peça em forma de estrela
        self.add_entity(PuzzlePiece(600, 300, "star", 60), "pieces")

def main():
    engine = create_engine("Puzzle Demo", 800, 600)
    engine.set_scene("game", PuzzleScene())
    engine.run()

if __name__ == "__main__":
    main()
```

### 3.4. Demonstração de Simulador de Líquidos

Este exemplo mostra como integrar uma cena de simulação de líquidos, demonstrando a capacidade da engine de lidar com efeitos visuais complexos.

```python
import pygame
from engine.core.scenes.scene_manager import SceneManager
from scenes.liquid_demo_scene import LiquidDemoScene

pygame.init()
screen = pygame.display.set_mode((800, 600))
manager = SceneManager()
manager.add_scene("liquid", LiquidDemoScene())
manager.set_scene("liquid", transition=False)
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        manager.handle_event(event)
    manager.update()
    screen.fill((0, 0, 0))
    manager.render(screen)
    pygame.display.flip()
    clock.tick(60)
```

### 3.5. Demonstração de Partículas de Água

Similar ao simulador de líquidos, este exemplo foca na demonstração de um sistema de partículas de água, ideal para efeitos visuais como chuva, respingos ou fluidos.

```python
import pygame
from engine.core.scenes.scene_manager import SceneManager
from scenes.water_particle_scene import WaterParticleScene

pygame.init()
screen = pygame.display.set_mode((800, 600))
manager = SceneManager()
manager.add_scene("water", WaterParticleScene())
manager.set_scene("water", transition=False)
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        manager.handle_event(event)
    manager.update()
    screen.fill((0, 0, 0))
    manager.render(screen)
    pygame.display.flip()
    clock.tick(60)
```

### 3.6. Demonstração de Multiplayer em Rede

Este exemplo mostra como configurar um servidor e clientes para um jogo multiplayer em rede, onde o movimento dos jogadores é sincronizado entre todos os peers conectados.

**Servidor:**
```bash
python network_server.py
```

**Cliente:**
```bash
python network_client.py player1
python network_client.py player2 --host 127.0.0.1 --port 6000
```

O script do cliente utiliza `DedicatedServer`, `Client` e `SyncComponent` para replicar a posição de cada jogador em todos os peers conectados.


