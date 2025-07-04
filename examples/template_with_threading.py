"""
Template de exemplo no formato solicitado
Use este como base para seus jogos com threading otimizado
"""

import multiprocessing as mp
from engine import create_engine
from engine.core.scenes.base_scene import BaseScene

class MyGameScene(BaseScene):
    """Sua scene personalizada aqui"""
    
    def on_initialize(self):
        """Inicializar recursos da scene"""
        print("Inicializando scene...")
        # Adicionar suas entidades aqui
        pass
        
    def update(self, delta_time: float):
        """Update da scene (com threading automático)"""
        super().update(delta_time)
        # Sua lógica personalizada aqui
        
    def render(self, screen):
        """Render da scene"""
        super().render(screen)
        # Seu render personalizado aqui

def main():
    cpu_count = mp.cpu_count()
    print(f"System has {cpu_count} CPU cores")
    
    num_threads = max(1, int(cpu_count * 0.75))
    print(f"Using {num_threads} threads for processing")

    engine = create_engine(
        title="Meu Jogo PyEngine",
        width=800,
        height=600,
        num_threads=num_threads
    )
    
    my_scene = MyGameScene()
    engine.set_scene("main_scene", my_scene)
    
    engine.run()

if __name__ == "__main__":
    main()