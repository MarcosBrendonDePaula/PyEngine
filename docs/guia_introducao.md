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


