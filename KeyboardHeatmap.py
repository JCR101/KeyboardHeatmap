import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib import animation
from pynput import keyboard
import queue
import threading

# Disables all default key bindings in Matplotlib
for key in mpl.rcParams:
    if key.startswith('keymap.'):
        mpl.rcParams[key] = ''


key_queue = queue.Queue()
fig, ax = plt.subplots(figsize=(10, 6))
hover_text_display = ax.text(
    7, -0.5, 'test_text', ha='center', va='center', color='blue', fontsize=30, zorder=10)
fig.canvas.draw()

fig.subplots_adjust(bottom=0.15)
canvas = fig.canvas

text_objects = {}
last_hovered_key = None

# Initializes dictionary with keys and default press count of 0

keys_pressed = {key: 0 for key in [
    'esc', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
    '`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'backspace',
    'tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\',
    'capslock', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', 'enter',
    'shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'rshift',
    'ctrl', 'alt', 'space', 'ralt', 'rctrl', '-'
]}

# Dictionary to fix the visual representation of the keys
key_visual_representation = {
    'esc': 'Esc', 'f1': 'F1', 'f2': 'F2', 'f3': 'F3', 'f4': 'F4', 'f5': 'F5',
    'f6': 'F6', 'f7': 'F7', 'f8': 'F8', 'f9': 'F9', 'f10': 'F10', 'f11': 'F11', 'f12': 'F12',
    '`': '`', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7',
    '8': '8', '9': '9', '0': '0', '-': '-', '=': '=', 'backspace': '⬅️',
    'tab': '→|', 'q': 'Q', 'w': 'W', 'e': 'E', 'r': 'R', 't': 'T', 'y': 'Y', 'u': 'U',
    'i': 'I', 'o': 'O', 'p': 'P', '[': '[', ']': ']', '\\': '\\',
    'capslock': '⬆️ Lock', 'a': 'A', 's': 'S', 'd': 'D', 'f': 'F', 'g': 'G', 'h': 'H',
    'j': 'J', 'k': 'K', 'l': 'L', ';': ';', '\'': '\'', 'enter': '⏎',
    'shift': '⇧', 'z': 'Z', 'x': 'X', 'c': 'C', 'v': 'V', 'b': 'B', 'n': 'N', 'm': 'M',
    ',': ',', '.': '.', '/': '/', 'rshift': '⇧',
    'ctrl': 'Ctrl', 'alt': 'Alt', 'space': 'Space',
    'ralt': 'Alt', 'rctrl': 'Ctrl'
}


def on_press(key):
    if not running:
        return False

    try:
        # Checks if the key character is in the dictionary
        key_char = key.char
    except AttributeError:
        # Handles special cases
        if key == keyboard.Key.shift_r:
            key_char = "rshift"
        elif key == keyboard.Key.ctrl_r:
            key_char = "rctrl"
        elif key == keyboard.Key.alt_gr:
            key_char = "ralt"
        elif key == keyboard.Key.caps_lock:
            key_char = "capslock"
        elif key == keyboard.Key.ctrl_l:
            key_char = "ctrl"
        elif key == keyboard.Key.alt_l:
            key_char = "alt"

        else:
            key_char = str(key).split('.')[1]
            # gets the key name for special keys like space, esc, etc.

    # Increases the count of the key pressed
    if key_char in keys_pressed:
        keys_pressed[key_char] += 1
        print(f"Key pressed: {key_char}, Count: {keys_pressed[key_char]}")


