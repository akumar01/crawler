from kivy.uix.layout import Layout
from kivy.properties import (NumericProperty, OptionProperty, 
							ListProperty,
							VariableListProperty, 
							ReferenceListProperty)
from math import floor
from operator import add
import pdb

class TileLayout(Layout):

	# Spacing between children  in the x and y directions
	spacing = ListProperty([0, 0])

	# Spacing between layout and its children
	# [padding_left, padding_top, padding_right, padding_bottom]
	# or:
	# [padding_horizontal, padding_vertical]
	# or:
	# [padding]
	padding = VariableListProperty([0, 0, 0, 0])

	# Orientation specifies which dimension to constrain.
	# A 'vertical' orientation means that the tiling will be 
	# constrained in the horiztontal direction such that we fill
	# left to right up to the available width, but let the tiles
	# flow down vertically as far as we need. This will thus
	# probably require a vertical scrollview. In a horizontal 
	# orientation, we constrain the height of the tiling, but let it
	# flow arbitrarily in the horizontal direction, thus probably 
	# requiring a horizontal scroll view. 
	orientation = OptionProperty('lr-tb', options=(
	'lr-tb', 'tb-lr'))

	minimum_height = NumericProperty(0)


	# The target dimensions (target_dim) guides resizing of tiles along the
	# constrained dimension. Space is maximially filled by tiles and they all have
	# the same dimensions along the constrained direction that is as close as possible
	# to the target dim
	target_dim = NumericProperty(0)


	def __init__(self, **kwargs):
		super(TileLayout, self).__init__(**kwargs)
		fbind = self.fbind
		update = self._trigger_layout
		fbind('spacing', update)
		fbind('padding', update)
		fbind('children', update)
		fbind('orientation', update)
		fbind('parent', update)
		fbind('size', update)
		fbind('pos', update)

	def do_layout(self, *largs):
		len_children = len(self.children)
		if len_children == 0:
			return
		selfx = self.x
		selfy = self.y
		selfw = self.width
		selfh = self.height
		padding_left = self.padding[0]
		padding_top = self.padding[1]
		padding_right = self.padding[2]
		padding_bottom = self.padding[3]
		spacing_x = self.spacing[0]
		spacing_y = self.spacing[1]
		orientation = self.orientation
		padding_x = padding_left + padding_right
		padding_y = padding_top + padding_bottom

		# Calculate maximum space available for use:
		minimum_size_x = padding_x + spacing_x * (len_children - 1)
		minimum_size_y = padding_y + spacing_y * (len_children - 1)



		# If the orientation is lr-tb, then the widths of children elements are set
		# by the layout to maximally fill the available width with all widths conforming
		# as closely as possible to the target_dim
		if self.orientation == 'lr-tb':
			# Coordinate systems are (0,0) at the bottom left corner. We want to add widgets
			# starting from the top right corner moving down.
			x = selfx + padding_left
			y = selfy + selfh - padding_top

			available_width = selfw - minimum_size_x

			if available_width < 0:
				self.width = minimum_size_x
				selfw = self.width

			available_width = selfw - minimum_size_x

			n_tiles_across = max(1, int(floor(available_width/self.target_dim)))

			tile_width = available_width/n_tiles_across

			# Now that we know how many columns of tiles we will have, let's
			# determine how many tiles we will stack in each columm. The criteria
			# used is not to stack numbers evenly but instead to stack heights
			# evenly. 

			total_height_needed  = 0
			for child in self.children:
				total_height_needed += child.height

			avg_height = float(total_height_needed)/n_tiles_across
			
			# Divide the children into stacks of equal height
			
			# Which stack should the child be added to?
			stack = [0] * len_children

			# stack_ind goes from 0 to n_tiles_across - 1
			stack_ind = 0

			# How high is each stack?
			stack_heights = [0] * n_tiles_across

			# How many tiles are in each stack?
			stack_occupancy = [0] * n_tiles_across

			# We want to assign each child to a stack. The reason this is
			# not so straightforward is that we want to add entries left 
			# to right, but it is the vertical height we want to take care of.
			# Thus, do the following: iterate through children left to right and
			# as long as the the current stack height does not exceed the average 
			# height, add it. If the current stack is filled up, then shift one 
			# over until we find the first available stack.

			for i in range(len_children):
				try:
					if stack_heights[stack_ind] <= avg_height:
						stack[i] = stack_ind
						stack_heights[stack_ind] += self.children[i].height
						stack_occupancy[stack_ind] += 1
					else:
					# If the stack is full, proceed to the next one.
						stack_ind += 1
						stack_ind = stack_ind % n_tiles_across
						# Keep moving over stacks until we find a free one:
						while stack_heights[stack_ind] > avg_height:
							stack_ind += 1
						# Assign this child to that 
						stack[i] = stack_ind % n_tiles_across
						stack_heights[stack_ind] += self.children[i].height
						stack_occupancy[stack_ind] += 1
				except:
					pdb.set_trace()

				stack_ind += 1
				stack_ind = stack_ind % n_tiles_across

			tile_y_end = [y] * n_tiles_across


			# As the orientation suggests, add tiles left to right (inner loop), top
			# to bottom (outer loop). Do this by just iterating through the children.
			# We know from above which stack they belong to.
			for i in range(len_children):
				self.children[i].width = tile_width
				self.children[i].x = x + stack[i] * (spacing_x + tile_width)

				tile_y_end[stack[i]] = tile_y_end[stack[i]] - self.children[i].height - spacing_y
				self.children[i].y = tile_y_end[stack[i]]

			# We can update the minimum_height now. It is highly recommended that we set
			# height of this layout to self.minimum_height when in use.

			# In principle we just be able to take max(stack_heights), however there 
			# may be strange cases where the spacing is so large that another column
			# actually ends up being the largest.

			spacing_heights = [spacing_y * (x - 1) for x in stack_occupancy]

			total_height = map(add, stack_heights, spacing_heights)

			self.minimum_height = padding_y + max(total_height)


		# Note: have not implemented the other orientation. Don't currently see a 
		# compelling reason to do so.


