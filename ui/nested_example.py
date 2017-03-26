from kivy.app import App
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

class HBoxWidget(Widget):
    def __init__(self, **kwargs):
        super(HBoxWidget, self).__init__(**kwargs)

class VBoxWidget(Widget):
    def __init__(self, **kwargs):
        super(VBoxWidget, self).__init__(**kwargs)
        
class ContainerGrid(GridLayout):
    def __init__(self, **kwargs):
        super(ContainerGrid, self).__init__(**kwargs)

class Test2App(App):
    def build(self):
        return ContainerGrid() 
     
if __name__ == '__main__':
    Test2App().run()