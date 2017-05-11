from kivy.app import App
from tilelayout import TileLayout
from kivy.uix.button import Button
import random




class TileLayoutTest(TileLayout):

	def __init__(self, **kwargs):
		super(TileLayoutTest, self).__init__(**kwargs)
		for i in range(30):
			height = random.randint(50, 200)
			self.add_widget(Button(text='height %d' % height, size_hint_y = None,
									height = height))

class TileTestApp(App):

	def build(self):
		pass


if __name__ == "__main__":
	TileTestApp().run()