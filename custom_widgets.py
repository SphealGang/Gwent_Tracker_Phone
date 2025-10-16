from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.popup import Popup 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
import os
from kivy.resources import resource_find
from kivy.utils import platform

class ClickableImage(ButtonBehavior, Image):
    def __init__(self, action=None, action_args = (), **kwargs):
        super().__init__(**kwargs)
        self.action = action
        self.action_args = action_args

    def on_press(self):
        if self.action:
            self.action(self, *self.action_args)

class UnitCard(ButtonBehavior, Image):
    def __init__(self, is_hero, power, special_effect, name, image_path,delete_card_function, delete_card_function_args = (),**kwargs):
        super().__init__(**kwargs)
        self.is_hero = True if is_hero == 1 else False
        self.power = power
        self.special_effect = special_effect
        self.name = name
        self.image_path = image_path
        self.delete_card_function = delete_card_function
        self.delete_card_function_args = delete_card_function_args

        self.popup_content  = BoxLayout(orientation = 'vertical')

        self.popup = Popup(
            title = 'Card details',
            size_hint=(0.75, 0.75),
            content = self.popup_content,
            separator_color=[255/255, 215/255, 0/255, 1],
            background='',
            background_color=[45/255, 30/255, 20/255, 1],
            title_size = '25sp'
        )
        
        card_image = Image(
            source = self.image_path,
            )
        self.popup_content.add_widget(card_image)
        
        button_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=180  # or any fixed value you prefer
        )
        self.popup_content.add_widget(button_layout)

        delete_button = Button(
            text = 'Delete card',
            background_normal='',
            font_size = 24,
            background_color=[25/255, 17/255, 10/255, 1],
        )
        button_layout.add_widget(delete_button)
        delete_button.bind(on_press=lambda instance: self.delete_card_function(self, *self.delete_card_function_args))

        close_button = Button(
            text = 'Close',
            background_normal='',
            font_size = 24,
            background_color=[25/255, 17/255, 10/255, 1],
            )
        close_button.bind(on_press = self.popup.dismiss)
        button_layout.add_widget(close_button)

    def on_press(self):
        self.popup.open()


# def get_item_path(file):
#     file_name = file.split('\\')[-1]
#     # print(file_name)

#     if platform == 'android':
#         from android.storage import app_storage_path # type: ignore
#         item_path = os.path.join(app_storage_path(), file_name)
#     else:
#         item_path = os.path.join(os.path.dirname(__file__), file_name)

#     return item_path