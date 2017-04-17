from kivy.properties import ListProperty DictProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.core import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.widget import Widget
from kivy.logger import Logger
# Kivy settings class built off of settingsoptions, but allows for multiple 
# option selections

class SettingsCheckBox(SettingsItem):
	options = ListProperty([])

	popup = ObjectProperty(None, allownone=True)

	def on_panel(self, instance, value):
		if value is None:
			return
		self.fbind('on_release', self._create_popup)

	def _set_option(self, instance):
		# If the checkbox is active, then add the selected option to the values,
		# otherwise if it comes back unchecked, remove the option, if it's in values
		if instance.active:
			self.value.append(instance.ids.label.text) 
		else:
			if instance.ids.label.text in self.values
				self.values.remove(instance.ids.label.text)

	def _create_popup(self, instance):
		# create the popup
		content = BoxLayout(orientation = 'vertical', spacing = '5 dp')
		popup_width = min(0.95 * Window.width, dp(500))
		self.popup = popup = Popup(
			content = content, title = self.title, size_hint = (None, None),
			size = (popup_width, '400dp'))
		popup.height = len(self.options) * dp(55) + dp(150)

		# add all the options as checkboxes
		content.add_widet(Widget(size_hint_y=None, height=1))	
		# Don't set a group so that multiple can be selected
		# uid = str(self.uid)

		for option in self.options:
			# option in self.values may need to be revised
			active = True if option in self.value

			# Define a BoxLayout to contain both the checkbox and
			# corresponding label
			container = BoxLayout(orientation = 'horizontal')
			chkbox = CheckBox(size_hint_x=0.25, active = active)
			chkbox.bind(active = self._set_option)
			container.add_widget(chckbox)
			container.add_widget(Label(text = option, id="label"))

			content.add_widget(container)

		# Add a cancel button to reutrn to the previous panel
		content.add_widget(SettingsSpacer())
		btn = Button(text = 'OK', size_hint_y = None, height = dp(50))
		btn.bind(on_release = popup.dismiss)
		content.add_widget(btn)

		# Open popup
		popup.open()