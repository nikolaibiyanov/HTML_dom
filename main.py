import re
import threading
import datetime
from datetime import timedelta
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo
import serial
import sqlite3 as sl
import serial.tools.list_ports as port_list
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from matplotlib import dates
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl


root = Tk()  # размеры основного окна
root.geometry("600x480")
"""
httpd = HTTPServer(('localhost', 4443), BaseHTTPRequestHandler)
httpd.socket = ssl.wrap_socket (httpd.socket,
        keyfile="path/to/key.pem",
        certfile='path/to/cert.pem', server_side=True)

httpd.serve_forever()
"""
str_get_text = []
humidity = ''  # влажность в помещении
temperature = ''  # температура в помещении

selection_port = "COM6"
#selection_port = "COM6"
# подключение по умолчанию
try:
    serial = serial.Serial(port="COM6", baudrate=9600, timeout=0.5)
except EXCEPTION:
    print("Port COM6 is closing. Try connect to port in combobox")
now = datetime.datetime.now()
tim = now.strftime("%Y-%m-%d %H:%M:%S")

print("{}.{}.{}  {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))  # 3.5.2017  11:21:33
print("{}:{}:{}".format(now.hour, now.minute, now.second))

label_set_time = ttk.Label()
label_set_time.place(x=485, y=10)  # время на экране

label_send_text_select_port = ttk.Label()

list_port = []

ports = list(port_list.comports())
for p in ports:
    # print(p)
    list_port.append(p)




def selected_com_port(event):
    global selection_port
    selection_port = combobox.get()
    selection_port = selection_port[:5]
    print(selection_port)

    #label_send_text_select_port["text"] = f"{selection_port}"


def click_button_connect():
    print("click Connect")
    global serial
    global selection_port
    if serial.isOpen():
        print(f"Port {serial.port} is already open")
    else:
        try:
            # p = (f"port={selection_port}, baudrate=9600, timeout=0.5")
            # serial = serial.Serial(p)
            #serial = serial.Serial(port="COM6", baudrate=9600, timeout=0.5)
            serial.open()
            #time.sleep(2)
            print(serial.port)
            print("Port opened")
            thread_read_message1 = threading.Thread(target=read_message)
            thread_read_message1.start()

           # read_message()
        #except serial.serialutil.SerialException:
        except:
            print("the port could not be opened")


def update_time():
    global tim
    time_on_display = datetime.datetime.now()
    time_on_display = time_on_display.strftime("%Y-%m-%d %H:%M:%S")
    label_set_time.config(text=f"{time_on_display}")  # время
    root.after(100, update_time)  # Запланировать выполнение этой же функции через 100 миллисекунд


def update_temp():
    try:
        if str_get_text[0] == "":
            pass
        else:
            # print("Update_temp")
            label_temp.config(text=f"{temperature}" + " С")
            label_hudim.config(text=f"{humidity}" + " %")
            root.after(100, update_temp)  # Запланировать выполнение этой же функции через 100 миллисекунд
    except Exception:
        print("NotUpdate_temp")


def check_connection():
    if serial.isOpen():
        text = f"подключено к {selection_port}"
        label_check_connection.config(text=text)
    else:
        label_check_connection.config(text=f"отключен")
    root.after(500, check_connection)


def click_button_stop():
    print("click Stop")


def click_button_start():
    print("click Start")
    if serial.isOpen():
        pass
    else:
        pass


def click_button_disconnect():
    print("click disconnect")
    if serial.isOpen():
        serial.close()
        text = f"port {serial.port} closed"
        print(text)
    else:
        print("port {serial.port} close")


def checkbutton_changed_pump():
    if enabled.get() == 1:
        showinfo(title="Info", message="Включено")
    else:
        showinfo(title="Info", message="Отключено")


def checkbutton_changed_lamp():
    onlamp = str(1)
    offlamp = str(0)
    if stateLamp.get() == "Включено":
        print("lampOn")
        serial.write(onlamp.encode())
    else:
        print("lampOFF")
        serial.write(offlamp.encode())
        # serial.write(bytes(byte0))
    # editor_right.insert("1.0, "(bytes(byte1)))


def to_send():
    pass
    '''if serial.isOpen():
        text = editor.get("1.0", "end")
        serial.write(text.encode())
   else:
        print(f"port not open")
    '''


def visual_diagram():
    con = sl.connect('data_temp_humid.db')
    cur = con.cursor()
    cur.execute('SELECT * FROM data_temp_humid')
    date = []
    fmt = dates.DateFormatter('%Y-%m-%d %H:%M:%S')
    values_temp = []
    values_humid = []
    for row in cur.fetchall():
        values_temp.append(row[1])
        values_humid.append(row[2])
        date.append(datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S"))
    fig, ax = plt.subplots()
    fig.set_size_inches(16, 9)
    plt.subplots_adjust(bottom=0.2, left=0.02, right=0.99, top=0.95)
    ax.xaxis.set_major_formatter(fmt)
    plt.xticks(rotation=90)
    plt.plot_date(date, values_temp, label='temp')
    plt.plot_date(date, values_humid, label='hid')
    plt.legend(bbox_to_anchor=(1, 0.6))
    plt.grid(True)
    plt.title("График за все время")
    axes = plt.axes([0.92, 0.95, 0.05, 0.045])  # кнопка в окне графика
    bnext = Button(axes, '1day', color="yellow")
    bnext.on_clicked(visual_one_day_diagram)
    plt.show()


def heating(value):
    global temperature
    set_temperature = int(scale.get())
    print(set_temperature)
    convector_on = str(1)
    temperature = int(float(temperature))
    convector_off = str(0)
    if set_temperature > temperature:
        print("konvektor ON")
        serial.write(convector_on.encode())
    elif set_temperature < temperature:
        print("konvektor OFF")
        serial.write(convector_off.encode())



def visual_one_day_diagram(val):
    plt.close()
    con = sl.connect('data_temp_humid.db')
    cur = con.cursor()
    day = datetime.datetime.now()  # текущее время
    da = day - timedelta(days=1)  # на день раньше
    #d = datetime.datetime.strftime(da, "%Y-%m-%d %H:%M:%S")
    #cur.execute('SELECT * FROM data_temp_humid WHERE update_time > ?  ', [da])
    cur.execute('SELECT * FROM data_temp_humid WHERE update_time BETWEEN ? AND ?  ', [da, day])
    str_dates = []
    fmt = dates.DateFormatter('%Y-%m-%d %H:%M:%S')
    values_temp = []
    values_humid = []
    fig, ax = plt.subplots()
    fig.set_size_inches(16, 9)
    plt.subplots_adjust(bottom=0.2, left=0.02, right=0.99, top=0.95)
    for row in cur.fetchall():
        if not row:
            showinfo(title="Info", message="в бд нет такого")
        values_temp.append(row[1])
        values_humid.append(row[2])
        str_dates.append(datetime.datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S"))
    cur.close()

    plt.xticks(rotation=90)
    plt.title("График за 1 день")
    ax.xaxis.set_major_formatter(fmt)
    plt.plot_date(str_dates, values_temp, label='temp')
    plt.plot_date(str_dates, values_humid, label='hid')
    plt.legend(bbox_to_anchor=(1, 0.6))
    plt.grid(True)
    plt.show()


def insert_database():
    con = sl.connect('data_temp_humid.db')
    with con:
        try:
            cur = con.cursor()
            cur.execute(
                'CREATE TABLE IF NOT EXISTS data_temp_humid( name_id integer primary key, temperature FLOAT '
                'NOT NULL, humidity FLOAT NOT NULL, update_time timestamp NOT NULL)')
            cur.execute("INSERT INTO data_temp_humid(temperature,humidity,update_time) VALUES (?,?,?)",
                        [temperature, humidity, tim])
            con.commit()
        except:
            print(f"ошибка бд")


def read_message():
    global str_get_text, humidity, temperature
    print("--- Read data to Serial ---")
    while serial.isOpen():
        update_temp()
        str_get_text_new = serial.readline().decode('utf-8')
        str_get_text = str_get_text_new.split("_")
        if str_get_text_new.strip() != '':
            try:
                humidity = re.findall(r'Humidity..\d\d.\d\d', str_get_text_new)
                humidity = ''.join(str(x) for x in humidity)
                humidity = humidity[9:15]
                humidity = float(humidity)
                temperature = re.findall(r'Temperature..\d\d.\d\d', str_get_text_new)
                temperature = ''.join(str(x) for x in temperature)
                temperature = temperature[13:18]
                temperature = float(temperature)
                insert_database()
            except:
                print("Not data temperature and humidity")
    serial.close()




# region canvas

frame = ttk.Frame(borderwidth=1, relief=SOLID, height=60, width=250)  # start stop connect disconnect
frame.pack(anchor=NW, padx=5, pady=5)

btnStart = ttk.Button(frame, text="Start", command=click_button_start, )  # кнопка старт
btnStart.place(x=5, y=5)

btnStop = ttk.Button(frame, text="Stop", command=click_button_stop)  # кнопка стоп
btnStop.place(x=5, y=30)

btnDisconnect = ttk.Button(frame, text="Disconnect", command=click_button_disconnect)  # кнопка Disconnect
btnDisconnect.place(x=85, y=30)

btnVisual = ttk.Button(frame, text="Diagram", command=visual_diagram)  # кнопка Disconnect
btnVisual.place(x=165, y=30)

btnConnect = ttk.Button(frame, text="Connect", command=click_button_connect)  # кнопка connect
btnConnect.place(x=85, y=5)

enabled = IntVar()
checkButtonPump = ttk.Checkbutton(text="Включить насос", variable=enabled, command=checkbutton_changed_pump)
enabled_label = ttk.Label(textvariable=enabled)
enabled_label.place(x=5, y=95)
checkButtonPump.place(x=5, y=75)

stateLampON = "Включено"
stateLampOFF = "Отключено"
stateLamp = StringVar(value=stateLampOFF)
checkButtonLamp = ttk.Checkbutton(text="Включить освещение", variable=stateLamp, offvalue=stateLampOFF,
                                  onvalue=stateLampON, command=checkbutton_changed_lamp)
checkButtonLamp.place(x=5, y=120)

combobox = ttk.Combobox(values=list_port, width=80)
combobox.place(x=5, y=160)

combobox.bind("<<ComboboxSelected>>", selected_com_port)
# schedule.every().minute.at(":02").do(job)
# threading.Thread(target=job).start()

label_time = ttk.Label(font=("helvetica", 15))

label_check_connection = ttk.Label(root, font=("helvetica", 10))
label_check_connection.pack()

frame_low_right = ttk.Frame(borderwidth=1, relief=SOLID)  # правая рамка
frame_low_right.place(x=300, y=200, width=280, height=140)
editor_right = Text(frame_low_right)  # правое поле ввода
editor_right.place(x=5, y=35, width=250, height=100)
label_send_mes = ttk.Label(frame_low_right, font=("helvetika", 10), text="Отправить сообщение")
label_send_mes.place(y=5)
button_send_mes = ttk.Button(frame_low_right, text="отправить сообщение", command=to_send)
button_send_mes.place(x=140, y=5)

frame_low_left = ttk.Frame(borderwidth=1, relief=SOLID)  # левая рамка
frame_low_left.place(x=5, y=200, width=280, height=140)
editor_left = Text(frame_low_left)  # левое поле ввода
editor_left.place(x=5, y=35, width=250, height=100)
label_geting_mes = ttk.Label(frame_low_left, font=("helvetika", 10), text="Принятое сообщение")
label_geting_mes.place(y=5)
button_get_mes = ttk.Button(frame_low_left, text="принять сообщение", command=read_message)
button_get_mes.place(x=140, y=5)

label_temp = ttk.Label(font=("helvetika", 10), text="температура")
label_temp.place(x=550, y=35)
label_hudim = ttk.Label(font=("helvetika", 10), text="влажность")
label_hudim.place(x=550, y=55)

scale_var = DoubleVar()  # ползунок
scale = Scale(variable=scale_var, from_=5, to=80, orient="horizontal", command=heating)
scale.pack()

# endregion
update_time()

check_connection()
thread_read_message = threading.Thread(target=read_message)
thread_read_message.start()
root.mainloop()
