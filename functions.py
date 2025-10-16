from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup 
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.resources import resource_find
import sqlite3
import threading
from itertools import groupby


from custom_widgets import *

def add_card(type,widget_surface,unit_list,handler,weather_status,commander_horn_status,update_score_function):
    popup_content = BoxLayout(orientation = 'vertical')

    popup = Popup(
        title = 'Add card',
        content = popup_content,
        size_hint=(0.75, 0.75),
        separator_color=[255/255, 215/255, 0/255, 1],
        background='',
        background_color=[45/255, 30/255, 20/255, 1],
        title_size = '25sp'
    )
    popup.open()

    search_bar = TextInput(
        size_hint = (1, None),
        height = 70,
        multiline = False,
        font_size = 50
    )
    popup_content.add_widget(search_bar)

    card_preview = ScrollView(
        do_scroll_x=True, 
        do_scroll_y=False, 
        bar_width = 0,
        )
    popup_content.add_widget(card_preview)
    
    scroll_surface = GridLayout(rows=1,size_hint_x=None)
    scroll_surface.bind(minimum_width=scroll_surface.setter('width'))
    card_preview.add_widget(scroll_surface)

    search_bar.bind(text=lambda instance, value: search(instance, value, scroll_surface,type,widget_surface,unit_list,handler,weather_status,commander_horn_status,update_score_function))

    close_button = Button(
        text = 'Close',
        size_hint=(1, None),
        height = 150,
        background_normal='',
        font_size = 24,
        background_color=[25/255, 17/255, 10/255, 1],
        )
    close_button.bind(on_press = popup.dismiss)
    popup_content.add_widget(close_button)

def send_card(instance,card,widget_surface,unit_list,handler,weather_status,commander_horn_status,update_score_function):
    final_card = UnitCard(
        source=resource_find(card[6]),
        is_hero=card[4],
        power=card[3],
        special_effect = card[5],
        name=card[1],
        image_path=card[6],
        delete_card_function=delete_card,
        delete_card_function_args=(handler, update_score_function),
        size_hint = (None,1),
        width = widget_surface.height * 0.6,
        mipmap=True,
        allow_stretch=False,
        keep_ratio=True,
        # action=lambda instance: print(handler.faction_power)
        )
    widget_surface.add_widget(final_card)
    unit_list.append(final_card)
    handler.faction_power = calculate_total(unit_list,weather_status,commander_horn_status)
    update_score_function()


def calculate_total(unit_list,weather_status,commander_horn_status):
    morale_boost_units = [x for x in unit_list if x.special_effect == 'Morale Boost']

    tight_bond_units = [x for x in unit_list if x.special_effect == 'Tight Bond']
    tight_bond_units.sort(key=lambda x : x.special_effect)
    
    tight_bond_units_sorted = [list(group) for key,group in groupby(tight_bond_units, key=lambda x: x.name)]
    # print(tight_bond_units_sorted)

    commander_horn_unit = [x for x in unit_list if x.name == 'Dandelion']

    non_hero_units = [x for x in unit_list if not x.is_hero and x.special_effect == 'none' and x.name != 'Decoy']

    hero_total = sum(x.power for x in unit_list if x.is_hero)
    non_hero_total = sum(x.power for x in non_hero_units)
    

    if weather_status:
        non_hero_total = 1 * len(non_hero_units)

    if len(tight_bond_units_sorted) >= 1:
        for x in tight_bond_units_sorted:
            if len(x) >= 2:
                # print("### WE HAVE A PAIR###")
                if not weather_status:
                    non_hero_total += (sum(y.power for y in x) * 2)
                else:
                    non_hero_total += (len(x) * 2)
            else:
                # print("### WE HAVE A SINGLE UNIT###")
                if not weather_status:
                    non_hero_total += (sum(y.power for y in x))
                else:
                    non_hero_total += (len(x))



    if morale_boost_units:
        for x in morale_boost_units:
            non_hero_total += 1 * (len(non_hero_units) - 1)

    if commander_horn_unit:
        non_hero_total *= 2

    if commander_horn_status:
        non_hero_total *= 2

    return hero_total + non_hero_total
    # print(final_total)


def search(instance,value,surface,type,widget_surface,unit_list,handler,weather_status,commander_horn_status,update_score_function):
    surface.clear_widgets()

    # loading_wheel(root=surface)

    threading.Thread(target=fetch_data, args=(value,surface,type,widget_surface,unit_list,handler,weather_status,commander_horn_status,update_score_function)).start()


def fetch_data(value,surface,type,widget_surface,unit_list,handler,weather_status,commander_horn_status,update_score_function):
    result = []
    # print('Search started')

    if len(value) >= 1:
        with sqlite3.connect(resource_find("card_db.db")) as db:
            cursor = db.cursor()
            command = f"SELECT * FROM Cards WHERE Name LIKE '{value}%' AND Type LIKE '%{type}%'"
            cursor.execute(command)
            result = cursor.fetchall()

    # print('Search finished')
    # print('Display started')

    Clock.schedule_once(lambda dt: display_data(result, surface, widget_surface,unit_list,handler,weather_status,commander_horn_status,update_score_function))

def display_data(result,surface,widget_surface,unit_list,handler,weather_status,commander_horn_status,update_score_function):
    surface.clear_widgets()

    for i in result:
        # print(i)
        x = ClickableImage(
            action=lambda instance, card=i: send_card(instance,card=card,widget_surface=widget_surface,unit_list=unit_list,handler=handler,weather_status=weather_status,commander_horn_status=commander_horn_status,update_score_function=update_score_function),
            source = resource_find(i[6]),
            size_hint_x=None,
            width=550,
            )
        surface.add_widget(x)  

    # print('Display Finished')      

# def loading_wheel(root):
#     loading_icon = Image(
#         source=r"/storage/emulated/0/Gwent_tracker_Phone/witcher_loading_icon-removebg-preview.png",
#         size_hint=(None,None),
#         size = (400,400)
#         )
#     root.add_widget(loading_icon)
        
def choose_weather_card(faction,weather):
    if faction == 'Close Combat':
        if weather:
            return "Weather_Cards/page_1_card_7.png"
        else:
            return "Weather_Cards/page_1_card_7-modified.png"

    elif faction == "Ranged Combat":
        if weather:
            return "Weather_Cards/page_3_card_2.png"
        else:
            return "Weather_Cards/page_3_card_2-modified.png"
    else:
        if weather:
            return "Weather_Cards/page_1_card_1.png"
        else:
            return "Weather_Cards/page_1_card_1-modified.png"


def weather_effect(update_score_function,handler):
    handler.weather_status = not handler.weather_status
        
    # handler.weather_button.source = r""
    handler.weather_button.source = choose_weather_card(handler.type,handler.weather_status)


    handler.faction_power = calculate_total(handler.unit_list,handler.weather_status,handler.commander_horn_status)
    
    update_score_function()

def commander_horn_effect(update_score_function,handler):
    handler.commander_horn_status = not handler.commander_horn_status

    if not handler.commander_horn_status:
        handler.battle_horn.source = resource_find("page_45_card_2-modified.png")
    else:
        handler.battle_horn.source = resource_find("page_45_card_2.png")
        

    handler.faction_power = calculate_total(handler.unit_list,handler.weather_status,handler.commander_horn_status)
    
    update_score_function()

def delete_card(card,handler,update_score_function):
    handler.unit_list.remove(card)

    handler.faction_power = calculate_total(handler.unit_list,handler.weather_status,handler.commander_horn_status)

    update_score_function()
    card.popup.dismiss()
    handler.card_view.remove_widget(card)


        