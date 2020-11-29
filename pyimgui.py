# -*- coding: utf-8 -*-
import datetime
import time, threading
import glfw
import imgui
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer


class Person:
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

def validate_date(date_str):
    try:
        return datetime.datetime.strptime(date_str, "%m.%d.%Y")
    except ValueError:
        return None

def main():
    imgui.create_context()
    window = impl_glfw_init()
    impl = GlfwRenderer(window)

    counter = 0
    tempC = 0
    tempF = 32

    flight_current = 0
    start_date = "01.01.1970"
    end_date = start_date 
    crud_selected = [False, False, False]
    crud_names = [Person("Steven", "Tyler"), Person("Tom", "Hamilton"), Person("Joey", "Kramer")]
    crud_filter_text = ""
    crud_first_name_text = ""
    crud_last_name_text = ""

    timer = 0
    xSize = 0
    ySize = 0
    fraction = .35
    value = 30

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

        imgui.begin("Counter")
        imgui.text(str(counter))
        imgui.same_line(spacing=50)
        if imgui.button("Count"):
            counter += 1
        imgui.end()


        imgui.set_next_window_position(200, 60)
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


        # END FLIGHT BOOKER
        imgui.end()



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

        imgui.begin('Timer')
        #imgui.text('Elapsed Time:')
        #imgui.same_line()
        #imgui.text('Bar thing')
        #imgui.progress_bar(fraction, xSize, ySize)
        imgui.text(str(timer) + 's')
        imgui.text('Duration:')
        imgui.same_line()
        changed, value = imgui.slider_float(
            "", value,
            min_value=0.0, max_value=60.0,
            format="%.0f",
            power=1.0
            )

        #def countdown(var):
        #    while var > 1:
        #        var -= 1
                #time.sleep(1)

        if changed:
            timer = value
            timer -= 1
            #temp = timer * 10000
            #while temp > 0:
            #    if (temp % 1000 == 0):
            #        timer -= 1
        
        
        if imgui.button("Reset"):
            timer = 0
            value = 30
        imgui.end()


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
