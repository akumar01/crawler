from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
import json_lines
from ..agg.json import read_json
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout

class TableHeader(Label):
    pass


class PlayerRecord(Label):
    pass

class MyGrid(GridLayout):

    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)
        self.fetch_data()
        self.display_scores()

    def fetch_data(self):
        self.data = read_json.read_data()

    def display_scores(self):
        self.clear_widgets()
        for i in xrange(len(self.data)):
            if i < 1:
                row = self.create_header(i)
            else:
                row = self.create_player_info(i)
            for item in row:
                self.add_widget(item)

    def create_header(self, i):
        first_column = TableHeader(text='Title')
        second_column = TableHeader(text='Author(s)')
        third_column = TableHeader(text='Tags')
        return [first_column, second_column, third_column]

    def create_player_info(self, i):
        first_column = PlayerRecord(text=self.data[i]['title'])
        authors = ''
        if(len(self.data[i]["authors"]) > 1):
            authors += self.data[i]["authors"][0]
            for author in self.data[i]["authors"][1:]:
                authors += ", %s" % author
        elif(len(self.data[i]["authors"]) == 1):
            authors = self.data[i]["authors"][0]
        second_column = PlayerRecord(text=authors)
        third_column = PlayerRecord(text=self.data[i]['tags'])
        return [first_column, second_column, third_column]


class TopRow(Widget):
    def __init__(self, **kwargs):
        super(TopRow, self).__init__(**kwargs)

class AnchorContainer(BoxLayout):
    def __init__(self, **kwargs):
        super(AnchorContainer, self).__init__(**kwargs)

class ContainerGrid(GridLayout):
    def __init__(self, **kwargs):
        super(ContainerGrid, self).__init__(**kwargs)

class Test(App):
    def build(self):
        return ContainerGrid()

if __name__  == "__main__":
    Test().run()
