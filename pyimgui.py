# -*- coding: utf-8 -*-
import datetime
import time, threading
import glfw
import imgui
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer
import math
import re


class Person:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

# Types
#   "DRAW": 
#       "Undo": Remove circle from list at index
#       "Redo": Add circle to list size x, y and radius radius
#   "RESIZE":
#       "Undo": Set size to old_r
#       "Redo": Set size to r

class CircleEvent:
    def __init__(self, action, index, radius = 0, old_radius = 0, x = 0, y = 0):
        self.action = action
        self.index = index
        self.radius = radius
        self.x = x
        self.y = y
        self.old_radius = old_radius
        self.next = None
        self.prev = None

class CircleList:
    def __init__(self):
        self.undo_head = CircleEvent("HEAD", -1)
        self.undo_tail = self.undo_head

    def add_event(self, action, index, radius = 0, old_radius = 0, x = 0, y = 0):
        e = CircleEvent(action, index, radius = radius, old_radius = old_radius, x = x, y = y)
    
        self.undo_tail.next = e
        e.prev = self.undo_tail
        self.undo_tail = self.undo_tail.next
    
    def undo(self):
        if self.undo_tail == self.undo_head:
            return None
        
        ret = self.undo_tail
        self.undo_tail = self.undo_tail.prev
        return ret
    
    def redo(self):
        if self.undo_tail.next is None:
            return None

        self.undo_tail = self.undo_tail.next
        return self.undo_tail

class Color:
    def __init__(self, label, r, g, b):
        self.label = label
        self.r = r
        self.g = g
        self.b = b

def validate_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, "%m.%d.%Y")
    except ValueError:
        return None

def calculate_cell_sum(eq, cells):
    res = re.search("\(([A-Z][0-9]+):([A-Z][0-9]+)\)", eq)
    c1 = res.group(1)
    c2 = res.group(2)

    start_j = ord(c1[0]) - ord('A')
    start_i = int(c1[1:])

    end_j = ord(c2[0]) - ord('A')
    end_i = int(c2[1:])

    s = 0
    for i in range(start_i, end_i + 1):
        for j in range(start_j, end_j + 1):
            try:
                s += int(cells[i][j]["val"])
            except:
                s += 0

    return s