def update_heatmap():
    if not plt.fignum_exists(fig.number):  # Checks if the figure still exists
        return

    current_hover_text = hover_text_display.get_text()

    # clears the current axes that the heatmap is on
    plt.gca().cla()

    # Adjustes key positions for a more realistic layout
    key_positions = {
        'esc': (0, 6), 'f1': (2, 6), 'f2': (3, 6), 'f3': (4, 6), 'f4': (5, 6), 'f5': (6, 6), 'f6': (7, 6), 'f7': (8, 6), 'f8': (9, 6), 'f9': (10, 6), 'f10': (11, 6), 'f11': (12, 6), 'f12': (13, 6),
        # ... (first row of keys)
        '`': (0, 5), '1': (1, 5), '2': (2, 5), '3': (3, 5), '4': (4, 5), '5': (5, 5), '6': (6, 5), '7': (7, 5), '8': (8, 5), '9': (9, 5), '0': (10, 5), '-': (11, 5), '=': (12, 5), 'backspace': (13, 5),
        # ... (second row of keys)
        'tab': (0, 4), 'q': (1.5, 4), 'w': (2.5, 4), 'e': (3.5, 4), 'r': (4.5, 4), 't': (5.5, 4), 'y': (6.5, 4), 'u': (7.5, 4), 'i': (8.5, 4), 'o': (9.5, 4), 'p': (10.5, 4), '[': (11.5, 4), ']': (12.5, 4), '\\': (13.5, 4),
        # ... (third row of keys)
        'capslock': (0.25, 3), 'a': (1.75, 3), 's': (2.75, 3), 'd': (3.75, 3), 'f': (4.75, 3), 'g': (5.75, 3), 'h': (6.75, 3), 'j': (7.75, 3), 'k': (8.75, 3), 'l': (9.75, 3), ';': (10.75, 3), '\'': (11.75, 3), 'enter': (12.75, 3),
        # ... (fourth row of keys)
        'shift': (0, 2), 'z': (2, 2), 'x': (3, 2), 'c': (4, 2), 'v': (5, 2), 'b': (6, 2), 'n': (7, 2), 'm': (8, 2), ',': (9, 2), '.': (10, 2), '/': (11, 2), 'rshift': (12, 2),
        # ... (fifth row of keys)
        'ctrl': (0, 1), 'alt': (3, 1), 'space': (8, 1), 'ralt': (12, 1), 'rctrl': (13.5, 1),
        # ... (sixth row of keys)

    }

    max_value = max(keys_pressed.values())
    # Handles the case where all counts are zero
    if max_value == 0:
        max_value = 1

    for key, position in key_positions.items():
        if key in ['-', '=', '[', ']', '\\', ';', '\'', ',', '.', '/', '`']:
            text_objects[key] = plt.text(position[0], position[1], key_visual_representation[key],
                                         ha='center', va='center', picker=True,
                                         bbox=dict(boxstyle="square,pad=0.5",
                                                   facecolor=colors.rgb2hex(plt.cm.Reds(
                                                       keys_pressed[key] / max_value)),
                                                   edgecolor="black"
                                                   )
                                         )
        else:

            text_objects[key] = plt.text(position[0], position[1], key_visual_representation[key].upper(),
                                         ha='center', va='center', picker=True,
                                         bbox=dict(boxstyle="square,pad=0.5",
                                                   facecolor=colors.rgb2hex(plt.cm.Reds(
                                                       keys_pressed[key] / max_value)),
                                                   edgecolor="black"
                                                   )


                                         )

    plt.xlim(-1, 15)
    plt.ylim(-1, 7)
    plt.axis('off')
    plt.draw()
    canvas.draw()
    canvas.flush_events()

    if last_hovered_key:
        hover_text_display.set_text(
            f"Hovering over key: {key_visual_representation[last_hovered_key]} - Press count: {keys_pressed[last_hovered_key]}")
    else:
        hover_text_display.set_text('')
    hover_text_display.set_zorder(10)
    hover_text_display.set_text(current_hover_text)  # Restore the hover text
    print(current_hover_text)


def on_hover(event):
    global last_hovered_key  # Declare it global so you can modify its value
    found_key = None
    for key, text in text_objects.items():
        if text.contains(event)[0]:
            found_key = key
            break

    if last_hovered_key != found_key:  # Check if this is a different key
        last_hovered_key = found_key  # Update the last hovered key
        if found_key:
            hover_text_display.set_text(
                f"Hovering over key: {key_visual_representation[key]} - Press count: {keys_pressed[key]}")
            canvas.draw_idle()
        else:
            # Clear text if not hovering over a key
            hover_text_display.set_text('')
            canvas.draw_idle()


fig.canvas.mpl_connect('motion_notify_event', on_hover)


def on_close(event):
    global running
    running = False
    # allows you to close the file and stop the program


fig.canvas.mpl_connect('close_event', on_close)


running = True


def animate(i):
    if not plt.fignum_exists(fig.number):  # Checks if the figure still exists
        return
    update_heatmap()  # Calling update_heatmap


# Using FuncAnimation to periodically call update_heatmap
ani = animation.FuncAnimation(
    fig, animate, interval=1000, cache_frame_data=False)

# Attaching the animation to the figure to prevent it from being garbage collected
fig.ani = ani


# Starting the pynput listener in a separate thread
def listen_keys():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


# Starting the pynput listener in a separate thread
thread = threading.Thread(target=listen_keys)
# set to a daemon to help with garbage collection on exit
thread.daemon = True
thread.start()


plt.show()
