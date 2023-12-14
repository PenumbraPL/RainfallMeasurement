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
    savedData = float(0)
    while go_event.isSet():
        data = arduino.readline().decode('utf-8').strip("\n").split(":")
        try:
            data_type = data[0]
            flowRate = None      
            if data_type == 'P':
                waterFlow = int(data[1])
                flowRate = waterFlow / 2.25
                flowRate = flowRate * 1000. / 60.
                print(flowRate)
            elif data_type == 'H':
                print(data[1])
            elif data_type == 'H_MIN':
                print(data[1])
            elif data_type == 'D':
                print(data[1])
            elif data_type == 'B':
                print(data[1])
            flowRate = flowRate if flowRate else savedData
            savedData = flowRate
            pumpState = 'Unknown'
            waterLevel = '13 mm'
            rainfall = '10 mm'

            data = { 'water' : str(flowRate),
                'pump' : pumpState, 'level': waterLevel, 'rainfall' : rainfall}

            window.write_event_value("Working", (data))
        except Exception as ex:
            print("Data is not readable!")
            print(ex)


def gui_init():
    layout = [[sg.Text('Podaj wysokość pojemnika w mm', key="height"), sg.InputText(key="in1")],
              [sg.Text('Podaj objętość pojemnika', key="vol"), sg.InputText(key="in2")],
              [sg.Text("", key="water", visible=False)],
              [sg.Text("", key="rainfall", visible=False)],
              [sg.Text("", key="level", visible=False)],
              [sg.Text("", key="pump", visible=False)],
              [sg.Button('Zatwierdz', key="Start")]]

    window = sg.Window("Pomiar opadów", layout,size=(300, 250))

    return window


def gui_update(window, data):
    window["height"].Update("Wysokość pojemnika: \t" + data["height"])
    window["vol"].Update("Objętość pojemnika: \t" + data["vol"])
    window["water"].Update("Ilość wody: \t\t" + data["water"], visible=True)
    window["pump"].Update("Pompa włączona: \t\t1" + data["pump"], visible=True)
    window["level"].Update("Wysokość wody: \t\t1" + data["level"], visible=True)
    window["rainfall"].Update("Ilość opadów: \t\t1" + data["rainfall"], visible=True)
    window["in1"].Update(visible=False)
    window["in2"].Update(visible=False)
    window["Start"].Update(visible=False)


if __name__ == "__main__":
    window = gui_init()

    go_event = threading.Event()

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            break
        elif event == "Start":
            try:
                val1 = values['in1']
                val2 = values['in2']
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
            data = values[event]
            #str((int(data["height"])-int(data["water"]))/int(data["height"]))
            data.update({'height' : values['in1'], 'vol' : values['in2']})

            try:
                gui_update(window, data)
            except Exception as ex:
                print("sth went wrong - check data")
                print(ex)

    window.close()
