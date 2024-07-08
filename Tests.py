import sys
import os
import time
import tornado.ioloop
from pywebio.input import *
from pywebio.utils import *
from pywebio.html import *
from pywebio.exceptions import *
from pywebio.platform import *
from pywebio.session import *
from pywebio.output import *
import webbrowser
import sqlite3
import re
from tkinter import Tk  # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
import pickle

try:
    def choise_options():
        ans = select("Выберите что нужно сделать:", ['Гражданская война в России XX век', 'It-mir', 'Считать из базы данных', 'Загрузить и запустить тест из БД', 'Выйти'])
        if ans == 'Гражданская война в России XX век':
            global name
            name = input("Введите ваше имя")
            if name == '':
                put_error("Ошибка! Имя не может быть пустым!")
                choise_options()
            else:
                testing_the_functionality_of_the_program()

        elif ans == 'It-mir':
            webbrowser.open("https://it-mir.info")

        elif ans == 'Выйти':
            os.abort()

        elif ans == 'Считать из базы данных':
            name = input("Введите ваше имя")
            if name == '':
                put_error("Ошибка! Имя не может быть пустым!")
                choise_options()
            res_user = f'Пользователь под именем {name} начал просмотр таблиц.\n'
            with open('Log.txt', 'a') as file:
                file.write(res_user)
                confirm = actions('Выбрать новую БД?', ['Да', 'Нет'])
                if confirm == 'Да':
                    put_warning("Выберите БД")
                    Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
                    filename = askopenfilename()
                    f = open('data.dat', 'wb')
                    pickle.dump(filename, f)
                    f.close()
                    if filename == '':
                        put_error(f"Ошибка! Укажите имя и путь файла!")
                        choise_options()
                    put_text(f"Имя и путь файла: {filename}")
                    conn = sqlite3.connect(filename)
                    cur = conn.cursor()
                    work_with_data_base(cur, conn)
                    return cur, conn
                else:
                    try:
                        check_file = os.path.exists('data.dat')  # True
                        if check_file:
                            f = open('data.dat', 'rb')
                            filename = pickle.load(f)
                            conn = sqlite3.connect(filename)
                            cur = conn.cursor()
                            work_with_data_base(cur, conn)
                            return cur, conn
                        else:
                            put_error('Нет сохраненных БД! Пожалуйста, выберите новую.')
                            choise_options()
                    except Exception as e:
                        put_error(f'Ошибка создания или загрузки БД! Сообщите код ошибки: {e}')

        elif ans == 'Загрузить и запустить тест из БД':
            name = input("Введите ваше имя")
            if name == '':
                put_error("Ошибка! Имя не может быть пустым!")
                choise_options()
            check_file = os.path.exists('data.dat')  # True
            if check_file:
                f = open('data.dat', 'rb')
                filename = pickle.load(f)
                conn = sqlite3.connect(filename)
                cur = conn.cursor()
                test_from_base(cur, conn)
                return cur, conn
            else:
                put_error('Нет сохраненных БД! Пожалуйста, выберите новую.')
                choise_options()
except Exception as err:
    with open('log.txt') as f:
        f.write("Ошибка в функции Choice")
        f.write(str(err))
        exit()

