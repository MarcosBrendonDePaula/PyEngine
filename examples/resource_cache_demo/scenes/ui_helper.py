from .ui_wrapper import ButtonWrapper, LabelWrapper

def create_ui(scene):
    """Create UI elements for the demo"""
    # Create title label
    title_label = LabelWrapper(
        x=20, 
        y=20, 
        text="Resource Cache Demo",
        font_size=24
    )
    title_label.set_text_color((255, 255, 255))
    scene.add_entity(title_label)
    
    # Create demo buttons
    button_y = 60
    for i, name in enumerate(scene.demo_names):
        button = ButtonWrapper(
            x=150,
            y=button_y,
            width=200,
            height=30,
            text=name
        )
        # Set click handler
        button.set_on_click(lambda idx=i: scene._on_demo_button_click(idx))
        button.demo_index = i
        scene.demo_buttons.append(button)
        scene.add_entity(button)
        button_y += 40
    
    # Create description label
    scene.description_label = LabelWrapper(
        x=50,
        y=button_y + 10,
        text=scene.demo_descriptions[0],
        font_size=16
    )
    scene.description_label.set_text_color((200, 200, 200))
    scene.add_entity(scene.description_label)
    
    # Create stats labels
    scene.stats_labels = []
    for i in range(5):
        label = LabelWrapper(
            x=50,
            y=400 + i * 25,
            text="",
            font_size=16
        )
        label.set_text_color((200, 200, 200))
        scene.stats_labels.append(label)
        scene.add_entity(label)

def update_stats_labels(scene):
    """Update the stats labels with current information"""
    # Clear existing labels
    for label in scene.stats_labels:
        label.set_text("")
    
    # Update load time comparison if available
    if len(scene.load_times) >= 2:
        scene.stats_labels[0].set_text(f"First load time: {scene.load_times[0]*1000:.2f}ms")
        scene.stats_labels[1].set_text(f"Second load time: {scene.load_times[1]*1000:.2f}ms")
        speedup = scene.load_times[0] / max(scene.load_times[1], 0.0001)
        scene.stats_labels[2].set_text(f"Speedup: {speedup:.2f}x")
    
    # Update cache stats if available
    if scene.stats and 'cache' in scene.stats:
        scene.stats_labels[3].set_text(
            f"Cache: {scene.stats['cache']['total_resources']} resources, "
            f"{scene.stats['cache']['memory_usage_mb']:.2f}MB used"
        )

def update_preloading_progress(scene):
    """Update the preloading progress display"""
    if scene.demo_state == "preloading":
        scene.stats_labels[0].set_text(f"Preloading resources: {scene.preload_progress}/{scene.preload_total}")
        
        # Update progress in other labels
        progress_pct = scene.preload_progress / scene.preload_total
        scene.stats_labels[1].set_text(f"Progress: {progress_pct*100:.0f}%")
