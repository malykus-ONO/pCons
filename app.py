import streamlit as st
import re
import os

def parse_process_line(line):
    # Пример: "name, 24, 4m+12t, 0, #000000"
    pattern = r'^(.*?),\s*(\d+),\s*([\dmt+\s]+),\s*([\d.]+),\s*(#[0-9A-Fa-f]{6})$'
    match = re.match(pattern, line.strip())
    if not match:
        return None
    name = match.group(1)
    life = int(match.group(2))
    active_str = match.group(3)
    urgency = float(match.group(4))
    color = match.group(5)
    # Парсим активную фазу
    min_match = re.search(r'(\d+)m', active_str)
    tick_match = re.search(r'(\d+)t', active_str)
    active_minutes = int(min_match.group(1)) if min_match else 0
    active_ticks = int(tick_match.group(1)) if tick_match else 0
    return {
        "Имя процесса": name,
        "Жизнь процесса (мин)": life,
        "Активная фаза (мин)": active_minutes,
        "Активная фаза (тики)": active_ticks,
        "Срочность": urgency,
        "Цвет": color
    }

def calc_gravity(active_minutes, active_ticks, life_minutes):
    active = active_minutes + (active_ticks * 5 / 60)
    return round(active / life_minutes, 3) if life_minutes else 0

if "processes" not in st.session_state:
    st.session_state.processes = []

st.title("Добавление процесса")

with st.form("process_form"):
    name = st.text_input("Имя процесса")
    life_minutes = st.number_input("Жизнь процесса (минуты)", min_value=1, step=1)
    active_minutes = st.number_input("Активная фаза (минуты)", min_value=0, step=1)
    active_ticks = st.number_input("Активная фаза (тики, 1 тик = 5 сек)", min_value=0, step=1)
    urgency = st.selectbox("Срочность", options=[0, 0.5, 1])
    color = st.color_picker("Цвет", "#00FF00")
    submitted = st.form_submit_button("Добавить")

if submitted:
    gravity = calc_gravity(active_minutes, active_ticks, life_minutes)
    st.session_state.processes.append({
        "Имя процесса": name,
        "Жизнь процесса (мин)": life_minutes,
        "Активная фаза (мин)": active_minutes,
        "Активная фаза (тики)": active_ticks,
        "Срочность": urgency,
        "Цвет": color,
        "Гравитация": gravity
    })

st.subheader("Импорт строки процесса")
import_line = st.text_input("Строка формата: name, 24, 4m+12t, 0, #000000")
if st.button("Импортировать"):
    proc = parse_process_line(import_line)
    if proc:
        gravity = calc_gravity(proc["Активная фаза (мин)"], proc["Активная фаза (тики)"], proc["Жизнь процесса (мин)"])
        proc["Гравитация"] = gravity
        st.session_state.processes.append(proc)
        st.success("Импортировано!")
    else:
        st.error("Ошибка формата строки")

st.subheader("Список процессов")
for i, proc in enumerate(st.session_state.processes):
    col1, col2 = st.columns([5,1])
    with col1:
        st.text(f"{proc['Имя процесса']} | Жизнь: {proc['Жизнь процесса (мин)']} мин | Актив: {proc['Активная фаза (мин)']}м+{proc['Активная фаза (тики)']}т | Срочность: {proc['Срочность']} | Цвет: {proc['Цвет']} | Гравитация: {proc['Гравитация']}")
    with col2:
        if st.button("Удалить", key=f"del_{i}"):
            st.session_state.processes.pop(i)
            st.experimental_rerun()

def export_processes(processes):
    lines = []
    for p in processes:
        active_str = f"{p['Активная фаза (мин)']}m+{p['Активная фаза (тики)']}t"
        line = f'"{p["Имя процесса"]}", {p["Жизнь процесса (мин)"]}, {active_str}, {p["Срочность"]}, {p["Цвет"]}'
        lines.append(line)
    return "\n".join(lines)

if st.button("Экспортировать в processes.py"):
    content = export_processes(st.session_state.processes)
    with open("processes.py", "w", encoding="utf-8") as f:
        f.write("# Экспортированные процессы\n")
        f.write("processes = [\n")
        for line in content.splitlines():
            f.write(f"    {line},\n")
        f.write("]\n")
    st.success("Экспортировано в processes.py")

if st.button("Очистить все процессы"):
    st.session_state.processes = []
    st.experimental_rerun()
