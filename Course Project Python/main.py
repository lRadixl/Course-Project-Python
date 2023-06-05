import yaml
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Radiobutton, StringVar

CONFIG = 'config.yml'
SAVE_FILE = 'results.yml'


def get_all_tests():
    with open(CONFIG, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f.read())
    return config['tests']


def get_test(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        test = yaml.safe_load(f.read())
    return test


def select_test(tests):
    test_options = "\n".join([f'{i+1}: {test["title"]}' for i, test in enumerate(tests)])
    test_number = simpledialog.askinteger("Вибір теста", f"Будь ласка оберіть тест:\n{test_options}", minvalue=1, maxvalue=len(tests)) - 1
    if test_number not in range(len(tests)):
        messagebox.showerror("Error", "Invalid Test Number")
        return select_test(tests)
    return get_test(tests[test_number]['filename'])


def save_result(username, result):
    with open(SAVE_FILE, 'r', encoding='utf-8') as f:
        prev_result = yaml.safe_load(f.read()) or {}

    user_data = prev_result.get(username, None)
    if user_data:
        prev_result[username].update(result)
    else:
        prev_result.update({username: result})

    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(prev_result, f, indent=4)


def get_response(question):
    answer_window = Toplevel()
    answer_window.title("Питання")
    answer_var = StringVar()

    question_label = tk.Label(answer_window, text=question['question'])
    question_label.pack()

    for k, v in question['answers'].items():
        answer_button = Radiobutton(answer_window, text=f'{k}: {v}', variable=answer_var, value=k)
        answer_button.pack(anchor='w')

    answer_button = tk.Button(answer_window, text='Submit', command=answer_window.destroy)
    answer_button.pack()
    answer_window.wait_window()

    return answer_var.get()


def show_answers(questions, results):
    x = messagebox.askyesno("Результат", "Ви хочете переглянути результат?")
    if not x:
        return

    for question in questions:
        user_answer = results[question['id']]['user_answer']
        correct_answer = question['correct_answer']
        messagebox.showinfo("Question", f"{question['question']}\nВаша відповідь: {user_answer}\nПравильна відповідь: {correct_answer}")


def start_test(test, instruction_window):
    instruction_window.destroy()

    username = simpledialog.askstring("Ім'я", "Введіть ваше ім'я")
    start = datetime.now()
    print('Start timer')

    questions = test['questions']
    test_result = {}
    correct_answers = 0

    for question in questions:
        response = get_response(question)
        is_correct = response == question['correct_answer']
        if is_correct:
            correct_answers += 1
        test_result[question['id']] = dict(
            correct_answer=question['correct_answer'],
            user_answer=response,
        )
    end = datetime.now()
    total_time_spend = end - start
    messagebox.showinfo("Test Time", 'Ви виконали тест за ' + str(total_time_spend))
    result = {test['title']: {
            'result': test_result,
            'time_spend': str(total_time_spend),
            'max_score': len(questions),
            'user_score': correct_answers,
        }
    }
    save_result(username, result)
    show_answers(questions, test_result)


def show_instructions(test):
    instruction_window = Toplevel()
    instruction_window.title("Інструкція")

    instructions = test.get('instructions', '1.Введіть ваше імя в поле для введення.\n 2.Для кожного питання у тесті\n Прочитайте питання.\n Оберіть один з варіантів відповідей, використовуючи радіокнопки.\n Натисніть кнопку "Submit", щоб перевірити вашу відповідь та перейти до наступного питання.\n 3.Після закінчення тесту зявиться повідомлення з часом, витраченим на тестування.\n 4. Результати тесту, включаючи ваші відповіді та правильні відповіді, будуть збережені в файлі "results.yml".\n 5. Якщо ви бажаєте, можете переглянути ваші відповіді та правильні відповіді на кожне питання.\n 6. Закрийте програму після завершення тестування.')
    instruction_label = tk.Label(instruction_window, text=instructions)
    instruction_label.pack()

    start_test_button = tk.Button(instruction_window, text='Почати тест', command=lambda: start_test(test, instruction_window))
    start_test_button.pack()

    instruction_window.mainloop()


def main():
    tests = get_all_tests()
    test = select_test(tests)
    show_instructions(test)


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    main()
    root.mainloop()
