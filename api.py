import threading
import serial
import PySimpleGUI as sg
import csv
import schedule
import datetime
from os.path import exists

arduino = serial.Serial(port='COM24', baudrate=9600, timeout=1)
amount = 0
sg.theme('DarkAmber')


def write(symbol, x):
    arduino.write(bytes(symbol, 'utf-8'))
    arduino.write(bytes(x, 'utf-8'))

def parse_line(start_txt, line):
    if line.find(start_txt) != -1:
        return int(line[len(start_txt):])

def write_to_file(path_to_file, rows):
    global amount
    if not isinstance(path_to_file, str):
        return
    try:
        if exists(path_to_file):
            with open(path_to_file, 'a') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
        else:
             with open(path_to_file, 'w') as f:
                writer = csv.writer(f)
                header_data = ['Time', 'Height', 'Volume']
                writer.writerow(header_data)
                writer.writerows(rows)
        amount = 0         
    except Exception as ex:
        print(ex)


def read(window, go_event):
    savedData = {'flowRate' : 0, 'pumpState': 'Unknown', 'waterLevel' : 0, 'sensorLevel' : 'Unknown'}
    while go_event.isSet():
        data = arduino.readline().decode('utf-8').strip("\n").split(":")
        try:
            data_type = data[0]
            flowRate = None
            pumpState = None     
            waterLevel = None
            sensorLevel = None
            if data_type == 'P':
                waterFlow = int(data[1])
                flowRate = waterFlow / 2.25
                flowRate = flowRate * 1000. / 60.
                #print(flowRate)
            elif data_type == 'D':
                waterLevel = int(data[1])
                print(data[1])
            elif data_type == 'S':
                s = int(data[1])
                if s < 266:
                    sensorLevel = '< 5 mm'
                elif s < 313:
                    sensorLevel = '5-10 mm'
                elif s < 331:
                    sensorLevel = '10-15 mm'
                elif s < 346:
                    sensorLevel = '15-20 mm'
                elif s < 356:
                    sensorLevel = '20-25 mm'
                elif s < 362:
                    sensorLevel = '25-30 mm'
                elif s < 370:
                    sensorLevel = '30-35 mm'
                elif s < 376:
                    sensorLevel = '35-40 mm'
                elif s < 380:
                    sensorLevel = '40-45 mm'
                elif s < 385:
                    sensorLevel = '45-48 mm'
                print(data[1])
            elif data_type == 'B':
                pumpState = 'Wł.' if int(data[1]) else 'Wył.'
                # print(data[1])

            flowRate = flowRate if flowRate else savedData['flowRate']
            savedData["flowRate"] = flowRate
            
            pumpState = pumpState if pumpState else savedData["pumpState"]
            savedData["pumpState"] = pumpState

            waterLevel = waterLevel if waterLevel else savedData["waterLevel"]
            savedData["waterLevel"] = waterLevel
            
            sensorLevel = sensorLevel if sensorLevel else savedData["sensorLevel"]
            savedData["sensorLevel"] = sensorLevel

            time = '10'

            data = { 'water' : str(flowRate), 'pump' : pumpState,
                     'level': str(waterLevel), 'time' : time, 'sensor' : sensorLevel}

            window.write_event_value("Working", (data))
        except Exception as ex:
            print("Data is not readable!")
            print(ex)


def gui_init():
    layout = [[sg.Text('Podaj wysokość pojemnika w mm', key="height"), sg.InputText(key="in1")],
              [sg.Text('Podaj objętość pojemnika', key="vol"), sg.InputText(key="in2")],
              [sg.Text('Podaj obszar z jakiego zebrano opad', key="area"), sg.InputText(key="in3")],
              [sg.Text("", key="water", visible=False)],
              [sg.Text("", key="level", visible=False)],
              [sg.Text("", key="pump", visible=False)],
              [sg.Button('Zapisz', key="Write", visible=False)],
              [sg.Button('Zatwierdz', key="Start")]]

    window = sg.Window("Pomiar opadów", layout,size=(300, 250))

    return window


def gui_update(window, data):
    window["height"].Update("Wysokość pojemnika: \t" + data["height"])
    window["vol"].Update("Objętość pojemnika: \t" + data["vol"])
    window["water"].Update("Ilość wody: \t\t" + data["water"], visible=True)
    window["pump"].Update("Pompa włączona: \t\t" + data["pump"], visible=True)
    window["level"].Update("Wysokość wody: \t\t" + data["level"], visible=True)
    window["in1"].Update(visible=False)
    window["in2"].Update(visible=False)
    window["in3"].Update(visible=False)
    window["Write"].Update(visible=True)
    window["Start"].Update(visible=False)


if __name__ == "__main__":
    window = gui_init()
    data_write = list()
    schedule.every(10).seconds.do(write_to_file,'data/test.csv',data_write)
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
                write('MAX:', val1)
                go_event.set()
                read_thread = threading.Thread(target=read, args=(window, go_event), daemon=True)
                read_thread.start()
            except:
                window["label"].Update("Wysokość i objętość muszą być liczbami!", visible=True)
                print("Wysokość i objętość muszą być liczbami")
        elif event == "Working":
            data = values[event]
            data.update({'height' : values['in1'], 'vol' : values['in2']})
            
            valueInPerc = int(values['in1']) - int(data['level'])
            if valueInPerc < 0:
                valueInPerc = 0
            valueInPerc = valueInPerc/ int(values['in1']) * 100
            area = int(values['in3'])
            amount += data['water']

            data_write.clear()
            data_write.append([datetime.datetime.now(),str(valueInPerc) + '%',amount])
            try:
                gui_update(window, data)
                schedule.run_pending()
                #time.sleep(1)
            except Exception as ex:
                print("sth went wrong - check data")
                print(ex)
        elif event == "Write":
            write("BB:", '1')



    window.close()
