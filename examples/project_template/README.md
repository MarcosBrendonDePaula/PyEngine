# PyEngine Project Template

Template organizado para novos projetos PyEngine com threading otimizado e estrutura profissional.

## Estrutura do Projeto

```
project_template/
├── main.py                    # Ponto de entrada principal
├── scenes/                    # Todas as scenes do jogo
│   ├── __init__.py           
│   └── main_scene.py         # Scene principal (customize aqui)
├── components/               # Componentes customizados
│   ├── __init__.py
│   └── example_component.py  # Exemplo de componente
├── assets/                   # Recursos do jogo
│   ├── images/              # Imagens e sprites
│   ├── sounds/              # Efeitos sonoros e música
│   └── fonts/               # Fontes customizadas
└── README.md                # Esta documentação
```

## Como Usar Este Template

### 1. Copiar o Template

```bash
cp -r examples/project_template meu_novo_jogo
cd meu_novo_jogo
```

### 2. Personalizar o Projeto

#### main.py
```python
import multiprocessing as mp
from engine import create_engine
from scenes.main_scene import MainScene

def main():
    cpu_count = mp.cpu_count()
    num_threads = max(1, int(cpu_count * 0.75))
    
    engine = create_engine(
        title="Meu Jogo Incrível",  # ← Mude aqui
        width=1024, height=768,     # ← Ajuste resolução
        num_threads=num_threads
    )
    
    main_scene = MainScene()
    engine.set_scene("main", main_scene)
    engine.run()
```

#### scenes/main_scene.py
```python
def on_initialize(self):
    # Adicione suas entidades aqui
    player = Entity(512, 384)
    player.add_component(PlayerController())
    self.add_entity(player)
    
def update(self, delta_time: float):
    super().update(delta_time)  # Threading automático
    # Sua lógica de jogo aqui
```

### 3. Adicionar Componentes Customizados

```python
# components/player_controller.py
from engine import Component
import pygame

class PlayerController(Component):
    def __init__(self, speed=200):
        super().__init__()
        self.speed = speed
        
    def update(self):
        keys = pygame.key.get_pressed()
        dt = self.entity.delta_time
        
        if keys[pygame.K_LEFT]:
            self.entity.position.x -= self.speed * dt
        if keys[pygame.K_RIGHT]:
            self.entity.position.x += self.speed * dt
```

### 4. Executar o Projeto

```bash
python main.py
```

## Funcionalidades Incluídas

### ✅ Threading Otimizado
- Auto-detecção de CPU cores
- Threading inteligente para performance máxima
- Thread-safety automático

### ✅ Estrutura Profissional
- Organização clara de pastas
- Separação de responsabilidades
- Fácil manutenção e extensão

### ✅ Template Pronto
- Scene base funcional
- Exemplo de componente
- Sistema de eventos
- UI básica

## Expandindo o Projeto

### Adicionar Nova Scene

```python
# scenes/menu_scene.py
from engine import BaseScene

class MenuScene(BaseScene):
    def on_initialize(self):
        # Configurar menu
        pass
        
# main.py
from scenes.menu_scene import MenuScene

menu_scene = MenuScene()
engine.add_scene("menu", menu_scene)
engine.set_scene("menu", menu_scene)  # Usar como inicial
```

### Adicionar Novos Componentes

```python
# components/health_component.py
from engine import Component

class HealthComponent(Component):
    def __init__(self, max_health=100):
        super().__init__()
        self.max_health = max_health
        self.current_health = max_health
        
    def take_damage(self, amount):
        self.current_health = max(0, self.current_health - amount)
        
    def is_alive(self):
        return self.current_health > 0
```

### Adicionar Assets

```
assets/
├── images/
│   ├── player.png
│   ├── enemy.png
│   └── background.png
├── sounds/
│   ├── jump.wav
│   └── music.ogg
└── fonts/
    └── game_font.ttf
```

```python
# Usar assets na scene
def on_initialize(self):
    # Carregar imagem
    self.add_resource("player_sprite", "assets/images/player.png")
    
    # Usar em componente
    player_texture = self.get_resource("player_sprite")
```

## Exemplos de Uso

### Jogo Simples
```python
# scenes/simple_game_scene.py
class SimpleGameScene(BaseScene):
    def on_initialize(self):
        # Player
        player = Entity(400, 300)
        player.add_component(PlayerController(speed=300))
        player.add_component(RectangleRenderer(32, 32, (0, 255, 0)))
        self.add_entity(player)
        
        # Inimigos
        for i in range(10):
            enemy = Entity(random.randint(50, 750), random.randint(50, 550))
            enemy.add_component(EnemyAI())
            enemy.add_component(RectangleRenderer(24, 24, (255, 0, 0)))
            self.add_entity(enemy)
```

### Jogo com Muitas Entidades (Threading)
```python
def on_initialize(self):
    # Criar muitas partículas (vai usar threading automaticamente)
    for i in range(2000):
        particle = Entity(
            random.randint(0, 800), 
            random.randint(0, 600)
        )
        particle.add_component(ParticlePhysics())
        particle.add_component(ParticleRenderer())
        self.add_entity(particle)
```

## Performance

### Threading Automático
- **< 20 entidades**: Processamento sequencial
- **20+ entidades**: Threading automático
- **Speedup típico**: 2-4x em sistemas multi-core

### Monitoramento
```python
# Adicionar métricas de performance
def update(self, delta_time: float):
    start_time = time.time()
    super().update(delta_time)
    update_time = time.time() - start_time
    print(f"Update time: {update_time*1000:.2f}ms")
```

## Próximos Passos

1. **Personalize** o template para seu jogo específico
2. **Adicione** componentes customizados em `components/`
3. **Crie** novas scenes em `scenes/`
4. **Adicione** assets em `assets/`
5. **Teste** com diferentes números de entidades para ver o threading em ação
6. **Otimize** baseado nas métricas de performance

## Suporte

- Documentação completa: `docs/THREADING.md`
- Exemplos: `examples/organized_threading_demo/`
- Tests: `tests/test_threading.py`