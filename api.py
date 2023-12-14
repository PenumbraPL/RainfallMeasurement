import threading
import serial
import PySimpleGUI as sg

arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)

sg.theme('DarkAmber')


def write(x):
    arduino.write(bytes(x, 'utf-8'))

def parse_line(start_txt, line):
    if line.find(start_txt) != -1:
        return int(line[len(start_txt):])


def read(window, go_event):
    while go_event.isSet():
        data = arduino.readline().decode('utf-8').strip("\n").split(",")
        try:
            height = data[0]
            print(height)         
            waterFlow = parse_line('D: ', height)
            if waterFlow:
                flowRate = waterFlow / 2.25
                flowRate = flowRate * 1000. / 60.
                print(flowRate)
            # window.write_event_value("Working", (156))
        except Exception as ex:
            print("Data is not readable!")
            print(ex)


def gui_init():
    layout = [[sg.Text('Podaj wysokość pojemnika w mm', key="height"), sg.InputText(key="in1")],
              [sg.Text('Podaj objętość pojemnika', key="vol"), sg.InputText(key="in2")],
              [sg.Text("", key="label", visible=False)],
              [sg.Button('Zatwierdz', key="Start")]]

    window = sg.Window("Pomiar opadów", layout,size=(300, 150))

    return window


def gui_update(window, w, o, p):
    window["height"].Update("Wysokość pojemnika: " + w)
    window["vol"].Update("Objętość pojemnika: " + o)
    window["label"].Update("Odczyt z arduino: " + p, visible=True)
    window["in1"].Update(visible=False)
    window["in2"].Update(visible=False)
    window["start"].Update(visible=False)


if __name__ == "__main__":
    window = gui_init()

    go_event = threading.Event()

    while True:
        event, values = window.read()
        val1 = values['in1']
        val2 = values['in2']

        if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            break
        elif event == "Start":
            try:
                if val1 == '' or val2 == '' or not int(val1) or not int(val2):
                    raise Exception()
                write(val1)
                go_event.set()
                read_thread = threading.Thread(target=read, args=(window, go_event), daemon=True)
                read_thread.start()
            except:
                window["label"].Update("Wysokość i objętość muszą być liczbami!", visible=True)
                print("Wysokość i objętość muszą być liczbami")
        elif event == "Working":
            height_left = values[event]

            curr_height_in_per = (int(val1)-int(height_left))/int(val1)
            try:
                gui_update(window, values['in1'], values['in2'], curr_height_in_per)
            except:
                print("sth went wrong - check data")
        

    window.close()
