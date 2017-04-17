from kivy.garden.cefpython import CefBrowser, cefpython
from kivy.app import App

class CefBrowserApp(App):
    def build(self):
        return CefBrowser(start_url='Kivy_ Cross-platform Python Framework for NUI Development.html')

CefBrowserApp().run()

cefpython.Shutdown()