import pygame
from engine.core.scenes.base_scene import BaseScene
from engine.core.entity import Entity
from engine.core.components.ui.progress_bar import ProgressBar
from engine.core.components.ui.input import Input
from engine.core.components.ui.select import Select
from engine.core.components.ui.input_select import InputSelect
from engine.core.components.ui.radio_button import RadioGroup
from engine.core.components.ui.label import Label
from engine.core.components.ui.html_view import HTMLView
from engine.core.components.ui.slider import Slider
from engine.core.components.ui.toggle import Toggle
from engine.core.components.ui.tooltip import TooltipMixin, Tooltip
from engine.core.components.ui.modal import MessageBox, ConfirmDialog
from engine.core.components.ui.tabs import Tabs
from engine.core.components.ui.menu import Menu, MenuItem
from engine.core.components.ui.grid import Grid, GridColumn
from engine.core.components.ui.image import Image, Icon
from engine.core.components.ui.scrollview import ScrollView
from engine.core.components.ui.titled_panel import TitledPanel
from engine.core.components.ui.button import Button
from engine.core.components.ui.multiline_input import MultilineInput
from engine.core.components.ui.checkbox import Checkbox
from engine.core.components.ui.circular_progress import CircularProgress

class TooltipButton(Button, TooltipMixin):
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, tooltip_text: str):
        Button.__init__(self, x, y, width, height, text)
        TooltipMixin.__init__(self, tooltip_text)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        return TooltipMixin.handle_event(self, event)
    
    def render(self, screen: pygame.Surface):
        Button.render(self, screen)
        TooltipMixin.render(self, screen)

class UIEntity(Entity):
    def __init__(self, ui_element):
        super().__init__()
        self.ui_element = ui_element
        
    def render(self, screen: pygame.Surface, offset=(0, 0)):
        self.ui_element.render(screen)
        
    def handle_event(self, event: pygame.event.Event):
        self.ui_element.handle_event(event)

