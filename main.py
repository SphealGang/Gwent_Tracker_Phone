from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
# from kivy.uix.relativelayout import RelativeLayout
# from kivy.uix.floatlayout import FloatLayout
# from kivy.uix.button import Button
from kivy.uix.label import Label
# from kivy.uix.popup import Popup 
# from kivy.uix.togglebutton import ToggleButton
# from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
# from kivy.utils import platform
from kivy.resources import resource_find
from kivy.core.image import Image as CoreImage
    
from custom_widgets import *
from functions import *



class Unit():
    def __init__(self,name,power,is_hero,special_effect):
        self.name = name
        self.power = power
        self.is_hero = is_hero
        self.special_effect = special_effect

class Handler(BoxLayout):
    def __init__(self,type,update_score_function, **kwargs):
        super().__init__(orientation='horizontal', size_hint=(1, 0.30), **kwargs)

        self.unit_list = []
        self.faction_power = 0

        self.weather_status = False
        self.commander_horn_status = False
        self.type = type

        handler_button_size_hint = (0.25,1)

        self.add_card_button = ClickableImage(
            source=resource_find("card_back.png"),
            action=lambda instance: add_card(
                type,
                self.card_view,
                self.unit_list,
                self,
                self.weather_status,
                self.commander_horn_status,
                update_score_function), 
            size_hint = handler_button_size_hint,
            mipmap=True,
            width = 50,
            allow_stretch=False,
            keep_ratio=True
        )

        # print(self.add_card_button.size)
        # print(Window.size)

        self.add_widget(self.add_card_button)
        self.height = self.add_card_button.height 
        
        self.battle_horn = ClickableImage(
            source = resource_find("page_45_card_2-modified.png"),
            action= lambda instace: commander_horn_effect(update_score_function,self),
            size_hint = handler_button_size_hint,
            mipmap=True,
            allow_stretch=False,
            keep_ratio=True
        )
        self.add_widget(self.battle_horn)

        self.card_scroll_view = ScrollView(
            do_scroll_x=True, 
            do_scroll_y=False, 
            bar_width = 0
            )
        self.add_widget(self.card_scroll_view)

        self.card_view = GridLayout(
            rows=1,
            size_hint_x=None,
            height = self.add_card_button.height,
            width = Window.width
            )
        
        self.card_scroll_view.add_widget(self.card_view)

        with self.canvas.before:
            Color(25/255, 17/255, 10/255, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

        self.weather_button = ClickableImage(
            source=resource_find(choose_weather_card(self.type,self.weather_status)),
            action= lambda instace: weather_effect(update_score_function,self),
            size_hint = handler_button_size_hint,
            mipmap=True,
            allow_stretch=False,
            keep_ratio=True
        )
        self.add_widget(self.weather_button)

    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

class PlayerWidget(BoxLayout):
    def __init__(self,top, **kwargs):
        super().__init__(orientation='vertical', spacing=5, size_hint = (1,0.5), **kwargs)

        def update_score():
            total = close_combat_handler.faction_power + ranged_combat_handler.faction_power + siege_handler.faction_power
            self.score_label.text = str(total)

        self.total_power = 0

        self.score_label = Label(
            text = '0',
            size_hint = (1, None),
            height = 40,
            font_size = 30
            )

        close_combat_handler = Handler('Close Combat',update_score)
        ranged_combat_handler = Handler('Ranged Combat',update_score)
        siege_handler = Handler('Siege',update_score)

        if top:
            self.add_widget(self.score_label)
        self.add_widget(close_combat_handler)
        self.add_widget(ranged_combat_handler)
        self.add_widget(siege_handler)
        if not top:
            self.add_widget(self.score_label)


class MainApp(App):
    def build(self):
        root = BoxLayout(
            orientation = 'vertical',
            )
        
        with root.canvas.before:
            Color(45/255, 30/255, 20/255, 1)
            self.rect = Rectangle(size=Window.size, pos=root.pos)

        Window.bind(on_resize=self.on_window_resize)

        def update_rect(instance, value):
            self.rect.size = instance.size
            self.rect.pos = instance.pos

        root.bind(size=update_rect, pos=update_rect)
        
        
        root.add_widget(PlayerWidget(top=False))
        root.add_widget(PlayerWidget(top=True))
        
        preload_image = [
        "Weather_Cards/page_1_card_7.png",
        "Weather_Cards/page_3_card_2.png",
        "Weather_Cards/page_1_card_1.png",
        "page_45_card_2.png",
        ]

        for x in preload_image:
            path = resource_find(x)
            if path:
                CoreImage(path).texture


        return root

    def on_window_resize(self, window, width, height):
        self.rect.size = (width, height)

if __name__ == "__main__":
    MainApp().run()