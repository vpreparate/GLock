# Импортируем необходимые модули для работы
import sys # Модуль для работы с параметрами и функциями системы
import httpx # Библиотека для выполнения HTTP-запросов
import csv # Модуль для работы с CSV-файлами
import requests  # Библиотека для выполнения HTTP-запросов
from bs4 import BeautifulSoup # Импортируем BeautifulSoup для парсинга HTML

# Импорт необходимых классов интерфейса
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                             QPushButton, QVBoxLayout, QScrollArea, QCheckBox, 
                             QWidget, QDialog, QMessageBox, QTableWidgetItem, QFileDialog)


# Определяем главный класс приложения, наследующий от QMainWindow
class UrlInputApp(QMainWindow):
    def __init__(self): # Метод инициализации
        super().__init__() # Вызов инициализации родительского класса

        self.selected_classes = []  # Список выбранных классов
        self.class_descriptions = {}  # Словарь для хранения описаний классов
        self.all_classes = []  # Все найденные классы
        self.class_checkboxes = {}  # Словарь для хранения чекбоксов для классов
        self.init_ui() # Инициализация пользовательского интерфейса

    def init_ui(self): # Метод для настройки пользовательского интерфейса
        self.setWindowTitle("URL Analyzer") # Установка заголовка окна
        # Настройка стиля окна
        self.setStyleSheet("background-color: #222; color: #fff;")

        # Основной виджет и компоновка
        self.central_widget = QWidget() # Главный виджет
        # Указываем центральный виджет окна
        self.setCentralWidget(self.central_widget)
        # Создаем вертикальный компоновщик
        self.layout = QVBoxLayout(self.central_widget)

        # Поле ввода URL\\\\
        # Метка для поля ввода URL
        self.url_label = QLabel("Введите URL страницы:")
        # Поле ввода для URL
        self.url_input = QLineEdit()
        # Добавляем метку в компоновщик
        self.layout.addWidget(self.url_label)
        # Добавляем поле ввода в компоновщик
        self.layout.addWidget(self.url_input)

        # Кнопка анализа URL\\\\
        # Кнопка для запуска анализа
        self.analyze_button = QPushButton("Анализировать")
        # Подключаем событие нажатия к методу анализа
        self.analyze_button.clicked.connect(self.analyze_url)
        # Добавляем кнопку в компоновщик
        self.layout.addWidget(self.analyze_button)

        # Поле для поиска класса\\\\
        # Метка для поля поиска классов
        self.search_class_label = QLabel("Поиск класса:")
        # Поле ввода для поиска класса
        self.search_class_input = QLineEdit()
        # Подключаем событие изменения текста к фильтрации классов
        self.search_class_input.textChanged.connect(self.filter_classes)
        # Добавляем метку в компоновщик
        self.layout.addWidget(self.search_class_label)
        # Добавляем поле ввода в компоновщик
        self.layout.addWidget(self.search_class_input)

        # Поле для ввода нового класса
        #self.new_class_label = QLabel("Добавить новый класс:")
        #self.new_class_input = QLineEdit()
        #self.layout.addWidget(self.new_class_label)
        #self.layout.addWidget(self.new_class_input)

        # Кнопка для добавления нового класса
        #self.add_class_button = QPushButton("Добавить класс")
        #self.add_class_button.clicked.connect(self.add_class)
        #self.layout.addWidget(self.add_class_button)

        # Список классов и их выбор\\\\
        # Контейнер для прокручиваемого списка классов
        self.class_container = QScrollArea()
        # Сделаем контейнер изменяемым по размеру
        self.class_container.setWidgetResizable(True)
        # Виджет для отображения классов
        self.classes_widget = QWidget()
        # Вертикальный компоновщик для классов
        self.class_layout = QVBoxLayout(self.classes_widget)
        # Устанавливаем виджет в контейнер прокрутки
        self.class_container.setWidget(self.classes_widget)
        # Добавляем контейнер в компоновщик
        self.layout.addWidget(self.class_container)

        # Кнопка для настройки пагинации\\\
        # Кнопка для перехода к следующему шагу
        self.next_button = QPushButton("Далее")
        # Подключаем событие нажатия к методу настройки пагинации
        self.next_button.clicked.connect(self.setup_pagination)
        # Добавляем кнопку в компоновщик
        self.layout.addWidget(self.next_button)

        # Показать окно\\\\
        # Устанавливаем размер окна
        self.resize(400, 600)
        # Отображаем окно
        self.show()

    def analyze_url(self): # Метод для анализа URL
        # Получаем текст из поля ввода URL и удаляем лишние пробелы
        url = self.url_input.text().strip()
        if url:  # Если URL не пустой
            try:
                # Выполняем GET-запрос по указанному URL
                response = httpx.get(url)
                # Проверяем на наличие ошибок в ответе
                response.raise_for_status()
                # Парсим содержимое страницы
                soup = BeautifulSoup(response.content, 'html.parser')

                # Извлечение и создание множества классов из всех элементов с классом
                classes = {cls for element in soup.find_all(class_=True) for cls in element["class"]}

                # Добавление описания для каждого класса
                for cls in classes: # Для каждого найденного класса
                    # Находим первый элемент с этим классом
                    first_element = soup.find(class_=cls)
                    # Получаем текст из найденного элемента или устанавливаем "Нет данных"
                    description = first_element.get_text(strip=True) if first_element else "Нет данных"
                    # Сохраняем описание класса в словаре
                    self.class_descriptions[cls] = description
                # Показываем найденные классы с описанием
                self.show_classes(classes)
            except Exception as e: # Обработка исключений
                # Сообщение об ошибке
                QMessageBox.critical(self, "Ошибка", f"Ошибка при получении данных: {e}")
        # Если URL пустой
        else:
            # Сообщение об ошибке
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите корректный URL.")

    def show_classes(self, classes):
        # Очистка предыдущих классов\\\\
        # Проходим по всем элементам в layout в обратном порядке
        for i in reversed(range(self.class_layout.count())):
            # Удаляем виджеты, чтобы очистить предыдущие классы
            self.class_layout.itemAt(i).widget().deleteLater()
        # Преобразуем входные данные (множество классов) в список
        self.all_classes = list(classes)

        # Создание чекбоксов для каждого класса с описанием\\\\
        # Очистка словаря предыдущих чекбоксов
        self.class_checkboxes.clear()
        # Для каждого класса в списке
        for cls in self.all_classes:
            # Создаем новый чекбокс с названием класса
            checkbox = QCheckBox(cls)
            # Подключаем сигнал изменения состояния чекбокса к методу обновления выбранных классов
            checkbox.stateChanged.connect(self.update_selected_classes)
            # Создаем метку с описанием класса (или "Нет данных", если описание отсутствует)
            description_label = QLabel(self.class_descriptions.get(cls, "Нет данных"))
            # Добавляем чекбокс в layout
            self.class_layout.addWidget(checkbox)
            self.class_layout.addWidget(description_label)  # Добавляем описание ниже чекбокса
            self.class_checkboxes[cls] = checkbox  # Сохраняем ссылку на чекбокс

    def update_selected_classes(self):
        # Обновление списка выбранных классов\\\\
        self.selected_classes = [ # Проходим по всем чекбоксам
            cls for cls, checkbox in self.class_checkboxes.items() 
            if checkbox.isChecked() # Проверяем, отмечен ли чекбокс
        ]
        print("Выбранные классы:", self.selected_classes)  # Вывод для отладки

    #def add_class(self):
        #new_class = self.new_class_input.text().strip()
        #if new_class and new_class not in self.all_classes:  # Убедитесь, что класс не дублируется
            #self.all_classes.append(new_class)  # Добавляем новый класс
            #self.class_descriptions[new_class] = "Нет данных"  # Устанавливаем значение описания по умолчанию
            #self.show_classes(self.all_classes)  # Обновляем отображение классов
            #self.new_class_input.clear()  # Очищаем поле ввода после добавления
        #else:
            #QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите уникальный класс.")

    def filter_classes(self):
        # Получаем текст поиска, удаляем лишние пробелы и приводим к нижнему регистру
        search_text = self.search_class_input.text().strip().lower()
        # Проходим по всем классам в списке
        filtered_classes = [  # Проверяем наличие текста поиска в названии класса или его описании
            cls for cls in self.all_classes 
            if search_text in cls.lower() or search_text in self.class_descriptions.get(cls, "").lower()
        ]
        # Вызываем функцию для отображения отфильтрованных классов
        self.show_classes(filtered_classes)

    def setup_pagination(self):
        print("Кнопка 'Далее' нажата")  # Проверка нажатия кнопки
        if not self.selected_classes: # Проверяем, пуст ли список выбранных классов
            print("Нет выбранных классов!")  # Сообщение об отсутствии выбранных классов
            # Показываем окно с предупреждением
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите хотя бы один класс для продолжения.")
            return

        print("Выбранные классы для пагинации:", self.selected_classes)  # Вывод выбранных классов

        try:
            # Создаем диалоговое окно для пагинации с выбранными классами и их описаниями
            self.pagination_dialog = PaginationDialog(self.selected_classes, self.class_descriptions, self)
            # Показываем диалоговое окно
            self.pagination_dialog.show()
            print("Окно пагинации должно было открыться.")
        except Exception as e: # Обработка исключений
            print(f"Ошибка при открытии окна пагинации: {e}") # Вывод сообщения об ошибке
        