# Подключить бд
try:
    def testing_the_functionality_of_the_program():
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS questions(
           questionsid INT PRIMARY KEY,
           question TEXT,
           ans1 TEXT,
           ans2 TEXT,
           ans3 TEXT,
           right_answer TEXT);
        """)
        conn.commit()
        answears_data = [('1',
                          'Внутренняя война между гражданами одной страны, борьба различных социальных и политический '
                          'сил за власть над страной называется:',
                          'гражданская война', 'отечественная война', 'восстание граждан', 'гражданская война'),
                         ('2',
                          'Вмешательство одной или нескольких стран во внутренние дела другой страны или в ее '
                          'взаимоотношения с третьими странами называется:',
                          'интервенция', 'переговоры представителей иностранных держав с Советской властью',
                          'сбор средств для продолжения белого движения', 'интервенция'),
                         ('3', 'Движения под руководством Антонова и Махно относятся к', 'Белому движению',
                          'Красному движению', 'Крестьянскому движению', 'Белому движению'),
                         ('4', 'К белому движению не принадлежат:', 'большевики', 'меньшевики', 'эсеры', 'большевики'),
                         ('5', 'Одной из главных причин гражданской войны в России является:',
                          'союз большевиков с левыми эсерами', 'развернывание интервенции странами Антанты',
                          'приход большевиков к власти и проводимая ими политика',
                          'приход большевиков к власти и проводимая ими политика')
                         ]
        cur.executemany("INSERT OR IGNORE INTO questions VALUES(?, ?, ?, ?, ?, ?);", answears_data)
        conn.commit()

        cur.execute("SELECT questionsid FROM questions ;")
        result = cur.fetchall()
        global ALL_qv
        ALL_qv = len(result)
        global otm
        otm = 0
        for res in result:
            num_vopr = res[0]

            # Выводим все в цикле кроме id
            cur.execute(
                f"SELECT question, ans1, ans2, ans3, right_answer FROM questions WHERE questionsid = {num_vopr} ;")
            cur.fetchall()

            # Получаем вопрос
            cur.execute(f"SELECT question FROM questions WHERE questionsid = {num_vopr} ;")
            base_qv = cur.fetchall()
            base_qv = str(base_qv)
            s1 = re.sub("[(|'|)|,]", "", base_qv)
            s1 = s1.replace("[", "")
            result_qv = s1.replace("]", "")
            # put_text(result_qv)

            # Получаем первый ответ
            cur.execute(f"SELECT ans1 FROM questions WHERE questionsid = {num_vopr} ;")
            base_ans1 = cur.fetchall()
            base_ans1 = str(base_ans1)
            s2 = re.sub("[(|'|)|,]", "", base_ans1)
            s2 = s2.replace("[", "")
            result_ans1 = s2.replace("]", "")
            # put_text(result_ans1)

            # Получаем второй ответ
            cur.execute(f"SELECT ans2 FROM questions WHERE questionsid = {num_vopr} ;")
            base_ans2 = cur.fetchall()
            base_ans2 = str(base_ans2)
            s3 = re.sub("[(|'|)|,]", "", base_ans2)
            s3 = s3.replace("[", "")
            result_ans2 = s3.replace("]", "")
            # put_text(result_ans2)

            # Получаем третий ответ
            cur.execute(f"SELECT ans3 FROM questions WHERE questionsid = {num_vopr} ;")
            base_ans4 = cur.fetchall()
            base_ans4 = str(base_ans4)
            s5 = re.sub("[(|'|)|,]", "", base_ans4)
            s5 = s5.replace("[", "")
            result_ans3 = s5.replace("]", "")
            # put_text(result_ans3)

            # Получаем правильный ответ
            cur.execute(f"SELECT right_answer FROM questions WHERE questionsid = {num_vopr} ;")
            base_ans5 = cur.fetchall()
            base_ans5 = str(base_ans5)
            s6 = re.sub("[(|'|)|,]", "", base_ans5)
            s6 = s6.replace("[", "")
            result_right_answer = s6.replace("]", "")
            # put_text(result_right_answer)

            # Формируем вопросы и ответы
            put_text(f"Вопрос {num_vopr}")
            ans = radio(
                result_qv,
                options=[result_ans1, result_ans2, result_ans3, 'Завершить'])
            confirm = actions('Подтвердить выбор ответа?', ['подтвердить', 'отменить'],
                              help_text='Невозможно выбрать несколько ответов. Ответы также нельзя будет изменить.')
            if confirm == 'подтвердить':

                if ans == '' or ans == None:
                    put_error("Внимание! Так как ответ пуст, он не будет защитан!")
            else:
                ans = radio(
                    result_qv,
                    options=[result_ans1, result_ans2, result_ans3, 'Завершить'])
            put_text("Ваш ответ:", ans)
            if ans == '' or ans == None:
                put_error("Внимание! Так как ответ пуст, он не будет защитан!")

            if ans == result_right_answer:
                otm += 1
            elif ans == 'Завершить':
                put_text(name, "вы набрали:", otm, "из", ALL_qv, "баллов!")
                write_score = ("Пользователь", name, "набрал", otm, "из", ALL_qv, "баллов!")
                write_score = str(write_score)
                f = open('Ответы.txt', 'a')
                f.write(write_score)
                f.close()
                put_warning("Внимание! Страница будет презапущена через 5 секунд!")
                time.sleep(5)
                clear()
                choise_options()

        put_text(name, "вы набрали:", otm, "из", ALL_qv, "баллов!")
        write_score = ("Пользователь", name, "набрал", otm, "из", ALL_qv, "баллов!")
        write_score = str(write_score)
        with open("ответы.txt", "a") as file:
            file.write(write_score)
        put_warning("Внимание! Страница будет презапущена через 5 секунд!")
        time.sleep(5)
        clear()
        choise_options()

except Exception as err:
    with open('log.txt') as f:
        f.write("Ошибка в функции testing_the_functionality_of_the_program")
        f.write(str(err))
        exit()

try:
    def validate_data(cur, conn):
        confirm = actions('Хотите очистить экран и перейти в главное меню?',
                          ['Да', 'В меню работы с БД', 'Перейти без очистки'])
        if confirm == 'Да':
            clear()
            choise_options()
        elif confirm == ('Перейти без очистки'):
            choise_options()
        elif confirm == 'В меню работы с БД':
            work_with_data_base(cur, conn)
        else:
            confirm = actions('Ответ не может быть пустым! Хотите очистить экран и перейти в главное меню или выйти?',
                              ['Да', 'Перейти без очистки', 'Выйти'])
            if confirm == 'Да':
                clear()
                choise_options()
            elif confirm == ('Перейти без очистки'):
                choise_options()
            else:
                sys.exit()

except Exception as err:
    with open('log.txt') as f:
        f.write("Ошибка в функции validate_data")
        f.write(str(err))
        exit()

    try:
        def work_with_data_base(cur, conn):
            # Выводим все таблицы из базы.
            global result_ans
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cur.fetchall()
            put_text("Выводим таблицы:\n")
            all_tables = []
            for table in tables:
                base_ans = str(table)
                str_ans = re.sub("[(|'|)|,]", "", base_ans)
                str_ans = str_ans.replace("[", "")
                result_ans = str_ans.replace("]", "")
                all_tables.append(result_ans)
                put_warning(f'{result_ans}\n')
                # Выбираем таблицу
            choise_table = input("Введите название таблцы")
            if choise_table == '':
                put_error("Ошибка! Введите название таблицы!")
                work_with_data_base(cur, conn)
            elif choise_table not in all_tables:
                put_error("Такой таблицы не существует!")
                work_with_data_base(cur, conn)
            else:
                put_text(f"Вы выбрали таблицу под названием: {choise_table}")
                user_answear = select("Выберите, что вы хотите сделать:",
                                      ['Вывести всю информацию из таблицы', 'Вывести значения из определенного столбца',
                                       'Вывести все данные', 'Редактировать базу данных', 'Выйти'])
                if user_answear == 'Вывести все данные':
                    cur.execute(f"SELECT * FROM sqlite_master;")
                    all_data = cur.fetchall()
                    put_text(all_data)
                    validate_data(cur, conn)
                elif user_answear == 'Вывести всю информацию из таблицы':
                    cur.execute(f"SELECT * FROM {choise_table};")
                    table_info = cur.fetchall()
                    put_text(table_info)
                    validate_data(cur, conn)
                elif user_answear == 'Вывести значения из определенного столбца':
                    cur.execute(f"select * from {choise_table} ;")
                    colnames = cur.description
                    put_text("Имена столбцов:")
                    for row in colnames:
                        put_warning(row[0])
                    # Получаем выбор пользователя и выводим все данные из таблицы
                    chois_row_name = input("Введите название столбца")
                    put_text(f"Вы выбрали: {chois_row_name}")
                    if chois_row_name == '' and chois_row_name not in colnames:
                        put_error(f"Ошибка! Невозможно найти {chois_row_name} в таблице {choise_table}!")
                        work_with_data_base(cur, conn)
                    else:
                        cur.execute(f"SELECT {chois_row_name} FROM {choise_table};")
                        row_info = cur.fetchall()
                        put_text("Значения:")
                        for row in row_info:
                            put_warning(row)
                elif user_answear == 'Редактировать базу данных':
                    answer_red = radio("Выберите, что хотите сделать:",
                                       options=['Удалить таблицу/столбец/строку', 'Изменить значения в таблице',
                                                'Добавить значения', 'Выйти в главное меню'])
                    if answer_red == 'Удалить таблицу/столбец/строку':
                        what_delete = radio("Выберите, что нужно удалить:",
                                            options=['Таблицу', 'Удалить значение с определенным параметром',
                                                     'Ввести команду SQL', 'Выйти в главное меню'])
                        if what_delete == 'Таблицу':
                            dr_table = input("Введите название таблицы для удаления.")
                            confirm = actions('Это действие нельзя отменить, вы уверены, что хотите это сделать?',
                                              ['Да', 'Перейти в главное меню'])
                            if confirm == 'Да':
                                cur.execute(f"DROP TABLE {dr_table}")
                                put_text(f'{dr_table} успешно удалена.')
                                validate_data(cur, conn)
                            else:
                                validate_data(cur, conn)
                        elif what_delete == 'Удалить значение с определенным параметром':
                            cur.execute(f"select * from {choise_table} ;")
                            colnames = cur.description
                            put_text("Имена столбцов:")
                            for row in colnames:
                                put_warning(row[0])
                            column_name = input("Введите название столбца")
                            confirm = actions('Это действие нельзя отменить, вы уверены, что хотите это сделать?',
                                              ['Да', 'Перейти в главное меню'])
                            if confirm == 'Да':
                                if column_name == '' and column_name not in colnames:
                                    put_error(f'Столбец с именем {column_name} не существует!')
                                    work_with_data_base(cur, conn)
                                param = input("Введите параметр. Например =3 или > 3.")
                                if param == '':
                                    put_error('Параметр не должен быть пустым!')
                                    work_with_data_base(cur, conn)
                                cur.execute(f"DELETE FROM {choise_table} WHERE {column_name} {param};")
                                conn.commit()
                                put_text("Выполнено")
                                validate_data(cur, conn)
                            else:
                                validate_data(cur, conn)
                        elif what_delete == 'Ввести команду SQL':
                            text = textarea('Введите команду', rows=4, placeholder='Введите SQL команду')
                            cur.execute(f"{text}")
                            conn.commit()
                            put_text("Выполнено")
                            validate_data(cur, conn)
                        elif what_delete == 'Выйти в главное меню':
                            validate_data(cur, conn)
                    elif answer_red == 'Изменить значения в таблице':
                        what_update = radio("Выберите, что нужно изменить:",
                                            options=['Изменить значение', 'Переименовать таблицу',
                                                     'Ввести команду SQL', 'Выйти в главное меню'])
                        if what_update == 'Переименовать таблицу':
                            two = input("Как вы хотите переименовать таблицу?")
                            if two == '':
                                put_error("Ошибка! Название таблицы не должно быть пустым!")
                                validate_data(cur, conn)
                            s = "ALTER TABLE %s RENAME TO %s"
                            cur.execute(s % (choise_table, two))
                        elif what_update == 'Изменить значение':
                            cur.execute(f"select * from {choise_table} ;")
                            colnames = cur.description
                            put_text("Имена столбцов:")
                            for row in colnames:
                                put_warning(row[0])
                            column_name = input("Введите название столбца:")
                            if column_name == '' and column_name not in colnames:
                                put_error(f'Столбец с именем {column_name} не существует!')
                                work_with_data_base(cur, conn)
                            new_zn = input('Введите новое значение')
                            if new_zn != '':
                                confirm = actions('Нужно ввести условие?',
                                                  ['Да', 'Нет'])
                                if confirm == 'Да':
                                    Condition = input("Введите условие, например: =3, >8, name LIKE 'Федор'")
                                    cur.execute(f"UPDATE {choise_table} SET {column_name} = {new_zn} WHERE {Condition};")
                                    conn.commit()
                                    put_text("Выполнено")
                                    validate_data(cur, conn)
                                else:
                                    cur.execute(f"UPDATE {choise_table} SET {column_name} = {new_zn};")
                                    conn.commit()
                                    put_text("Выполнено")
                                    validate_data(cur, conn)
                            else:
                                put_error("Ошибка! Значение не может быть пустым!")
                                validate_data(cur, conn)
                        elif what_update == 'Ввести команду SQL':
                            text = textarea('Введите команду', rows=4, placeholder='Введите SQL команду')
                            cur.execute(f"{text}")
                            conn.commit()
                            put_text("Выполнено")
                            validate_data(cur, conn)
                        elif what_update == 'Выйти в главное меню':
                            validate_data(cur, conn)
                    elif answer_red == 'Выйти в главное меню':
                        validate_data(cur, conn)
                    elif answer_red == 'Добавить значения':
                        what_add = radio("Выберите, что нужно добавить:",
                                         options=['Таблицу', 'Ввести команду SQL', 'Выйти в главное меню'])
                        if what_add == 'Ввести команду SQL':
                            text = textarea('Введите команду', rows=4, placeholder='Введите SQL команду')
                            cur.execute(f"{text}")
                            conn.commit()
                            put_text("Выполнено")
                            validate_data(cur, conn)

                        elif what_add == 'Выйти в главное меню':
                            validate_data(cur, conn)

                        elif what_add == 'Таблицу':
                            table_add = input("Введите название таблицы")
                            if table_add == '':
                                put_error('Ошибка! Имя таблицы не должно быить пустым!')
                                validate_data(cur, conn)
                            try:
                                How_tables = int(input('Введите колличество столбцов.'))
                                if How_tables == '':
                                    put_error('Колличество строк не может быть пустым!')
                                    validate_data(cur, conn)
                                elif How_tables == 1:
                                    column = input("Введите имя столбца")
                                    type_data = radio("Введите тип данных", options=['INT', 'TEXT', 'STRING'])
                                    if column == '' or type_data == '':
                                        put_error('Имя столбца и/или тип данных не могут быть пустыми значениями!')
                                        validate_data(cur, conn)
                                    data_add = textarea('Выберите нужное значение', rows=4,
                                                        placeholder='Введите значение')
                                    if table_add == '' or data_add == '':
                                        put_error("Ошибка! Имя столбца не может быть пустым!")
                                        validate_data(cur, conn)
                                    cur = conn.cursor()
                                    put_warning(
                                        f'Это SQL запрос: CREATE TABLE IF NOT EXISTS {table_add}({column} {type_data});')
                                    cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_add}({column} {type_data});""")
                                    conn.commit()
                                    cur.execute(f"INSERT INTO {table_add} VALUES(?);", (data_add,))
                                    conn.commit()
                                    put_text('Готово')
                                    validate_data(cur, conn)
                                elif How_tables > 1:
                                    for i in range(How_tables):
                                        column = input("Введите имя столбца")
                                        type_data = radio("Введите тип данных", options=['INT', 'TEXT', 'STRING'])
                                        if column == '' or type_data == '':
                                            put_error('Имя столбца и/или тип данных не могут быть пустыми значениями!')
                                            validate_data(cur, conn)
                                        data_add = textarea('Выберите нужное значение', rows=4,
                                                            placeholder='Введите значение')
                                        if table_add == '' or data_add == '':
                                            put_error("Ошибка! Имя столбца не может быть пустым!")
                                            validate_data(cur, conn)
                                        cur = conn.cursor()
                                        put_warning(
                                            f'Это SQL запрос: CREATE TABLE IF NOT EXISTS {table_add}({column} {type_data});')
                                        if i == How_tables:
                                            cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_add}({column} {type_data});""")
                                            conn.commit()
                                            cur.execute(f"INSERT INTO {table_add} VALUES(?);", (data_add,))
                                            conn.commit()
                                        else:
                                            cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_add}({column} {type_data});""")
                                            conn.commit()
                                            cur.execute(f"INSERT INTO {table_add} VALUES(?);", (data_add,))
                                            conn.commit()
                                    put_text('Готово')
                                    validate_data(cur, conn)

                            except Exception as e:
                                put_error(f'Ошибка! Сообщите создателю этот код: {e}')
                                validate_data(cur, conn)


                            else:
                                cur.execute(f"""CREATE TABLE IF NOT EXISTS {table_add}""")
                                conn.commit()
    except Exception as err:
        with open('log.txt') as f:
            f.write("Ошибка в функции Chek DB")
            f.write(str(err))
            exit()

