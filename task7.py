import RPi.GPIO as GPIO
import time
import matplotlib.pyplot as plt

#объявляем пины и переменные участвующие в работе
comparator_value = 4
troyka = 17
leds = [21, 20, 16, 12, 7, 8, 25, 24]
dac = [26, 19, 13, 6, 5, 11, 9, 10]
bits = len(dac)
levels = 2**bits
maxvoltage = 3.3
vals = []
times = []

#перевод числа в двоичное представление для комапаратора
def decimal2binary(dec):
      return[int(bin) for bin in bin(dec)[2:].zfill(bits)]

#вывод двоичного представления для комапаратора
def dec2dac(dec):
    for i in range(bits):
        GPIO.output(dac[i], dec[i])

#получение значения сигнала бинарным разбиением с компаратора
def adc(comparator_value):
    znach = [1, 0, 0, 0, 0, 0, 0, 0, 0]
    for sch in range(9):
        dec2dac(znach)
        time.sleep(0.008) #стоп должен стоять между подачей сигнала на компаратор и его считыванием
        comp = GPIO.input(comparator_value)
        if sch == 8:
            val = 0
            for i in range(8):
                val += (2 ** (7 - i)) * znach[i]
            #вывод значения напряжения на диоды leds
            n = int(val / 30)
            for i in range (8):
                if i <= n-1:
                    GPIO.output(leds[i], 1)
                else:
                    GPIO.output(leds[i], 0)
            return val
        elif comp == 0:
            znach[sch] = 0
            znach[sch + 1] = 1
        elif comp == 1:
            znach[sch + 1] = 1

#установка режимов работы модуля rpi.gpio и настройка портов
GPIO.setmode(GPIO.BCM)
GPIO.setup(dac, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(leds, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(comparator_value, GPIO.IN)
GPIO.setup(troyka, GPIO.OUT)
comp = GPIO.input(comparator_value)

try:
    #задаём начальное значение напряжения на конденсаторе (0)
    value = 0
    #задаём первую строку в файле с вычислениями как 0 - 0, чтобы очистить его от предыдущих результатов.
    with open("/home/gr106/Desktop/Scripts/file.txt", "w") as f:
            f.write("0 0" + "\n")
            #Запускаем отсчёт времени
    start_time = time.time()
    GPIO.output(troyka, 1)
    #считываем значения при зарядке конденсатора
    print("происходит зарядка конденсатора")
    while value <= 245:
        current_time = time.time()
        value = adc(comparator_value)
        current_time = time.time()
        timer = current_time - start_time
        #Запись значений в файл
        with open("/home/gr106/Desktop/Scripts/file.txt", "a") as f:
            f.write(str(value) + " " + str(timer) + "\n")
        #запись значений напряжения и времени в соответствующие массивы
        vals.append(value)
        times.append(timer)
        print(value)
    #когда конденсатор заряжен, убираем напряжение с входа и считываем значения при разрядке
    GPIO.output(troyka, 0)
    print("происходит разрядка конденсатора")
    while value >= 5:
        current_time = time.time()
        value = adc(comparator_value)
        current_time = time.time()
        timer = current_time - start_time
        with open("/home/gr106/Desktop/Scripts/file.txt", "a") as f:
            f.write(str(value) + " " + str(timer) + "\n")
        vals.append(value)
        times.append(timer)
        print(value)
finally:
    #в конце концов выводим построенный график и чистим малинку
    GPIO.output(troyka, 0)
    GPIO.cleanup()
    dlit = times[len(times) - 1]
    shag = 3.3 / 256
    period = dlit / len(times)
    chastota = 1 / period
    with open("/home/gr106/Desktop/Scripts/settings.txt", "a") as f:
        f.write("Длительность эксперимента =" + str(dlit) +" период измерений ="+str(period)+" часота дискретизации =" +str(chastota)+" шаг по напряжению =" + str(shag) +" время указано в секундах" + "\n")
    print("Длительность эксперимента =" + str(dlit) +" период измерений ="+str(period)+" часота дискретизации =" +str(chastota)+" шаг по напряжению =" + str(shag) +" время указано в секундах")
    plt.plot(times, vals)
    plt.show()
