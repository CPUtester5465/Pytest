import os
import openpyxl

# Указываем путь к директории, в которой будет создан файл
filepath = "/home/tim/test-scripts/FIBONACHI/"

# Создаем новый документ Excel
workbook = openpyxl.Workbook()

# Получаем активный лист документа
worksheet = workbook.active

# Заполняем таблицу значениями Фибоначчи
for i in range(1, 21):
    for j in range(1, 21):
        if i == 1 or i == 2 or j == 1 or j == 2:
            worksheet.cell(row=i, column=j).value = 1
        else:
            worksheet.cell(row=i, column=j).value = worksheet.cell(row=i-1, column=j).value + worksheet.cell(row=i-2, column=j).value

# Убедитесь, что директория существует
if not os.path.exists(filepath):
    os.makedirs(filepath)

# Указываем полный путь к файлу
filename = os.path.join(filepath, "fibonacci.xlsx")

# Сохраняем документ Excel в указанной директории
workbook.save(filename)