def main():
    imgui.create_context()
    window = impl_glfw_init()
    impl = GlfwRenderer(window)

    # Counter Variables
    counter = 0

    # Temperature Converter 
    tempC = 0
    tempF = 32

    # Flight Booker Variables
    flight_current = 0
    start_date = "01.01.1970"
    end_date = start_date

    # CRUD Variables
    crud_selected = [False, False, False]
    crud_names = [Person("Steven", "Tyler"), Person("Tom", "Hamilton"), Person("Joey", "Kramer")]
    crud_filter_text = ""
    crud_first_name_text = ""
    crud_last_name_text = ""

    # MVP Variables
    show_mvp_window = False

    # Circle Variables
    circle_list = []
    colored_circle = None
    colored_circle_size = 0
    show_circle_slider = False
    undo_list = CircleList()

    # Timer Variables
    start_time = time.perf_counter()
    timer_length = 30

    # Cells Variables
    cells = []
    ROWS = 100
    COLS = 26
    sum_reg = re.compile("SUM\([A-Z][0-9]+:[A-Z][0-9]+\)")

    # CNH Variables
    w = 600
    h = 300
    name = ""
    health = 100
    color = None
    color_ind = 0
    button_colors = [(0, 0, 0), (0, 0, 0), (0, 0, 0)]
    click1 = False
    click2 = False
    click3 = False
    colors = [
        Color("White", 255, 255, 255),
        Color("Black", 0, 0, 0),
        Color("Air Force Blue (Raf)", 93, 138, 168),
        Color("Air Force Blue (Usaf)", 0, 48, 143),
        Color("Air Superiority Blue", 114, 160, 193),
        Color("Alabama Crimson", 163, 38, 56),
        Color("Alice Blue", 240, 248, 255),
        Color("Alizarin Crimson", 227, 38, 54),
        Color("Alloy Orange", 196, 98, 16),
        Color("Almond", 239, 222, 205),
        Color("Amaranth", 229, 43, 80),
        Color("Amber", 255, 191, 0),
        Color("Amber (Sae/Ece)", 255, 126, 0),
        Color("American Rose", 255, 3, 62),
        Color("Amethyst", 153, 102, 204),
        Color("Android Green", 164, 198, 57),
        Color("Anti-Flash White", 242, 243, 244),
        Color("Antique Brass", 205, 149, 117),
        Color("Antique Fuchsia", 145, 92, 131),
        Color("Antique Ruby", 132, 27, 45),
        Color("Antique White", 250, 235, 215),
        Color("Ao (English)", 0, 128, 0),
        Color("Apple Green", 141, 182, 0),
        Color("Apricot", 251, 206, 177),
        Color("Aqua", 0, 255, 255),
        Color("Aquamarine", 127, 255, 212),
        Color("Army Green", 75, 83, 32),
        Color("Arsenic", 59, 68, 75),
        Color("Arylide Yellow", 233, 214, 107),
        Color("Ash Grey", 178, 190, 181),
        Color("Asparagus", 135, 169, 107),
        Color("Atomic Tangerine", 255, 153, 102),
        Color("Auburn", 165, 42, 42),
        Color("Aureolin", 253, 238, 0),
        Color("Aurometalsaurus", 110, 127, 128),
        Color("Avocado", 86, 130, 3),
        Color("Azure", 0, 127, 255),
        Color("Azure Mist/Web", 240, 255, 255),
        Color("Baby Blue", 137, 207, 240),
        Color("Baby Blue Eyes", 161, 202, 241),
        Color("Baby Pink", 244, 194, 194),
        Color("Ball Blue", 33, 171, 205),
        Color("Banana Mania", 250, 231, 181),
        Color("Banana Yellow", 255, 225, 53),
        Color("Barn Red", 124, 10, 2),
        Color("Battleship Grey", 132, 132, 130),
        Color("Bazaar", 152, 119, 123),
        Color("Beau Blue", 188, 212, 230),
        Color("Beaver", 159, 129, 112),
        Color("Beige", 245, 245, 220),
        Color("Big Dip O’Ruby", 156, 37, 66),
        Color("Bisque", 255, 228, 196),
        Color("Bistre", 61, 43, 31),
        Color("Bittersweet", 254, 111, 94),
        Color("Bittersweet Shimmer", 191, 79, 81),
        Color("Black", 0, 0, 0),
        Color("Black Bean", 61, 12, 2),
        Color("Black Leather Jacket", 37, 53, 41),
        Color("Black Olive", 59, 60, 54),
        Color("Blanched Almond", 255, 235, 205),
        Color("Blast-Off Bronze", 165, 113, 100),
        Color("Bleu De France", 49, 140, 231),
        Color("Blizzard Blue", 172, 229, 238),
        Color("Blond", 250, 240, 190),
        Color("Blue", 0, 0, 255),
        Color("Blue Bell", 162, 162, 208),
        Color("Blue (Crayola)", 31, 117, 254),
        Color("Blue Gray", 102, 153, 204),
        Color("Blue-Green", 13, 152, 186),
        Color("Blue (Munsell)", 0, 147, 175),
        Color("Blue (Ncs)", 0, 135, 189),
        Color("Blue (Pigment)", 51, 51, 153),
        Color("Blue (Ryb)", 2, 71, 254),
        Color("Blue Sapphire", 18, 97, 128),
        Color("Blue-Violet", 138, 43, 226),
        Color("Blush", 222, 93, 131),
        Color("Bole", 121, 68, 59),
        Color("Bondi Blue", 0, 149, 182),
        Color("Bone", 227, 218, 201),
        Color("Boston University Red", 204, 0, 0),
        Color("Bottle Green", 0, 106, 78),
        Color("Boysenberry", 135, 50, 96),
        Color("Brandeis Blue", 0, 112, 255),
        Color("Brass", 181, 166, 66),
        Color("Brick Red", 203, 65, 84),
        Color("Bright Cerulean", 29, 172, 214),
        Color("Bright Green", 102, 255, 0),
        Color("Bright Lavender", 191, 148, 228),
        Color("Bright Maroon", 195, 33, 72),
        Color("Bright Pink", 255, 0, 127),
        Color("Bright Turquoise", 8, 232, 222),
        Color("Bright Ube", 209, 159, 232),
        Color("Brilliant Lavender", 244, 187, 255),
        Color("Brilliant Rose", 255, 85, 163),
        Color("Brink Pink", 251, 96, 127),
        Color("British Racing Green", 0, 66, 37),
        Color("Bronze", 205, 127, 50),
        Color("Brown (Traditional)", 150, 75, 0),
        Color("Brown (Web)", 165, 42, 42),
        Color("Bubble Gum", 255, 193, 204),
        Color("Bubbles", 231, 254, 255),
        Color("Buff", 240, 220, 130),
        Color("Bulgarian Rose", 72, 6, 7),
        Color("Burgundy", 128, 0, 32),
        Color("Burlywood", 222, 184, 135),
        Color("Burnt Orange", 204, 85, 0),
        Color("Burnt Sienna", 233, 116, 81),
        Color("Burnt Umber", 138, 51, 36),
        Color("Byzantine", 189, 51, 164),
        Color("Byzantium", 112, 41, 99),
        Color("Cadet", 83, 104, 114),
        Color("Cadet Blue", 95, 158, 160),
        Color("Cadet Grey", 145, 163, 176),
        Color("Cadmium Green", 0, 107, 60),
        Color("Cadmium Orange", 237, 135, 45),
        Color("Cadmium Red", 227, 0, 34),
        Color("Cadmium Yellow", 255, 246, 0),
        Color("Café Au Lait", 166, 123, 91),
        Color("Café Noir", 75, 54, 33),
        Color("Cal Poly Green", 30, 77, 43),
        Color("Cambridge Blue", 163, 193, 173),
        Color("Camel", 193, 154, 107),
        Color("Cameo Pink", 239, 187, 204),
        Color("Camouflage Green", 120, 134, 107),
        Color("Canary Yellow", 255, 239, 0),
        Color("Candy Apple Red", 255, 8, 0),
        Color("Candy Pink", 228, 113, 122),
        Color("Capri", 0, 191, 255),
        Color("Caput Mortuum", 89, 39, 32),
        Color("Cardinal", 196, 30, 58),
        Color("Caribbean Green", 0, 204, 153),
        Color("Carmine", 150, 0, 24),
        Color("Carmine (M&P)", 215, 0, 64),
        Color("Carmine Pink", 235, 76, 66),
        Color("Carmine Red", 255, 0, 56),
        Color("Carnation Pink", 255, 166, 201),
        Color("Carnelian", 179, 27, 27),
        Color("Carolina Blue", 153, 186, 221),
        Color("Carrot Orange", 237, 145, 33),
        Color("Catalina Blue", 6, 42, 120),
        Color("Ceil", 146, 161, 207),
        Color("Celadon", 172, 225, 175),
        Color("Celadon Blue", 0, 123, 167),
        Color("Celadon Green", 47, 132, 124),
        Color("Celeste (Colour)", 178, 255, 255),
        Color("Celestial Blue", 73, 151, 208),
        Color("Cerise", 222, 49, 99),
        Color("Cerise Pink", 236, 59, 131),
        Color("Cerulean", 0, 123, 167),
        Color("Cerulean Blue", 42, 82, 190),
        Color("Cerulean Frost", 109, 155, 195),
        Color("Cg Blue", 0, 122, 165),
        Color("Cg Red", 224, 60, 49),
        Color("Chamoisee", 160, 120, 90),
        Color("Champagne", 250, 214, 165),
        Color("Charcoal", 54, 69, 79),
        Color("Charm Pink", 230, 143, 172),
        Color("Chartreuse (Traditional)", 223, 255, 0),
        Color("Chartreuse (Web)", 127, 255, 0),
        Color("Cherry", 222, 49, 99),
        Color("Cherry Blossom Pink", 255, 183, 197),
        Color("Chestnut", 205, 92, 92),
        Color("China Pink", 222, 111, 161),
        Color("China Rose", 168, 81, 110),
        Color("Chinese Red", 170, 56, 30),
        Color("Chocolate (Traditional)", 123, 63, 0),
        Color("Chocolate (Web)", 210, 105, 30),
        Color("Chrome Yellow", 255, 167, 0),
        Color("Cinereous", 152, 129, 123),
        Color("Cinnabar", 227, 66, 52),
        Color("Cinnamon", 210, 105, 30),
        Color("Citrine", 228, 208, 10),
        Color("Classic Rose", 251, 204, 231),
        Color("Cobalt", 0, 71, 171),
        Color("Cocoa Brown", 210, 105, 30),
        Color("Coffee", 111, 78, 55),
        Color("Columbia Blue", 155, 221, 255),
        Color("Congo Pink", 248, 131, 121),
        Color("Cool Black", 0, 46, 99),
        Color("Cool Grey", 140, 146, 172),
        Color("Copper", 184, 115, 51),
        Color("Copper (Crayola)", 218, 138, 103),
        Color("Copper Penny", 173, 111, 105),
        Color("Copper Red", 203, 109, 81),
        Color("Copper Rose", 153, 102, 102),
        Color("Coquelicot", 255, 56, 0),
        Color("Coral", 255, 127, 80),
        Color("Coral Pink", 248, 131, 121),
        Color("Coral Red", 255, 64, 64),
        Color("Cordovan", 137, 63, 69),
        Color("Corn", 251, 236, 93),
        Color("Cornell Red", 179, 27, 27),
        Color("Cornflower Blue", 100, 149, 237),
        Color("Cornsilk", 255, 248, 220),
        Color("Cosmic Latte", 255, 248, 231),
        Color("Cotton Candy", 255, 188, 217),
        Color("Cream", 255, 253, 208),
        Color("Crimson", 220, 20, 60),
        Color("Crimson Glory", 190, 0, 50),
        Color("Cyan", 0, 255, 255),
        Color("Cyan (Process)", 0, 183, 235),
        Color("Daffodil", 255, 255, 49),
        Color("Dandelion", 240, 225, 48),
        Color("Dark Blue", 0, 0, 139),
        Color("Dark Brown", 101, 67, 33),
        Color("Dark Byzantium", 93, 57, 84),
        Color("Dark Candy Apple Red", 164, 0, 0),
        Color("Dark Cerulean", 8, 69, 126),
        Color("Dark Chestnut", 152, 105, 96),
        Color("Dark Coral", 205, 91, 69),
        Color("Dark Cyan", 0, 139, 139),
        Color("Dark Electric Blue", 83, 104, 120),
        Color("Dark Goldenrod", 184, 134, 11),
        Color("Dark Gray", 169, 169, 169),
        Color("Dark Green", 1, 50, 32),
        Color("Dark Imperial Blue", 0, 65, 106),
        Color("Dark Jungle Green", 26, 36, 33),
        Color("Dark Khaki", 189, 183, 107),
        Color("Dark Lava", 72, 60, 50),
        Color("Dark Lavender", 115, 79, 150),
        Color("Dark Magenta", 139, 0, 139),
        Color("Dark Midnight Blue", 0, 51, 102),
        Color("Dark Olive Green", 85, 107, 47),
        Color("Dark Orange", 255, 140, 0),
        Color("Dark Orchid", 153, 50, 204),
        Color("Dark Pastel Blue", 119, 158, 203),
        Color("Dark Pastel Green", 3, 192, 60),
        Color("Dark Pastel Purple", 150, 111, 214),
        Color("Dark Pastel Red", 194, 59, 34),
        Color("Dark Pink", 231, 84, 128),
        Color("Dark Powder Blue", 0, 51, 153),
        Color("Dark Raspberry", 135, 38, 87),
        Color("Dark Red", 139, 0, 0),
        Color("Dark Salmon", 233, 150, 122),
        Color("Dark Scarlet", 86, 3, 25),
        Color("Dark Sea Green", 143, 188, 143),
        Color("Dark Sienna", 60, 20, 20),
        Color("Dark Slate Blue", 72, 61, 139),
        Color("Dark Slate Gray", 47, 79, 79),
        Color("Dark Spring Green", 23, 114, 69),
        Color("Dark Tan", 145, 129, 81),
        Color("Dark Tangerine", 255, 168, 18),
        Color("Dark Taupe", 72, 60, 50),
        Color("Dark Terra Cotta", 204, 78, 92),
        Color("Dark Turquoise", 0, 206, 209),
        Color("Dark Violet", 148, 0, 211),
        Color("Dark Yellow", 155, 135, 12),
        Color("Dartmouth Green", 0, 112, 60),
        Color("Davy'S Grey", 85, 85, 85),
        Color("Debian Red", 215, 10, 83),
        Color("Deep Carmine", 169, 32, 62),
        Color("Deep Carmine Pink", 239, 48, 56),
        Color("Deep Carrot Orange", 233, 105, 44),
        Color("Deep Cerise", 218, 50, 135),
        Color("Deep Champagne", 250, 214, 165),
        Color("Deep Chestnut", 185, 78, 72),
        Color("Deep Coffee", 112, 66, 65),
        Color("Deep Fuchsia", 193, 84, 193),
        Color("Deep Jungle Green", 0, 75, 73),
        Color("Deep Lilac", 153, 85, 187),
        Color("Deep Magenta", 204, 0, 204),
        Color("Deep Peach", 255, 203, 164),
        Color("Deep Pink", 255, 20, 147),
        Color("Deep Ruby", 132, 63, 91),
        Color("Deep Saffron", 255, 153, 51),
        Color("Deep Sky Blue", 0, 191, 255),
        Color("Deep Tuscan Red", 102, 66, 77),
        Color("Denim", 21, 96, 189),
        Color("Desert", 193, 154, 107),
        Color("Desert Sand", 237, 201, 175),
        Color("Dim Gray", 105, 105, 105),
        Color("Dodger Blue", 30, 144, 255),
        Color("Dogwood Rose", 215, 24, 104),
        Color("Dollar Bill", 133, 187, 101),
        Color("Drab", 150, 113, 23),
        Color("Duke Blue", 0, 0, 156),
        Color("Earth Yellow", 225, 169, 95),
        Color("Ebony", 85, 93, 80),
        Color("Ecru", 194, 178, 128),
        Color("Eggplant", 97, 64, 81),
        Color("Eggshell", 240, 234, 214),
        Color("Egyptian Blue", 16, 52, 166),
        Color("Electric Blue", 125, 249, 255),
        Color("Electric Crimson", 255, 0, 63),
        Color("Electric Cyan", 0, 255, 255),
        Color("Electric Green", 0, 255, 0),
        Color("Electric Indigo", 111, 0, 255),
        Color("Electric Lavender", 244, 187, 255),
        Color("Electric Lime", 204, 255, 0),
        Color("Electric Purple", 191, 0, 255),
        Color("Electric Ultramarine", 63, 0, 255),
        Color("Electric Violet", 143, 0, 255),
        Color("Electric Yellow", 255, 255, 0),
        Color("Emerald", 80, 200, 120),
        Color("English Lavender", 180, 131, 149),
        Color("Eton Blue", 150, 200, 162),
        Color("Fallow", 193, 154, 107),
        Color("Falu Red", 128, 24, 24),
        Color("Fandango", 181, 51, 137),
        Color("Fashion Fuchsia", 244, 0, 161),
        Color("Fawn", 229, 170, 112),
        Color("Feldgrau", 77, 93, 83),
        Color("Fern Green", 79, 121, 66),
        Color("Ferrari Red", 255, 40, 0),
        Color("Field Drab", 108, 84, 30),
        Color("Fire Engine Red", 206, 32, 41),
        Color("Firebrick", 178, 34, 34),
        Color("Flame", 226, 88, 34),
        Color("Flamingo Pink", 252, 142, 172),
        Color("Flavescent", 247, 233, 142),
        Color("Flax", 238, 220, 130),
        Color("Floral White", 255, 250, 240),
        Color("Fluorescent Orange", 255, 191, 0),
        Color("Fluorescent Pink", 255, 20, 147),
        Color("Fluorescent Yellow", 204, 255, 0),
        Color("Folly", 255, 0, 79),
        Color("Forest Green (Traditional)", 1, 68, 33),
        Color("Forest Green (Web)", 34, 139, 34),
        Color("French Beige", 166, 123, 91),
        Color("French Blue", 0, 114, 187),
        Color("French Lilac", 134, 96, 142),
        Color("French Lime", 204, 255, 0),
        Color("French Raspberry", 199, 44, 72),
        Color("French Rose", 246, 74, 138),
        Color("Fuchsia", 255, 0, 255),
        Color("Fuchsia (Crayola)", 193, 84, 193),
        Color("Fuchsia Pink", 255, 119, 255),
        Color("Fuchsia Rose", 199, 67, 117),
        Color("Fulvous", 228, 132, 0),
        Color("Fuzzy Wuzzy", 204, 102, 102),
        Color("Gainsboro", 220, 220, 220),
        Color("Gamboge", 228, 155, 15),
        Color("Ghost White", 248, 248, 255),
        Color("Ginger", 176, 101, 0),
        Color("Glaucous", 96, 130, 182),
        Color("Glitter", 230, 232, 250),
        Color("Gold (Metallic)", 212, 175, 55),
        Color("Gold (Web) (Golden)", 255, 215, 0),
        Color("Golden Brown", 153, 101, 21),
        Color("Golden Poppy", 252, 194, 0),
        Color("Golden Yellow", 255, 223, 0),
        Color("Goldenrod", 218, 165, 32),
        Color("Granny Smith Apple", 168, 228, 160),
        Color("Gray", 128, 128, 128),
        Color("Gray-Asparagus", 70, 89, 69),
        Color("Gray (Html/Css Gray)", 128, 128, 128),
        Color("Gray (X11 Gray)", 190, 190, 190),
        Color("Green (Color Wheel) (X11 Green)", 0, 255, 0),
        Color("Green (Crayola)", 28, 172, 120),
        Color("Green (Html/Css Green)", 0, 128, 0),
        Color("Green (Munsell)", 0, 168, 119),
        Color("Green (Ncs)", 0, 159, 107),
        Color("Green (Pigment)", 0, 165, 80),
        Color("Green (Ryb)", 102, 176, 50),
        Color("Green-Yellow", 173, 255, 47),
        Color("Grullo", 169, 154, 134),
        Color("Guppie Green", 0, 255, 127),
        Color("Halayà úBe", 102, 56, 84),
        Color("Han Blue", 68, 108, 207),
        Color("Han Purple", 82, 24, 250),
        Color("Hansa Yellow", 233, 214, 107),
        Color("Harlequin", 63, 255, 0),
        Color("Harvard Crimson", 201, 0, 22),
        Color("Harvest Gold", 218, 145, 0),
        Color("Heart Gold", 128, 128, 0),
        Color("Heliotrope", 223, 115, 255),
        Color("Hollywood Cerise", 244, 0, 161),
        Color("Honeydew", 240, 255, 240),
        Color("Honolulu Blue", 0, 127, 191),
        Color("Hooker'S Green", 73, 121, 107),
        Color("Hot Magenta", 255, 29, 206),
        Color("Hot Pink", 255, 105, 180),
        Color("Hunter Green", 53, 94, 59),
        Color("Iceberg", 113, 166, 210),
        Color("Icterine", 252, 247, 94),
        Color("Imperial Blue", 0, 35, 149),
        Color("Inchworm", 178, 236, 93),
        Color("India Green", 19, 136, 8),
        Color("Indian Red", 205, 92, 92),
        Color("Indian Yellow", 227, 168, 87),
        Color("Indigo", 111, 0, 255),
        Color("Indigo (Dye)", 0, 65, 106),
        Color("Indigo (Web)", 75, 0, 130),
        Color("International Klein Blue", 0, 47, 167),
        Color("International Orange (Aerospace)", 255, 79, 0),
        Color("International Orange (Engineering)", 186, 22, 12),
        Color("International Orange (Golden Gate Bridge)", 192, 54, 44),
        Color("Iris", 90, 79, 207),
        Color("Isabelline", 244, 240, 236),
        Color("Islamic Green", 0, 144, 0),
        Color("Ivory", 255, 255, 240),
        Color("Jade", 0, 168, 107),
        Color("Jasmine", 248, 222, 126),
        Color("Jasper", 215, 59, 62),
        Color("Jazzberry Jam", 165, 11, 94),
        Color("Jet", 52, 52, 52),
        Color("Jonquil", 250, 218, 94),
        Color("June Bud", 189, 218, 87),
        Color("Jungle Green", 41, 171, 135),
        Color("Kelly Green", 76, 187, 23),
        Color("Kenyan Copper", 124, 28, 5),
        Color("Khaki (Html/Css) (Khaki)", 195, 176, 145),
        Color("Khaki (X11) (Light Khaki)", 240, 230, 140),
        Color("Ku Crimson", 232, 0, 13),
        Color("La Salle Green", 8, 120, 48),
        Color("Languid Lavender", 214, 202, 221),
        Color("Lapis Lazuli", 38, 97, 156),
        Color("Laser Lemon", 254, 254, 34),
        Color("Laurel Green", 169, 186, 157),
        Color("Lava", 207, 16, 32),
        Color("Lavender Blue", 204, 204, 255),
        Color("Lavender Blush", 255, 240, 245),
        Color("Lavender (Floral)", 181, 126, 220),
        Color("Lavender Gray", 196, 195, 208),
        Color("Lavender Indigo", 148, 87, 235),
        Color("Lavender Magenta", 238, 130, 238),
        Color("Lavender Mist", 230, 230, 250),
        Color("Lavender Pink", 251, 174, 210),
        Color("Lavender Purple", 150, 123, 182),
        Color("Lavender Rose", 251, 160, 227),
        Color("Lavender (Web)", 230, 230, 250),
        Color("Lawn Green", 124, 252, 0),
        Color("Lemon", 255, 247, 0),
        Color("Lemon Chiffon", 255, 250, 205),
        Color("Lemon Lime", 227, 255, 0),
        Color("Licorice", 26, 17, 16),
        Color("Light Apricot", 253, 213, 177),
        Color("Light Blue", 173, 216, 230),
        Color("Light Brown", 181, 101, 29),
        Color("Light Carmine Pink", 230, 103, 113),
        Color("Light Coral", 240, 128, 128),
        Color("Light Cornflower Blue", 147, 204, 234),
        Color("Light Crimson", 245, 105, 145),
        Color("Light Cyan", 224, 255, 255),
        Color("Light Fuchsia Pink", 249, 132, 239),
        Color("Light Goldenrod Yellow", 250, 250, 210),
        Color("Light Gray", 211, 211, 211),
        Color("Light Green", 144, 238, 144),
        Color("Light Khaki", 240, 230, 140),
        Color("Light Pastel Purple", 177, 156, 217),
        Color("Light Pink", 255, 182, 193),
        Color("Light Red Ochre", 233, 116, 81),
        Color("Light Salmon", 255, 160, 122),
        Color("Light Salmon Pink", 255, 153, 153),
        Color("Light Sea Green", 32, 178, 170),
        Color("Light Sky Blue", 135, 206, 250),
        Color("Light Slate Gray", 119, 136, 153),
        Color("Light Taupe", 179, 139, 109),
        Color("Light Thulian Pink", 230, 143, 172),
        Color("Light Yellow", 255, 255, 224),
        Color("Lilac", 200, 162, 200),
        Color("Lime (Color Wheel)", 191, 255, 0),
        Color("Lime Green", 50, 205, 50),
        Color("Lime (Web) (X11 Green)", 0, 255, 0),
        Color("Limerick", 157, 194, 9),
        Color("Lincoln Green", 25, 89, 5),
        Color("Linen", 250, 240, 230),
        Color("Lion", 193, 154, 107),
        Color("Little Boy Blue", 108, 160, 220),
        Color("Liver", 83, 75, 79),
        Color("Lust", 230, 32, 32),
        Color("Magenta", 255, 0, 255),
        Color("Magenta (Dye)", 202, 31, 123),
        Color("Magenta (Process)", 255, 0, 144),
        Color("Magic Mint", 170, 240, 209),
        Color("Magnolia", 248, 244, 255),
        Color("Mahogany", 192, 64, 0),
        Color("Maize", 251, 236, 93),
        Color("Majorelle Blue", 96, 80, 220),
        Color("Malachite", 11, 218, 81),
        Color("Manatee", 151, 154, 170),
        Color("Mango Tango", 255, 130, 67),
        Color("Mantis", 116, 195, 101),
        Color("Mardi Gras", 136, 0, 133),
        Color("Maroon (Crayola)", 195, 33, 72),
        Color("Maroon (Html/Css)", 128, 0, 0),
        Color("Maroon (X11)", 176, 48, 96),
        Color("Mauve", 224, 176, 255),
        Color("Mauve Taupe", 145, 95, 109),
        Color("Mauvelous", 239, 152, 170),
        Color("Maya Blue", 115, 194, 251),
        Color("Meat Brown", 229, 183, 59),
        Color("Medium Aquamarine", 102, 221, 170),
        Color("Medium Blue", 0, 0, 205),
        Color("Medium Candy Apple Red", 226, 6, 44),
        Color("Medium Carmine", 175, 64, 53),
        Color("Medium Champagne", 243, 229, 171),
        Color("Medium Electric Blue", 3, 80, 150),
        Color("Medium Jungle Green", 28, 53, 45),
        Color("Medium Lavender Magenta", 221, 160, 221),
        Color("Medium Orchid", 186, 85, 211),
        Color("Medium Persian Blue", 0, 103, 165),
        Color("Medium Purple", 147, 112, 219),
        Color("Medium Red-Violet", 187, 51, 133),
        Color("Medium Ruby", 170, 64, 105),
        Color("Medium Sea Green", 60, 179, 113),
        Color("Medium Slate Blue", 123, 104, 238),
        Color("Medium Spring Bud", 201, 220, 135),
        Color("Medium Spring Green", 0, 250, 154),
        Color("Medium Taupe", 103, 76, 71),
        Color("Medium Turquoise", 72, 209, 204),
        Color("Medium Tuscan Red", 121, 68, 59),
        Color("Medium Vermilion", 217, 96, 59),
        Color("Medium Violet-Red", 199, 21, 133),
        Color("Mellow Apricot", 248, 184, 120),
        Color("Mellow Yellow", 248, 222, 126),
        Color("Melon", 253, 188, 180),
        Color("Midnight Blue", 25, 25, 112),
        Color("Midnight Green (Eagle Green)", 0, 73, 83),
        Color("Mikado Yellow", 255, 196, 12),
        Color("Mint", 62, 180, 137),
        Color("Mint Cream", 245, 255, 250),
        Color("Mint Green", 152, 255, 152),
        Color("Misty Rose", 255, 228, 225),
        Color("Moccasin", 250, 235, 215),
        Color("Mode Beige", 150, 113, 23),
        Color("Moonstone Blue", 115, 169, 194),
        Color("Mordant Red 19", 174, 12, 0),
        Color("Moss Green", 173, 223, 173),
        Color("Mountain Meadow", 48, 186, 143),
        Color("Mountbatten Pink", 153, 122, 141),
        Color("Msu Green", 24, 69, 59),
        Color("Mulberry", 197, 75, 140),
        Color("Mustard", 255, 219, 88),
        Color("Myrtle", 33, 66, 30),
        Color("Nadeshiko Pink", 246, 173, 198),
        Color("Napier Green", 42, 128, 0),
        Color("Naples Yellow", 250, 218, 94),
        Color("Navajo White", 255, 222, 173),
        Color("Navy Blue", 0, 0, 128),
        Color("Neon Carrot", 255, 163, 67),
        Color("Neon Fuchsia", 254, 65, 100),
        Color("Neon Green", 57, 255, 20),
        Color("New York Pink", 215, 131, 127),
        Color("Non-Photo Blue", 164, 221, 237),
        Color("North Texas Green", 5, 144, 51),
        Color("Ocean Boat Blue", 0, 119, 190),
        Color("Ochre", 204, 119, 34),
        Color("Office Green", 0, 128, 0),
        Color("Old Gold", 207, 181, 59),
        Color("Old Lace", 253, 245, 230),
        Color("Old Lavender", 121, 104, 120),
        Color("Old Mauve", 103, 49, 71),
        Color("Old Rose", 192, 128, 129),
        Color("Olive", 128, 128, 0),
        Color("Olive Drab #7", 60, 52, 31),
        Color("Olive Drab (Web) (Olive Drab #3)", 107, 142, 35),
        Color("Olivine", 154, 185, 115),
        Color("Onyx", 53, 56, 57),
        Color("Opera Mauve", 183, 132, 167),
        Color("Orange (Color Wheel)", 255, 127, 0),
        Color("Orange Peel", 255, 159, 0),
        Color("Orange-Red", 255, 69, 0),
        Color("Orange (Ryb)", 251, 153, 2),
        Color("Orange (Web Color)", 255, 165, 0),
        Color("Orchid", 218, 112, 214),
        Color("Otter Brown", 101, 67, 33),
        Color("Ou Crimson Red", 153, 0, 0),
        Color("Outer Space", 65, 74, 76),
        Color("Outrageous Orange", 255, 110, 74),
        Color("Oxford Blue", 0, 33, 71),
        Color("Pakistan Green", 0, 102, 0),
        Color("Palatinate Blue", 39, 59, 226),
        Color("Palatinate Purple", 104, 40, 96),
        Color("Pale Aqua", 188, 212, 230),
        Color("Pale Blue", 175, 238, 238),
        Color("Pale Brown", 152, 118, 84),
        Color("Pale Carmine", 175, 64, 53),
        Color("Pale Cerulean", 155, 196, 226),
        Color("Pale Chestnut", 221, 173, 175),
        Color("Pale Copper", 218, 138, 103),
        Color("Pale Cornflower Blue", 171, 205, 239),
        Color("Pale Gold", 230, 190, 138),
        Color("Pale Goldenrod", 238, 232, 170),
        Color("Pale Green", 152, 251, 152),
        Color("Pale Lavender", 220, 208, 255),
        Color("Pale Magenta", 249, 132, 229),
        Color("Pale Pink", 250, 218, 221),
        Color("Pale Plum", 221, 160, 221),
        Color("Pale Red-Violet", 219, 112, 147),
        Color("Pale Robin Egg Blue", 150, 222, 209),
        Color("Pale Silver", 201, 192, 187),
        Color("Pale Spring Bud", 236, 235, 189),
        Color("Pale Taupe", 188, 152, 126),
        Color("Pale Violet-Red", 219, 112, 147),
        Color("Pansy Purple", 120, 24, 74),
        Color("Papaya Whip", 255, 239, 213),
        Color("Paris Green", 80, 200, 120),
        Color("Pastel Blue", 174, 198, 207),
        Color("Pastel Brown", 131, 105, 83),
        Color("Pastel Gray", 207, 207, 196),
        Color("Pastel Green", 119, 221, 119),
        Color("Pastel Magenta", 244, 154, 194),
        Color("Pastel Orange", 255, 179, 71),
        Color("Pastel Pink", 222, 165, 164),
        Color("Pastel Purple", 179, 158, 181),
        Color("Pastel Red", 255, 105, 97),
        Color("Pastel Violet", 203, 153, 201),
        Color("Pastel Yellow", 253, 253, 150),
        Color("Patriarch", 128, 0, 128),
        Color("Payne'S Grey", 83, 104, 120),
        Color("Peach", 255, 229, 180),
        Color("Peach (Crayola)", 255, 203, 164),
        Color("Peach-Orange", 255, 204, 153),
        Color("Peach Puff", 255, 218, 185),
        Color("Peach-Yellow", 250, 223, 173),
        Color("Pear", 209, 226, 49),
        Color("Pearl", 234, 224, 200),
        Color("Pearl Aqua", 136, 216, 192),
        Color("Pearly Purple", 183, 104, 162),
        Color("Peridot", 230, 226, 0),
        Color("Periwinkle", 204, 204, 255),
        Color("Persian Blue", 28, 57, 187),
        Color("Persian Green", 0, 166, 147),
        Color("Persian Indigo", 50, 18, 122),
        Color("Persian Orange", 217, 144, 88),
        Color("Persian Pink", 247, 127, 190),
        Color("Persian Plum", 112, 28, 28),
        Color("Persian Red", 204, 51, 51),
        Color("Persian Rose", 254, 40, 162),
        Color("Persimmon", 236, 88, 0),
        Color("Peru", 205, 133, 63),
        Color("Phlox", 223, 0, 255),
        Color("Phthalo Blue", 0, 15, 137),
        Color("Phthalo Green", 18, 53, 36),
        Color("Piggy Pink", 253, 221, 230),
        Color("Pine Green", 1, 121, 111),
        Color("Pink", 255, 192, 203),
        Color("Pink Lace", 255, 221, 244),
        Color("Pink-Orange", 255, 153, 102),
        Color("Pink Pearl", 231, 172, 207),
        Color("Pink Sherbet", 247, 143, 167),
        Color("Pistachio", 147, 197, 114),
        Color("Platinum", 229, 228, 226),
        Color("Plum (Traditional)", 142, 69, 133),
        Color("Plum (Web)", 221, 160, 221),
        Color("Portland Orange", 255, 90, 54),
        Color("Powder Blue (Web)", 176, 224, 230),
        Color("Princeton Orange", 255, 143, 0),
        Color("Prune", 112, 28, 28),
        Color("Prussian Blue", 0, 49, 83),
        Color("Psychedelic Purple", 223, 0, 255),
        Color("Puce", 204, 136, 153),
        Color("Pumpkin", 255, 117, 24),
        Color("Purple Heart", 105, 53, 156),
        Color("Purple (Html/Css)", 128, 0, 128),
        Color("Purple Mountain Majesty", 150, 120, 182),
        Color("Purple (Munsell)", 159, 0, 197),
        Color("Purple Pizzazz", 254, 78, 218),
        Color("Purple Taupe", 80, 64, 77),
        Color("Purple (X11)", 160, 32, 240),
        Color("Quartz", 81, 72, 79),
        Color("Rackley", 93, 138, 168),
        Color("Radical Red", 255, 53, 94),
        Color("Rajah", 251, 171, 96),
        Color("Raspberry", 227, 11, 93),
        Color("Raspberry Glace", 145, 95, 109),
        Color("Raspberry Pink", 226, 80, 152),
        Color("Raspberry Rose", 179, 68, 108),
        Color("Raw Umber", 130, 102, 68),
        Color("Razzle Dazzle Rose", 255, 51, 204),
        Color("Razzmatazz", 227, 37, 107),
        Color("Red", 255, 0, 0),
        Color("Red-Brown", 165, 42, 42),
        Color("Red Devil", 134, 1, 17),
        Color("Red (Munsell)", 242, 0, 60),
        Color("Red (Ncs)", 196, 2, 51),
        Color("Red-Orange", 255, 83, 73),
        Color("Red (Pigment)", 237, 28, 36),
        Color("Red (Ryb)", 254, 39, 18),
        Color("Red-Violet", 199, 21, 133),
        Color("Redwood", 171, 78, 82),
        Color("Regalia", 82, 45, 128),
        Color("Resolution Blue", 0, 35, 135),
        Color("Rich Black", 0, 64, 64),
        Color("Rich Brilliant Lavender", 241, 167, 254),
        Color("Rich Carmine", 215, 0, 64),
        Color("Rich Electric Blue", 8, 146, 208),
        Color("Rich Lavender", 167, 107, 207),
        Color("Rich Lilac", 182, 102, 210),
        Color("Rich Maroon", 176, 48, 96),
        Color("Rifle Green", 65, 72, 51),
        Color("Robin Egg Blue", 0, 204, 204),
        Color("Rose", 255, 0, 127),
        Color("Rose Bonbon", 249, 66, 158),
        Color("Rose Ebony", 103, 72, 70),
        Color("Rose Gold", 183, 110, 121),
        Color("Rose Madder", 227, 38, 54),
        Color("Rose Pink", 255, 102, 204),
        Color("Rose Quartz", 170, 152, 169),
        Color("Rose Taupe", 144, 93, 93),
        Color("Rose Vale", 171, 78, 82),
        Color("Rosewood", 101, 0, 11),
        Color("Rosso Corsa", 212, 0, 0),
        Color("Rosy Brown", 188, 143, 143),
        Color("Royal Azure", 0, 56, 168),
        Color("Royal Blue (Traditional)", 0, 35, 102),
        Color("Royal Blue (Web)", 65, 105, 225),
        Color("Royal Fuchsia", 202, 44, 146),
        Color("Royal Purple", 120, 81, 169),
        Color("Royal Yellow", 250, 218, 94),
        Color("Rubine Red", 209, 0, 86),
        Color("Ruby", 224, 17, 95),
        Color("Ruby Red", 155, 17, 30),
        Color("Ruddy", 255, 0, 40),
        Color("Ruddy Brown", 187, 101, 40),
        Color("Ruddy Pink", 225, 142, 150),
        Color("Rufous", 168, 28, 7),
        Color("Russet", 128, 70, 27),
        Color("Rust", 183, 65, 14),
        Color("Rusty Red", 218, 44, 67),
        Color("Sacramento State Green", 0, 86, 63),
        Color("Saddle Brown", 139, 69, 19),
        Color("Safety Orange (Blaze Orange)", 255, 103, 0),
        Color("Saffron", 244, 196, 48),
        Color("Salmon", 255, 140, 105),
        Color("Salmon Pink", 255, 145, 164),
        Color("Sand", 194, 178, 128),
        Color("Sand Dune", 150, 113, 23),
        Color("Sandstorm", 236, 213, 64),
        Color("Sandy Brown", 244, 164, 96),
        Color("Sandy Taupe", 150, 113, 23),
        Color("Sangria", 146, 0, 10),
        Color("Sap Green", 80, 125, 42),
        Color("Sapphire", 15, 82, 186),
        Color("Sapphire Blue", 0, 103, 165),
        Color("Satin Sheen Gold", 203, 161, 53),
        Color("Scarlet", 255, 36, 0),
        Color("Scarlet (Crayola)", 253, 14, 53),
        Color("School Bus Yellow", 255, 216, 0),
        Color("Screamin' Green", 118, 255, 122),
        Color("Sea Blue", 0, 105, 148),
        Color("Sea Green", 46, 139, 87),
        Color("Seal Brown", 50, 20, 20),
        Color("Seashell", 255, 245, 238),
        Color("Selective Yellow", 255, 186, 0),
        Color("Sepia", 112, 66, 20),
        Color("Shadow", 138, 121, 93),
        Color("Shamrock Green", 0, 158, 96),
        Color("Shocking Pink", 252, 15, 192),
        Color("Shocking Pink (Crayola)", 255, 111, 255),
        Color("Sienna", 136, 45, 23),
        Color("Silver", 192, 192, 192),
        Color("Sinopia", 203, 65, 11),
        Color("Skobeloff", 0, 116, 116),
        Color("Sky Blue", 135, 206, 235),
        Color("Sky Magenta", 207, 113, 175),
        Color("Slate Blue", 106, 90, 205),
        Color("Slate Gray", 112, 128, 144),
        Color("Smalt (Dark Powder Blue)", 0, 51, 153),
        Color("Smokey Topaz", 147, 61, 65),
        Color("Smoky Black", 16, 12, 8),
        Color("Snow", 255, 250, 250),
        Color("Spiro Disco Ball", 15, 192, 252),
        Color("Spring Bud", 167, 252, 0),
        Color("Spring Green", 0, 255, 127),
        Color("St. Patrick'S Blue", 35, 41, 122),
        Color("Steel Blue", 70, 130, 180),
        Color("Stil De Grain Yellow", 250, 218, 94),
        Color("Stizza", 153, 0, 0),
        Color("Stormcloud", 79, 102, 106),
        Color("Straw", 228, 217, 111),
        Color("Sunglow", 255, 204, 51),
        Color("Sunset", 250, 214, 165),
        Color("Tan", 210, 180, 140),
        Color("Tangelo", 249, 77, 0),
        Color("Tangerine", 242, 133, 0),
        Color("Tangerine Yellow", 255, 204, 0),
        Color("Tango Pink", 228, 113, 122),
        Color("Taupe", 72, 60, 50),
        Color("Taupe Gray", 139, 133, 137),
        Color("Tea Green", 208, 240, 192),
        Color("Tea Rose (Orange)", 248, 131, 121),
        Color("Tea Rose (Rose)", 244, 194, 194),
        Color("Teal", 0, 128, 128),
        Color("Teal Blue", 54, 117, 136),
        Color("Teal Green", 0, 130, 127),
        Color("Telemagenta", 207, 52, 118),
        Color("Tenné (Tawny)", 205, 87, 0),
        Color("Terra Cotta", 226, 114, 91),
        Color("Thistle", 216, 191, 216),
        Color("Thulian Pink", 222, 111, 161),
        Color("Tickle Me Pink", 252, 137, 172),
        Color("Tiffany Blue", 10, 186, 181),
        Color("Tiger'S Eye", 224, 141, 60),
        Color("Timberwolf", 219, 215, 210),
        Color("Titanium Yellow", 238, 230, 0),
        Color("Tomato", 255, 99, 71),
        Color("Toolbox", 116, 108, 192),
        Color("Topaz", 255, 200, 124),
        Color("Tractor Red", 253, 14, 53),
        Color("Trolley Grey", 128, 128, 128),
        Color("Tropical Rain Forest", 0, 117, 94),
        Color("True Blue", 0, 115, 207),
        Color("Tufts Blue", 65, 125, 193),
        Color("Tumbleweed", 222, 170, 136),
        Color("Turkish Rose", 181, 114, 129),
        Color("Turquoise", 48, 213, 200),
        Color("Turquoise Blue", 0, 255, 239),
        Color("Turquoise Green", 160, 214, 180),
        Color("Tuscan Red", 124, 72, 72),
        Color("Twilight Lavender", 138, 73, 107),
        Color("Tyrian Purple", 102, 2, 60),
        Color("Ua Blue", 0, 51, 170),
        Color("Ua Red", 217, 0, 76),
        Color("Ube", 136, 120, 195),
        Color("Ucla Blue", 83, 104, 149),
        Color("Ucla Gold", 255, 179, 0),
        Color("Ufo Green", 60, 208, 112),
        Color("Ultra Pink", 255, 111, 255),
        Color("Ultramarine", 18, 10, 143),
        Color("Ultramarine Blue", 65, 102, 245),
        Color("Umber", 99, 81, 71),
        Color("Unbleached Silk", 255, 221, 202),
        Color("United Nations Blue", 91, 146, 229),
        Color("University Of California Gold", 183, 135, 39),
        Color("Unmellow Yellow", 255, 255, 102),
        Color("Up Forest Green", 1, 68, 33),
        Color("Up Maroon", 123, 17, 19),
        Color("Upsdell Red", 174, 32, 41),
        Color("Urobilin", 225, 173, 33),
        Color("Usafa Blue", 0, 79, 152),
        Color("Usc Cardinal", 153, 0, 0),
        Color("Usc Gold", 255, 204, 0),
        Color("Utah Crimson", 211, 0, 63),
        Color("Vanilla", 243, 229, 171),
        Color("Vegas Gold", 197, 179, 88),
        Color("Venetian Red", 200, 8, 21),
        Color("Verdigris", 67, 179, 174),
        Color("Vermilion (Cinnabar)", 227, 66, 52),
        Color("Vermilion (Plochere)", 217, 96, 59),
        Color("Veronica", 160, 32, 240),
        Color("Violet", 143, 0, 255),
        Color("Violet-Blue", 50, 74, 178),
        Color("Violet (Color Wheel)", 127, 0, 255),
        Color("Violet (Ryb)", 134, 1, 175),
        Color("Violet (Web)", 238, 130, 238),
        Color("Viridian", 64, 130, 109),
        Color("Vivid Auburn", 146, 39, 36),
        Color("Vivid Burgundy", 159, 29, 53),
        Color("Vivid Cerise", 218, 29, 129),
        Color("Vivid Tangerine", 255, 160, 137),
        Color("Vivid Violet", 159, 0, 255),
        Color("Warm Black", 0, 66, 66),
        Color("Waterspout", 164, 244, 249),
        Color("Wenge", 100, 84, 82),
        Color("Wheat", 245, 222, 179),
        Color("White", 255, 255, 255),
        Color("White Smoke", 245, 245, 245),
        Color("Wild Blue Yonder", 162, 173, 208),
        Color("Wild Strawberry", 255, 67, 164),
        Color("Wild Watermelon", 252, 108, 133),
        Color("Wine", 114, 47, 55),
        Color("Wine Dregs", 103, 49, 71),
        Color("Wisteria", 201, 160, 220),
        Color("Wood Brown", 193, 154, 107),
        Color("Xanadu", 115, 134, 120),
        Color("Yale Blue", 15, 77, 146),
        Color("Yellow", 255, 255, 0),
        Color("Yellow-Green", 154, 205, 50),
        Color("Yellow (Munsell)", 239, 204, 0),
        Color("Yellow (Ncs)", 255, 211, 0),
        Color("Yellow Orange", 255, 174, 66),
        Color("Yellow (Process)", 255, 239, 0),
        Color("Yellow (Ryb)", 254, 254, 51),
        Color("Zaffre", 0, 20, 168),
        Color("Zinnwaldite Brown", 44, 22, 8)
    ]

    for r in range(ROWS):
        cells.append([])
        for c in range(COLS):
            cells[r].append({"formula": None, "val": str(0)})

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        imgui.new_frame()

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):

                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", 'Cmd+Q', False, True
                )

                if clicked_quit:
                    exit(1)

                imgui.end_menu()
            imgui.end_main_menu_bar()

        # BEGIN COUNTER
        imgui.begin("Counter")
        imgui.text(str(counter))
        imgui.same_line(spacing=50)
        if imgui.button("Count"):
            counter += 1
        imgui.end()
        # END COUNTER

        # BEGIN TEMPCONV
        imgui.set_next_window_size(275, 55)
        imgui.begin("TempConv")
        imgui.push_item_width(50)
        inputC = imgui.input_float('Celsius =', tempC, format="%.1f")
        if inputC[0]:
            tempC = inputC[1]
            tempF = round((tempC * (9/5) + 32), 1)

        imgui.push_item_width(50)
        imgui.same_line(spacing=10)

        imgui.push_item_width(50)
        inputF = imgui.input_float('Fahrenheit', tempF, format="%.1f")
        if inputF[0]:
            tempF = inputF[1]
            tempC = round(((tempF - 32) / (9/5)), 1)

        imgui.end()
        # END TEMPCONV
        
        # BEGIN FLIGHT BOOKER
        imgui.set_next_window_size(250, 150)
        imgui.begin("Flight Booker")
        num_pops = 0

        _, flight_current = imgui.combo("##flight_combo", 
                flight_current, ["one way flight", "return flight"])

        start_date_date = validate_date(start_date)

        # invalid date
        if not start_date_date:
            imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 0.0, 0.0)
            num_pops += 1
        _, start_date = imgui.input_text('Start Date', start_date, 11)
        
        imgui.pop_style_color(num_pops)
        num_pops = 0

        end_date_flags = 0

        end_date_date = validate_date(end_date)

        # no end date for one way flight
        if flight_current == 0:
            end_date_flags |= imgui.INPUT_TEXT_READ_ONLY
            imgui.push_style_color(imgui.COLOR_TEXT, 0.5, 0.5, 0.5)
            num_pops += 1


        # invalid date
        if not end_date_date and flight_current == 1:
            imgui.push_style_color(imgui.COLOR_TEXT, 1.0, 0.0, 0.0)
            num_pops += 1
        _, end_date = imgui.input_text('End Date', end_date, 11, end_date_flags)

        imgui.pop_style_color(num_pops)
        num_pops = 0

        # PyImGui doesn't support disabled buttons, so instead conditionally show text/button
        if not end_date_date or not start_date_date or end_date_date < start_date_date:
            imgui.text("Book")
        elif imgui.button("Book"):
            imgui.open_popup("Booking Confirmation")
        imgui.same_line()
        if imgui.begin_popup("Booking Confirmation"):
            if flight_current == 0:
                imgui.text("You booked a one way flight for " + start_date_date.strftime("%m.%d.%Y")+ ".")
            else: 
                imgui.text("You booked a flight for " + start_date_date.strftime("%m.%d.%Y") + " and a return flight on " + end_date_date.strftime("%m.%d.%Y")+".")
            imgui.end_popup()

        imgui.end()
        # END FLIGHT BOOKER

        # BEGIN TIMER
        imgui.begin('CRUD')
        imgui.text("Filter prefix:")
        imgui.same_line()
        _, crud_filter_text = imgui.input_text('##crud_filter', crud_filter_text, 999)
        imgui.text("Name:")
        imgui.same_line()
        _, crud_first_name_text = imgui.input_text("##crud_first_name", crud_first_name_text, 100)
        imgui.text("Surname:")
        imgui.same_line()
        _, crud_last_name_text = imgui.input_text("##crud_last_name", crud_last_name_text, 100)


        name_format = "{}, {}"
        for i in range(len(crud_names)):
            if crud_filter_text == crud_names[i].last_name[:len(crud_filter_text)]:
                _, crud_selected[i] = imgui.selectable(name_format.format(crud_names[i].last_name, crud_names[i].first_name), crud_selected[i])
            else:
                # anything not displayed should not be selected
                crud_selected[i] = False

        if imgui.button("Create"):
            crud_names.append(Person(crud_first_name_text, crud_last_name_text))
            crud_selected.append(False)
            crud_first_name_text = ""
            crud_last_name_text = ""
        imgui.same_line()


        if not True in crud_selected:
            # no element selected
            imgui.text("Update")
            imgui.same_line()
            imgui.text("Delete")
        else: 
            if imgui.button("Update"):
                for i in range(len(crud_selected)):
                    if crud_selected[i]:
                        crud_names[i].first_name = crud_first_name_text
                        crud_names[i].last_name = crud_last_name_text
                        crud_first_name_text = ""
                        crud_last_name_text = ""
            imgui.same_line()
            if imgui.button("Delete"):
                for i in range(len(crud_selected)):
                    if crud_selected[i]:
                        crud_names.pop(i)
                        crud_selected.pop(i)
                        crud_first_name_text = ""
                        crud_last_name_text = ""
                        break

        imgui.end()
        # END CRUD

        # BEGIN TIMER
        imgui.begin('Timer')
        
        elapsed_time = round((time.perf_counter() - start_time), 1)
        if elapsed_time < 0:
            elapsed_time = 0

        imgui.text('Elapsed Time:')
        imgui.same_line()
        imgui.progress_bar(elapsed_time / timer_length, (100, 20))
        imgui.text(str(elapsed_time) + 's')
        changed, timer_length = imgui.slider_float(
            "", timer_length,
            min_value=1.0, max_value=60.0,
            format="%.0f",
            power=1.0
            )
        
        if imgui.button("Reset"):
            start_time = time.perf_counter()
        imgui.end()
        # END TIMER
        

        # MVP
        imgui.begin("MVP")

        if imgui.button("Click me!"):
            show_mvp_window = True

        imgui.end()

        if show_mvp_window:
            imgui.begin("Successful click!")
            imgui.text("Congratulations, this was much easier in Python than React Native")
            if imgui.button("Close Me"):
                show_mvp_window = False
            imgui.end()
        # END MVP

        #CIRCLES
        imgui.begin("Circle")

        if imgui.button("Redo"):
            e = undo_list.redo()
            if e is not None:
                if e.action == "DRAW":
                    circle_list.insert(e.index, {"pos": (e.x, e.y), "filled": 0, "r": e.radius})
                else:
                    circle_list[e.index]["r"] = e.radius

        if imgui.button("Undo"):
            e = undo_list.undo()
            if e is not None:
                if e.action == "DRAW":
                    if circle_list[e.index] == colored_circle:
                        colored_circle = None
                        colored_circle_size = 0
                    circle_list.pop(e.index)
                else:
                    circle_list[e.index]["r"] = e.old_radius

        draw_list = imgui.get_window_draw_list()
        io = imgui.get_io()
        pos = io.mouse_pos

        if imgui.is_mouse_clicked(0) and imgui.is_window_hovered():
            dist = float('inf')

            for circle in circle_list:
                dist_to_click = math.sqrt((circle["pos"][0] - pos[0]) ** 2 + (circle["pos"][1] - pos[1]) ** 2)
                if dist_to_click < dist and dist_to_click > circle["r"]:
                    colored_circle = circle
                    colored_circle_size = circle["r"]
                    dist = dist_to_click

            circle_list.append({"pos": pos, "filled": 0, "r": 20})
            undo_list.add_event("DRAW", len(circle_list) - 1, radius = 20, x = pos[0], y = pos[1])

        if imgui.is_mouse_clicked(1) and colored_circle is not None:
            show_circle_slider = True
            
        for circle in circle_list:
            if circle != colored_circle:
                draw_list.add_circle(circle["pos"][0], circle["pos"][1], circle["r"], imgui.get_color_u32_rgba(1,1,0,1), thickness=3)
            else:
                draw_list.add_circle_filled(circle["pos"][0], circle["pos"][1], circle["r"], imgui.get_color_u32_rgba(1,1,0,1))

        imgui.end()

        if show_circle_slider:
            x = colored_circle["pos"][0]
            y = colored_circle["pos"][1]
            imgui.begin(f"Adjust diameter of circle")
            _, rad = imgui.slider_int("Radius", colored_circle["r"], 0, 100, format = "%d")
            colored_circle["r"] = rad
            if imgui.button("Close"):
                show_circle_slider = False
                undo_list.add_event("RESIZE", circle_list.index(colored_circle), radius = rad, old_radius = colored_circle_size)
                colored_circle_size = rad
            imgui.end()
        #END CIRCLES

        #CELLS

        imgui.begin("Cells", flags = imgui.WINDOW_HORIZONTAL_SCROLLING_BAR)

        imgui.begin_group()

        for r in range(ROWS):
            for c in range(ord('A') - 1, ord('Z') + 1):
                imgui.push_item_width(100)
                if r == 0 and c >= ord('A'):
                    imgui.input_text(f'##{c}{r}', chr(c), 20, flags = imgui.INPUT_TEXT_READ_ONLY)
                elif c == ord('A') - 1:
                    imgui.input_text(f'##{c}{r}', str(r), 20, flags = imgui.INPUT_TEXT_READ_ONLY)
                else:
                    changed, cells[r][c - ord('A')]["val"] = imgui.input_text(f'##{c}{r}', str(cells[r][c - ord('A')]["val"]), 20)
                    s = sum_reg.match(cells[r][c - ord('A')]["val"])

                    if s != None:
                        cells[r][c - ord('A')]["formula"] = s.group()
                    
                    if changed:
                        cells[r][c - ord('A')]["formula"] = None

                    if cells[r][c - ord('A')]["formula"] != None:
                        cells[r][c - ord('A')]["val"] = calculate_cell_sum(cells[r][c - ord('A')]["formula"], cells)

                imgui.pop_item_width()
                if c < ord('Z'):
                    imgui.same_line()
        
        imgui.end_group()

        imgui.end()

        #END CELLS
        
        # CNH Demo

        imgui.begin("CNH")
        imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (0, 0))

        imgui.push_style_color(imgui.COLOR_CHILD_BACKGROUND, 0, 0, 103)
        imgui.begin_child("child1", width = w, height = h, border = True)

        imgui.push_style_color(imgui.COLOR_BUTTON, button_colors[0][0], button_colors[0][1], button_colors[0][2])
        if imgui.button("Color 1"):
            click1 = not click1
        imgui.pop_style_color()

        imgui.push_style_color(imgui.COLOR_BUTTON, button_colors[1][0], button_colors[1][1], button_colors[1][2])
        if imgui.button("Color 2"):
            click2 = not click2
        imgui.pop_style_color()

        imgui.push_style_color(imgui.COLOR_BUTTON, button_colors[2][0], button_colors[2][1], button_colors[2][2])
        if imgui.button("Color 3"):
            click3 = not click3
        imgui.pop_style_color()

        if imgui.button("Damage"):
            health -= 10
        
        if health <= 0:
            imgui.text(f"{name} defeated")

        if imgui.button("Heal"):
            health = 100

        imgui.end_child()
        imgui.pop_style_color()

        imgui.same_line()

        imgui.invisible_button("vsplitter", 8, h)

        imgui.same_line()

        imgui.push_style_color(imgui.COLOR_CHILD_BACKGROUND, 0, 0, 0)
        imgui.begin_child("child2", width = 0, height = h, border = True)

        imgui.text("Name")
        imgui.same_line()
        _, name = imgui.input_text("##Name", name, 20)

        imgui.text(" ")

        imgui.text("Health")
        imgui.same_line()
        _, health = imgui.input_float("##Health", health)

        imgui.text(" ")

        imgui.text("Color")
        imgui.same_line()
        changed, color_ind = imgui.combo("", color_ind, [c.label for c in colors])

        if changed:
            if click1:
                button_colors[0] = (colors[color_ind].r, colors[color_ind].g, colors[color_ind].b)
            if click2:
                button_colors[1] = (colors[color_ind].r, colors[color_ind].g, colors[color_ind].b)
            if click3:
                button_colors[2] = (colors[color_ind].r, colors[color_ind].g, colors[color_ind].b)
            print(str(colors[color_ind].r) + " " + str(colors[color_ind].g) + " " + str(colors[color_ind].b))
        imgui.end_child()
        imgui.pop_style_color()

        imgui.same_line()

        imgui.invisible_button("hsplitter", -1, 8)

        imgui.pop_style_var()
        imgui.end()

        # End CNH
        gl.glClearColor(1., 1., 1., 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()


def impl_glfw_init():
    width, height = 1280, 720
    window_name = "minimal ImGui/GLFW3 example"

    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)

    # OS X supports only forward-compatible core profiles from 3.2
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(
        int(width), int(height), window_name, None, None
    )
    glfw.make_context_current(window)

    if not window:
        glfw.terminate()
        print("Could not initialize Window")
        exit(1)

    return window

if __name__ == "__main__":
    main()