try:
    def test_from_base(cur, conn):
        otm = 0
        global result_ans
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()
        put_text("Выводим таблицы:\n")
        all_tables = []
        for table in tables:
            base_ans = str(table)
            str_ans = re.sub("[(|'|)|,]", "", base_ans)
            str_ans = str_ans.replace("[", "")
            result_ans = str_ans.replace("]", "")
            all_tables.append(result_ans)
            put_warning(f'{result_ans}\n')
        # Попросить название таблицы, название столбца с номерами вопросов
        choise_table_test = input("Введите название таблицы")
        if choise_table_test == '':
            put_error("Ошибка! Введите название таблицы!")
            test_from_base(cur, conn)
        # Получаем названия столбцов
        put_text('Выводим названия столбцов:')
        cur.execute(f"PRAGMA table_info({choise_table_test});")
        finaly_column = cur.fetchall()
        for column in finaly_column:
           put_warning(column[1])

        id = input("Введите название столбца с номерами вопроса:")
        if id =='':
            put_error("Ошибка! Название не может быть пустым!")
            test_from_base(cur, conn)
        # put_text("Выводим все данные из таблицы")
        # cur.execute(f"SELECT * FROM {choise_table_test};")
        # table_info = cur.fetchall()
        # put_text(table_info)

        column_in_test = input("Введите через запятую названия столбцов, нужные для создания теста.\nПример: Вопросы, ответ, ответ2, ответ3, правильный ответ.\nТест состоит из номера, вопроса, трех вариантов ответа и правильного ответа. Большее колличество вызовет ошибку.")
        if choise_table_test =='':
            put_error("Ошибка! Необходимо обязательно ввести названия столбцов!")
            test_from_base(cur, conn)
        vopros = column_in_test.rsplit(', ')
        all_column_in_DB = [vopros]
        done = radio('Готово, запустить тест?', options=['Да', 'Нет'])
        if done =='Да':
            clear()
            cur.execute(f"SELECT {id} FROM {choise_table_test} ;")
            result = cur.fetchall()
            ALL_Vopr = len(result)
            global start
            start = 0
            for res in result:
                num_vopr = res[0]

                # Выводим все в цикле кроме id
                cur.execute(
                    f"SELECT {column_in_test} FROM {choise_table_test} WHERE {id} = {num_vopr} ;")
                cur.fetchall()

                # Получаем вопрос
                for qves in all_column_inDB:
                    cur.execute(f"SELECT {qves[0]} FROM {choise_table_test} WHERE {id} = {num_vopr} ;")
                    base_qv = cur.fetchall()
                    base_qv = str(base_qv)
                    s1 = re.sub("[(|'|)|,]", "", base_qv)
                    s1 = s1.replace("[", "")
                    result_qv = s1.replace("]", "")
                    # put_text(result_qv)

                # Получаем первый ответ
                for ans1 in all_column_in_DB:
                    cur.execute(f"SELECT {ans1[1]} FROM {choise_table_test} WHERE {id} = {num_vopr};")
                    base_ans1 = cur.fetchall()
                    base_ans1 = str(base_ans1)
                    s2 = re.sub("[(|'|)|,]", "", base_ans1)
                    s2 = s2.replace("[", "")
                    result_ans1 = s2.replace("]", "")
                    # put_text(result_ans1)

                # Получаем второй ответ
                for ans2 in all_column_in_DB:
                    cur.execute(f"SELECT {ans2[2]} FROM {choise_table_test} WHERE {id} = {num_vopr};")
                    base_ans2 = cur.fetchall()
                    base_ans2 = str(base_ans2)
                    s3 = re.sub("[(|'|)|,]", "", base_ans2)
                    s3 = s3.replace("[", "")
                    result_ans2 = s3.replace("]", "")
                    # put_text(result_ans2)

                # Получаем третий ответ
                for ans3 in all_column_in_DB:
                    cur.execute(f"SELECT {ans3[3]} FROM {choise_table_test} WHERE {id} = {num_vopr};")
                    base_ans4 = cur.fetchall()
                    base_ans4 = str(base_ans4)
                    s5 = re.sub("[(|'|)|,]", "", base_ans4)
                    s5 = s5.replace("[", "")
                    result_ans3 = s5.replace("]", "")
                    # put_text(result_ans3)

                # Получаем правильный ответ
                for r_ans in all_column_in_DB:
                    cur.execute(f"SELECT {r_ans[4]} FROM {choise_table_test} WHERE {id} = {num_vopr};")
                    base_ans5 = cur.fetchall()
                    base_ans5 = str(base_ans5)
                    s6 = re.sub("[(|'|)|,]", "", base_ans5)
                    s6 = s6.replace("[", "")
                    result_right_answer = s6.replace("]", "")
                    # put_text(result_right_answer)

                # Формируем вопросы и ответы
                put_text(f"Вопрос {num_vopr}")
                ans = radio(
                    result_qv,
                    options=[result_ans1, result_ans2, result_ans3, 'Завершить'])
                confirm = actions('Подтвердить выбор ответа?', ['подтвердить', 'отменить'],
                                  help_text='Невозможно выбрать несколько ответов. Ответы также нельзя будет изменить.')
                if confirm == 'подтвердить':

                    if ans == '' or ans == None:
                        put_error("Внимание! Так как ответ пуст, он не будет защитан!")
                else:
                    ans = radio(
                        result_qv,
                        options=[result_ans1, result_ans2, result_ans3, 'Завершить'])
                put_warning("Ваш ответ:", ans)
                if ans == '' or ans == None:
                    put_error("Внимание! Так как ответ пуст, он не будет защитан!")

                if ans == result_right_answer:
                    otm += 1
                elif ans == 'Завершить':
                    put_text(name, "вы набрали:", otm, "из", ALL_qv, "баллов!")
                    write_score = ("Пользователь", name, "набрал", otm, "из", ALL_qv, "баллов!")
                    write_score = str(write_score)
                    f = open('Ответы.txt', 'a')
                    f.write(write_score)
                    f.close()
                    put_warning("Внимание! Страница будет презапущена через 5 секунд!")
                    time.sleep(5)
                    clear()
                    choise_options()

            put_text(name, "вы набрали:", otm, "из", ALL_Vopr, "баллов!")
            write_score = ("Пользователь", name, "набрал", otm, "из", ALL_Vopr, "баллов!")
            write_score = str(write_score)
            with open("ответы.txt", "a") as file:
                file.write(write_score)
            put_warning("Внимание! Страница будет презапущена через 5 секунд!")
            time.sleep(5)
            clear()
            choise_options()
except Exception as err:
    with open('log.txt') as f:
        f.write("Ошибка в функции test_from_base")
        f.write(str(err))
        exit()

if __name__=="__main__":
    try:
        webbrowser.open("http://localhost:8080/")
        # Запуск сервера
        start_server(choise_options, port=8080, host='localhost', debug=True, no_browser=True)
        choise_options()
    except Exception as err:
        with open('log.txt') as f:
            f.write(str(err))
            exit()
        #print(err)
