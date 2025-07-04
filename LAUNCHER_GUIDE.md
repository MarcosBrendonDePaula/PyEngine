# PyEngine Examples Launcher

## 🚀 Início Rápido

Para explorar todos os exemplos do PyEngine de forma interativa:

```bash
python launcher.py
```

Este comando abrirá o **PyEngine Examples Launcher** - um menu visual completo para navegar e executar todos os exemplos disponíveis.

## 📱 Interface do Launcher

### Principais Funcionalidades

🎮 **Menu Visual Interativo**
- Interface gráfica moderna e intuitiva
- Navegação por categorias organizadas
- Cards informativos para cada exemplo
- Lançamento direto com um clique

🔍 **Sistema de Categorias**
- **Performance**: Threading e otimizações
- **Physics**: Colisões e simulações físicas  
- **Graphics**: Iluminação e efeitos visuais
- **Animation**: Sprites e animações
- **UI**: Interface de usuário
- **Games**: Jogos completos
- **Templates**: Bases para projetos

⚡ **Recursos Avançados**
- Threading otimizado para interface responsiva
- Efeitos visuais e animações suaves
- Scroll suave com mouse ou teclado
- Indicadores de dificuldade e features

## 🎯 Como Usar

### 1. Executar o Launcher
```bash
# Na raiz do projeto PyEngine
python launcher.py
```

### 2. Navegar pelos Exemplos
- **Sidebar esquerda**: Clique nas categorias para filtrar
- **Cards centrais**: Informações detalhadas de cada exemplo
- **Mouse wheel**: Scroll pelos exemplos
- **Clique no card**: Lança o exemplo selecionado

### 3. Controles
| Ação | Controle |
|------|----------|
| Lançar exemplo | Clique no card |
| Filtrar categoria | Clique na sidebar |
| Scroll vertical | Mouse wheel ou ↑/↓ |
| Sair | ESC ou fechar janela |

## 📊 Exemplos Catalogados

### Por Dificuldade
- 🟢 **Beginner** (4 exemplos): UI Demo, Sprite Animation, Project Template, Simple Threading
- 🟡 **Intermediate** (5 exemplos): Collision Demo, Light Demo, Day/Night Cycle, State Machine, Puzzle Game  
- 🔴 **Advanced** (4 exemplos): Threading Demo, Directional Light, Water Particle, Local Multiplayer

### Exemplos em Destaque

**🧵 Threading Demo**
- Demonstra processamento paralelo com milhares de entidades
- Monitoramento de performance em tempo real
- Ideal para entender otimizações

**🎮 Collision Demo**  
- Sistema completo de detecção de colisões
- Física interativa e controles responsivos
- Ótimo para jogos de ação

**💡 Light Demo**
- Iluminação dinâmica com sombras
- Efeitos visuais avançados
- Perfeito para jogos atmosféricos

**🧩 UI Demo**
- Showcase completo de componentes de interface
- Botões, labels, e elementos interativos
- Base para qualquer aplicação

## 🛠️ Para Desenvolvedores

### Estrutura do Launcher
```
launcher_menu/
├── main.py                    # Entrada principal
├── scenes/main_menu_scene.py  # Scene do menu
├── components/menu_component.py # Componentes UI
├── utils/example_launcher.py  # Sistema de lançamento
└── launcher_config.json      # Configurações
```

### Adicionar Novos Exemplos

1. **Criar o exemplo** seguindo a estrutura padrão:
```
meu_exemplo/
├── main.py
└── scenes/
    └── minha_scene.py
```

2. **Registrar no launcher** editando `utils/example_launcher.py`:
```python
ExampleInfo(
    name="Meu Exemplo",
    description="Descrição do que faz",
    file_path="meu_exemplo/main.py",
    category="Minha Categoria",
    difficulty="Intermediate",
    features=["Feature 1", "Feature 2"]
)
```

3. **Usar formato padrão** no main.py:
```python
import multiprocessing as mp
from engine import create_engine
from scenes.minha_scene import MinhaScene

def main():
    cpu_count = mp.cpu_count()
    num_threads = max(1, int(cpu_count * 0.75))
    
    engine = create_engine(
        title="Meu Exemplo",
        width=800, height=600,
        num_threads=num_threads
    )
    
    scene = MinhaScene()
    engine.set_scene("main", scene)
    engine.run()

if __name__ == "__main__":
    main()
```

## 🎨 Personalização

### Configuração Visual
Edite `launcher_config.json` para personalizar:
- Cores da interface
- Tamanhos e layout  
- Animações e efeitos
- Comportamento de threading

### Exemplo de Configuração
```json
{
  "ui": {
    "theme": {
      "primary_color": [100, 149, 237],
      "card_background": [45, 45, 55]
    },
    "layout": {
      "cards_per_row": 3,
      "card_spacing": 20
    }
  }
}
```

## 🚀 Alternativas de Execução

### 1. Launcher Visual (Recomendado)
```bash
python launcher.py
```

### 2. Exemplo Específico
```bash
cd examples/threading_demo
python threading_demo.py
```

### 3. Launcher Menu Direto
```bash
cd examples/launcher_menu  
python main.py
```

## 💡 Dicas

- **Performance**: O launcher usa threading para manter a interface responsiva
- **Múltiplos exemplos**: Você pode executar vários exemplos simultaneamente
- **Threading demos**: Procure o indicador 🧵 para exemplos que demonstram paralelismo
- **Dificuldade**: Comece pelos exemplos 🟢 Beginner se for novo no PyEngine

## 🔧 Troubleshooting

### Launcher não abre
```bash
# Verificar dependências
pip install pygame

# Verificar estrutura
ls examples/launcher_menu/
```

### Exemplo não executa
- Verifique se o arquivo existe no caminho especificado
- Confirme que todas as dependências estão instaladas
- Use modo debug editando `launcher_config.json`

### Performance baixa
- Reduza `particle_count` na configuração
- Desabilite animações se necessário
- Use menos threads se o sistema for limitado

O **PyEngine Examples Launcher** é a forma mais fácil e visual de explorar todas as capacidades do engine! 🎮✨