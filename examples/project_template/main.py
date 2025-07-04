"""
PyEngine Project Template
Template organizado para novos projetos com threading otimizado
"""

import multiprocessing as mp
from engine import create_engine
from scenes.main_scene import MainScene

def main():
    """Ponto de entrada principal do projeto."""
    print("Meu Projeto PyEngine")
    print("=====================")
    
    # Configuração automática de threading
    cpu_count = mp.cpu_count()
    print(f"System has {cpu_count} CPU cores")
    
    num_threads = max(1, int(cpu_count * 0.75))
    print(f"Using {num_threads} threads for processing")

    # Criar engine com threading otimizado
    engine = create_engine(
        title="Meu Projeto PyEngine",
        width=1024,
        height=768,
        num_threads=num_threads
    )
    
    # Configurar scene principal
    main_scene = MainScene()
    engine.set_scene("main", main_scene)
    
    # Executar o jogo
    print("Iniciando jogo...")
    try:
        engine.run()
    except KeyboardInterrupt:
        print("\nJogo interrompido pelo usuário")
    finally:
        print("Jogo finalizado")

if __name__ == "__main__":
    main()