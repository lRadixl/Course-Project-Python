import yaml
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Radiobutton, StringVar

CONFIG = 'config.yml'
SAVE_FILE = 'results.yml'


def get_all_tests():
    with open(CONFIG, 'r') as f:
        config = yaml.safe_load(f.read())
    return config['tests']


def get_test(filename):
    with open(filename, 'r') as f:
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
    with open(SAVE_FILE, 'r') as f:
        prev_result = yaml.safe_load(f.read()) or {}

    user_data = prev_result.get(username, None)
    if user_data:
        prev_result[username].update(result)
    else:
        prev_result.update({username: result})

    with open(SAVE_FILE, 'w') as f:
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
        messagebox.showinfo("Question", f"{question['question']}\nВаша відповідь: {user_answer}\nПравельна відповідь: {correct_answer}")


def start_test(test):
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
    messagebox.showinfo("Test Time", 'You done your test in ' + str(total_time_spend))
    result = {test['title']: {
            'result': test_result,
            'time_spend': str(total_time_spend),
            'max_score': len(questions),
            'user_score': correct_answers,
        }
    }
    save_result(username, result)
    show_answers(questions, test_result)


def main():
    tests = get_all_tests()
    test = select_test(tests)
    start_test(test)


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    main()
    root.mainloop()
    