from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import nmax
from kivy.properties import (NumericProperty, ReferenceListProperty,
                             VariableListProperty)
import pdb

# Create a box layout that supports the minimum_size

class DynamicBoxLayout(BoxLayout):

	# To use the minimum_size property, be sure to set the size_hints of the children
	# along the relevant dimension to None. This way, we can let the child widgets take
	# the height/width they natively need, and resize the boxlayoutto match.

	minimum_height = NumericProperty(0)

	minimum_width = NumericProperty(0)

	minimum_size = ReferenceListProperty(minimum_width, minimum_height)

	def __init__(self, **kwargs):
		super(DynamicBoxLayout, self).__init__(**kwargs)

	def update_minimum_size(self, *largs):
		children = self.children

		# if children[2].height != 0:
		# 	pdb.set_trace()

		len_children = len(children)

		children_width = [None] * len(children)
		children_height = [None] * len(children)

		if children[3].height > 200:
			pdb.set_trace()

		# Calculate minimum height and/or width. Unlike the GridLayout, there
		# is really only one relevant quantity, depending on the orientation. If 
		# the orientation is vertical, then we are interested in the minimum_height,
		# otherwise if it is horizontal, we are interested in the minimum_width. The
		# other dimension is trivial and fixed. We set it to self.(width/height) 

		width = 0
		height = 0

		for i, child in enumerate(children):
			if child.width is not None:
				width += child.width
			if child.height is not None:
				height += child.height

		# Begin add padding + spacing
		padding_x = self.padding[0] + self.padding[2]
		padding_y = self.padding[1] + self.padding[3]

		if self.orientation == 'horizontal':
			width += padding_x + self.spacing * (len(children) - 1)
			height = self.height
		elif self.orientation == 'vertical':
			width = self.width 
			height += padding_y + self.spacing * (len(children) - 1)

		self.minimum_size = (width, height)		

	# Override do_layout so that we update the minimum_size first
	def do_layout(self, *largs):
		self.update_minimum_size()

		# Continue as usual otherwise. Remember, if there are size_hints 
		# then they will be taken into account by BoxLayout and the desired
		# effect will not occur
		super(DynamicBoxLayout, self).do_layout(*largs)
