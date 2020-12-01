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