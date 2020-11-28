# -*- coding: utf-8 -*-
import glfw
import OpenGL.GL as gl

import imgui
from imgui.integrations.glfw import GlfwRenderer


def main():
    imgui.create_context()
    window = impl_glfw_init()
    impl = GlfwRenderer(window)

    counter = 0
    tempC = 0
    tempF = 32

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