class UIDemoScene(BaseScene):
    def __init__(self):
        super().__init__()
        
        # Create scrollable container for all content
        self.scroll_view = ScrollView(0, 0, 800, 600)
        self.add_entity(UIEntity(self.scroll_view), "ui")
        
        # Create tabs
        self.tabs = Tabs(20, 20, 760, 560)
        self.scroll_view.add_child(self.tabs)
        
        # Basic Controls Tab
        basic_panel = self.tabs.add_tab("basic", "Basic Controls")
        self._setup_basic_controls(basic_panel)
        
        # Advanced Controls Tab
        advanced_panel = self.tabs.add_tab("advanced", "Advanced Controls")
        self._setup_advanced_controls(advanced_panel)
        
        # Data Display Tab
        data_panel = self.tabs.add_tab("data", "Data Display")
        self._setup_data_display(data_panel)
    
    def _setup_basic_controls(self, panel):
        """Setup basic controls demo"""
        y = 20
        
        # Progress Bar
        progress_label = Label(20, y, "Progress Bar:")
        panel.add_child(progress_label)
        
        self.progress_bar = ProgressBar(20, y + 30, 300, 30)
        self.progress_bar.progress = 0.7
        panel.add_child(self.progress_bar)
        
        # Slider
        y += 80
        slider_label = Label(20, y, "Slider:")
        panel.add_child(slider_label)
        
        self.slider = Slider(20, y + 30, 300, 30)
        self.slider.on_value_changed = lambda v: print(f"Slider value: {v}")
        panel.add_child(self.slider)
        
        # Toggle Switch
        y += 80
        toggle_label = Label(20, y, "Toggle Switch:")
        panel.add_child(toggle_label)
        
        self.toggle = Toggle(20, y + 30)
        self.toggle.on_value_changed = lambda v: print(f"Toggle value: {v}")
        panel.add_child(self.toggle)
        
        # Button with Tooltip
        y += 80
        tooltip_label = Label(20, y, "Button with Tooltip:")
        panel.add_child(tooltip_label)
        
        self.tooltip_button = TooltipButton(20, y + 30, 200, 40,
                                          "Hover Me",
                                          "This is a tooltip!")
        panel.add_child(self.tooltip_button)

        # Multiline Input
        y += 80
        multiline_label = Label(20, y, "Multiline Input:")
        panel.add_child(multiline_label)
        
        self.multiline_input = MultilineInput(20, y + 30, 400, 150,
                                            "Type multiple lines here...")
        self.multiline_input.set_text("This is a multiline input field.\nYou can type multiple lines of text.\nIt supports scrolling and text selection.")
        panel.add_child(self.multiline_input)

        # HTML View
        y += 200
        html_label = Label(20, y, "HTML View:")
        panel.add_child(html_label)
        
        self.html_view = HTMLView(20, y + 30, 700, 150)
        sample_html = """
        <h1>HTML Demo</h1>
        <p>This is a <b>paragraph</b> with some <i>formatted</i> text.</p>
        <h2>Features</h2>
        <p>Supports basic HTML tags:<br>
        - Headings (h1-h6)<br>
        - Paragraphs<br>
        - Line breaks</p>
        """
        self.html_view.set_html(sample_html)
        panel.add_child(self.html_view)

        # Checkbox
        y += 200
        checkbox_label = Label(20, y, "Checkbox:")
        panel.add_child(checkbox_label)

        self.checkbox = Checkbox(20, y + 30, 20, "Accept")
        panel.add_child(self.checkbox)

        # Circular Progress
        y += 80
        circle_label = Label(20, y, "Circular Progress:")
        panel.add_child(circle_label)

        self.progress_circle = CircularProgress(20, y + 60, 30)
        self.progress_circle.progress = 0.5
        panel.add_child(self.progress_circle)
    
    def _setup_advanced_controls(self, panel):
        """Setup advanced controls demo"""
        y = 20
        
        # Modal Dialog
        modal_label = Label(20, y, "Modal Dialog:")
        panel.add_child(modal_label)
        
        def show_modal():
            dialog = ConfirmDialog("Confirmation",
                                 "Do you want to proceed?",
                                 lambda: print("Confirmed!"),
                                 lambda: print("Cancelled!"))
            dialog.show()
            
        modal_button = Button(20, y + 30, 200, 40, "Show Dialog")
        modal_button.on_click = show_modal
        panel.add_child(modal_button)
        
        # Menu
        y += 80
        menu_label = Label(20, y, "Dropdown Menu:")
        panel.add_child(menu_label)
        
        menu_items = [
            MenuItem("File", submenu=[
                MenuItem("New", lambda: print("New")),
                MenuItem("Open", lambda: print("Open")),
                MenuItem("Save", lambda: print("Save"))
            ]),
            MenuItem("Edit", submenu=[
                MenuItem("Cut", lambda: print("Cut")),
                MenuItem("Copy", lambda: print("Copy")),
                MenuItem("Paste", lambda: print("Paste"))
            ])
        ]
        
        self.menu = Menu(20, y + 30, menu_items)
        panel.add_child(self.menu)
        
        menu_button = Button(20, y + 30, 200, 40, "Show Menu")
        menu_button.on_click = self.menu.show
        panel.add_child(menu_button)
        
        # Titled Panel with ScrollView
        y += 80
        panel_width = 700
        panel_height = 300
        
        self.scroll_panel = TitledPanel(20, y, panel_width, panel_height,
                                      "Scrollable Content")
        panel.add_child(self.scroll_panel)
        
        # Add scrollview with content
        scroll_view = ScrollView(10, 10, panel_width - 20, panel_height - 50)
        self.scroll_panel.add_child(scroll_view)
        
        # Add lots of content to demonstrate scrolling
        for i in range(20):
            label = Label(10, i * 30, f"Scrollable content line {i + 1}")
            scroll_view.add_child(label)
    
    def _setup_data_display(self, panel):
        """Setup data display demo"""
        y = 20
        
        # Grid
        grid_label = Label(20, y, "Data Grid:")
        panel.add_child(grid_label)
        
        columns = [
            GridColumn("ID", "id", 80),
            GridColumn("Name", "name", 200),
            GridColumn("Age", "age", 100),
            GridColumn("Email", "email", 300)
        ]
        
        self.grid = Grid(20, y + 30, 700, 200, columns)
        
        # Sample data
        data = [
            {"id": 1, "name": "John Doe", "age": 30, "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "age": 25, "email": "jane@example.com"},
            {"id": 3, "name": "Bob Johnson", "age": 35, "email": "bob@example.com"},
            {"id": 4, "name": "Alice Brown", "age": 28, "email": "alice@example.com"},
            {"id": 5, "name": "Charlie Wilson", "age": 32, "email": "charlie@example.com"}
        ]
        self.grid.set_data(data)
        panel.add_child(self.grid)
        
        # Image Demo
        y += 250
        panel_width = 300
        panel_height = 200
        
        self.image_panel = TitledPanel(20, y, panel_width, panel_height,
                                     "Image Demo")
        panel.add_child(self.image_panel)
        
        # Add image (using a colored rectangle as placeholder)
        placeholder = pygame.Surface((100, 100))
        placeholder.fill((100, 150, 200))
        
        self.image = Image(10, 10, panel_width - 20, panel_height - 50,
                          placeholder)
        self.image_panel.add_child(self.image)
    
    def update(self):
        super().update()

        # Animate progress bar
        self.progress_bar.progress = (self.progress_bar.progress + 0.001) % 1.0
        if hasattr(self, 'progress_circle'):
            self.progress_circle.progress = (self.progress_circle.progress + 0.005) % 1.0
        
    def render(self, screen: pygame.Surface):
        """Render scene"""
        if not self._is_loaded:
            self._render_loading_screen(screen)
            return

        # Fill background
        screen.fill((240, 240, 240))  # Light gray background
        
        # Render entities
        for entity in self.get_entities_by_group("ui"):
            if entity.visible:
                entity.render(screen)