# Определяем класс для окна пагинации, наследующий от QDialog\\\\
class PaginationDialog(QDialog):
    # Метод инициализации
    def __init__(self, selected_classes, class_descriptions, parent=None):
        # Вызов инициализации родительского класса
        super().__init__(parent)
        print("Создание окна пагинации...")
        # Сохраняем выбранные классы
        self.selected_classes = selected_classes
        # Сохраняем описания классов
        self.class_descriptions = class_descriptions
        # Инициализация пользовательского интерфейса
        self.init_ui()

    def init_ui(self): # Метод для настройки пользовательского интерфейса
        # Сообщение о начале настройки интерфейса
        print("Инициализация интерфейса для диалога пагинации...")
        # Установка заголовка окна
        self.setWindowTitle("Настройка пагинации")
        # Настройка стиля окна
        self.setStyleSheet("background-color: #222; color: #fff;")
        # Создаем вертикальный компоновщик
        self.layout = QVBoxLayout(self)

        # Поле ввода полного URL без параметра страницы
        self.url_input = QLineEdit()
        # Установка текста-заполнителя
        self.url_input.setPlaceholderText("Полный URL Без параметра страницы")
        # Добавление поля ввода в компоновщик
        self.layout.addWidget(self.url_input)

        # Поле для ввода переменной, отвечающей за номер страницы
        self.page_param_input = QLineEdit()
        # Установка текста-заполнителя
        self.page_param_input.setPlaceholderText("Переменная для номера страницы (например, page)")
        # Добавление поля ввода в компоновщик
        self.layout.addWidget(self.page_param_input)

        # Поля ввода для пагинации
        self.start_page_input = QLineEdit()
        self.start_page_input.setPlaceholderText("Начальная страница (число)")
        self.layout.addWidget(self.start_page_input)

        self.end_page_input = QLineEdit()
        self.end_page_input.setPlaceholderText("Конечная страница (число)")
        self.layout.addWidget(self.end_page_input)

        self.increment_input = QLineEdit()
        self.increment_input.setPlaceholderText("Шаг инкремента (число)")
        self.layout.addWidget(self.increment_input)

        # Поле для поиска классов
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск классов")
        self.layout.addWidget(self.search_input)

        # Список классов и их выбор\\\\
        # Создаем прокручиваемую область для классов
        self.class_container = QScrollArea()
        # Делаем прокручиваемую область изменяемой по размеру
        self.class_container.setWidgetResizable(True)
        # Создаем виджет для отображения классов
        self.classes_widget = QWidget()
        # Вертикальный компоновщик для классов
        self.class_layout = QVBoxLayout(self.classes_widget)
        # Устанавливаем виджет в прокручиваемую область
        self.class_container.setWidget(self.classes_widget)
        # Добавляем прокручиваемую область в компоновщик
        self.layout.addWidget(self.class_container)

        # Заполнение списка классов\\\\
        # Вызываем метод для заполнения списка классов
        self.populate_class_view()

        # Кнопка для запуска сбора данных
        self.run_button = QPushButton("Запустить сбор данных")
        # Подключаем сигнал нажатия кнопки к методу сбора данных
        self.run_button.clicked.connect(self.collect_and_save_data)
        # Добавляем кнопку в компоновщик
        self.layout.addWidget(self.run_button)

        # Создаем список для хранения собранных данных
        self.collected_data = []

        self.resize(400, 400)  # Устанавливаем размер окна

    def populate_class_view(self): # Метод для заполнения списка классов
        # Очистка предыдущих классов\\\
        # Проходим по всем элементам в обратном порядке
        for i in reversed(range(self.class_layout.count())):
            # Удаляем виджеты, чтобы очистить предыдущие классы
            self.class_layout.itemAt(i).widget().deleteLater()

        # Заполнение списка классов\\\
        # Для каждого класса в списке выбранных классов
        for cls in self.selected_classes:
            # Создаем чекбокс для класса
            checkbox = QCheckBox(cls)
            # Устанавливаем чекбокс в состояние "отмечен"
            checkbox.setChecked(True)
            # Подключаем сигнал изменения состояния чекбокса к методу обновления выбранных классов
            checkbox.stateChanged.connect(self.update_selected_classes)
            # Создаем метку с описанием класса (или "Нет описания", если описание отсутствует)
            description_label = QLabel(self.class_descriptions.get(cls, "Нет описания"))
            # Добавляем чекбокс в компоновщик
            self.class_layout.addWidget(checkbox)
            # Добавляем описание ниже чекбокса в компоновщик
            self.class_layout.addWidget(description_label)

    def update_selected_classes(self): # Метод для обновления списка выбранных классов
        # Создание списка выбранных классов на основе состояния чекбоксов
        self.selected_classes = [checkbox.text() for checkbox in self.class_layout.findChildren(QCheckBox) if checkbox.isChecked()]
        # Вывод списка выбранных классов для отладки
        print("Выбранные классы в пагинации:", self.selected_classes)

    def collect_and_save_data(self): # Метод для сбора и сохранения данных\\\\
        # Получаем и очищаем URL из поля ввода
        url = self.url_input.text().strip()
        # Получаем и очищаем имя параметра страницы
        page_param = self.page_param_input.text().strip()

        try:
            # Преобразуем значения из полей ввода начальной и конечной страницы,
            #а также инкремента в целые числа
            start_page = int(self.start_page_input.text())
            end_page = int(self.end_page_input.text())
            increment = int(self.increment_input.text())
        # Если значения не являются числами, показываем сообщение об ошибке
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Пожалуйста, убедитесь, что начальная, конечная страницы и шаг инкремента являются числами.")
            return # Завершаем выполнение метода, если возникла ошибка

        self.collected_data = []  # Сброс данных перед новым сбором

        # Цикл по диапазону страниц с указанным шагом
        for page in range(start_page, end_page + 1, increment):
            # Формирование полного URL с параметром страницы
            full_url = f"{url}?{page_param}={page}"
            print(f"Запрос к: {full_url}")

            try:
                # Выполнение GET-запроса
                response = requests.get(full_url)
                response.raise_for_status()  # Проверка на ошибки HTTP
                # Парсинг содержимого страницы с помощью BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')

                # Временные списки для собранных данных
                temp_data = [] # Временный список для хранения собранных данных
                current_entry = {} # Словарь для текущей записи

                # Сбор данных по выбранным классам\\\\
                # Проходим по каждому выбранному классу
                for class_name in self.selected_classes:
                    # Находим все элементы с данным классом
                    elements = soup.find_all(class_=class_name)

                    # Назначаем значения текущему словарю по каждому классу
                    # Извлекаем текст из найденных элементов
                    current_entry[class_name] = [element.get_text(strip=True) for element in elements]

                #  Добавляем только те элементы, которые имеют данные\\\\
                # Проверяем, есть ли данные в текущем словаре
                if current_entry:
                    # Приводим к списку, чтобы заполнять только те поля, которые есть\\\
                    # Находим максимальную длину значений
                    max_length = max(len(v) for v in current_entry.values())
                    # Проходим по индексам до максимальной длины
                    for i in range(max_length):
                        # Создаем запись, учитывая, что может не быть данных для всех классов
                        entry = {class_name: current_entry[class_name][i] if i < len(current_entry[class_name]) else '' for class_name in self.selected_classes}
                        # Добавляем запись во временный список
                        temp_data.append(entry)

                # Добавляем собранные данные в основной список
                self.collected_data.extend(temp_data)

            except Exception as e: # Обработка исключений, если что-то пошло не так
                QMessageBox.critical(self, "Ошибка", f"Ошибка при обработке страницы {page}: {e}")

        # Сохранение собранных данных в CSV
        self.save_to_csv() # Вызываем метод для сохранения данных в CSV

    def save_to_csv(self): # Метод для сохранения собранных данных в CSV файл
        if not self.collected_data: # Проверяем, есть ли данные для сохранения
            QMessageBox.warning(self, "Ошибка", "Нет данных для сохранения.")
            return # Завершаем выполнение метода

        # Запись в CSV\\\\
        # Открываем файл для записи
        with open('output_data.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file) # Создаем CSV writer

            # Запись заголовка\\\
            # Записываем заголовок файла из выбранных классов
            writer.writerow(self.selected_classes)

            # Запись строк данных\\\
            # Проходим по каждой записи в собранных данных
            for entry in self.collected_data:
                # Формируем строку, получая данные по каждому классу
                row = [entry.get(class_name, '') for class_name in self.selected_classes]
                # Записываем строку в CSV файл
                writer.writerow(row)
        # Сообщаем пользователю о завершении сохранения
        QMessageBox.information(self, "Сохранение завершено", "Данные успешно сохранены в output_data.csv")

if __name__ == "__main__": # Проверяем, что скрипт запущен как основная программа
    app = QApplication(sys.argv) # Создаем экземпляр приложения с аргументами командной строки
    # Устанавливаем стиль интерфейса приложения на 'Fusion' для улучшения внешнего вида
    app.setStyle('Fusion')
    # Создаем экземпляр класса UrlInputApp (главного окна приложения)
    window = UrlInputApp()
    # Отображаем главное окно приложения
    window.show()
    # Запускаем цикл обработки событий приложения и корректно завершаем выполнение при выходе
    sys.exit(app.exec_())
        
            
        

        

