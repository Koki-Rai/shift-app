from ortools.sat.python import cp_model
import pandas as pd

members = [
        {"name": "Aさん", "in_shift": True},
        {"name": "Bさん", "in_shift": True},
        {"name": "Cさん", "in_shift": True},
        {"name": "Dさん", "in_shift": True},
        {"name": "Eさん", "in_shift": True},
        {"name": "Zさん", "in_shift": False},
    ]
bands = [
        {
            "band": "バンドX",
            "unavailable_slots": ["午前"],
            "Bj": "Aさん",
            "Md": "Bさん",
            "Gt": "Zさん",        # 演奏専門のZさん
            "Bs": "なし",
            "Fd": "なし",
            "Db": "なし",
            "other": "",
        },
        {
            "band": "バンドY",
            "unavailable_slots": [],
            "Bj": "Cさん",
            "Md": "なし",
            "Gt": "なし",
            "Bs": "なし",
            "Fd": "なし",
            "Db": "なし",
            "other": "",
        },
    ]
    
slots = ["午前", "午後", "夕方"]
roles = ["レジ", "調理"]
role_demand = {"レジ": 1, "調理": 1}


def solve_shift(band_placement):
    unavailable_pairs = []

    # シフトに入る人の名前だけを取り出す
    employees = []
    for member in members:
        if member["in_shift"]:
            employees.append(member["name"])
    # シフトメンバーのバンド演奏時間をシフト不可にする
    # 演奏連動：配置されたバンドの演奏時間に、そのメンバー（シフト参加者）を不可にする
    instrument_keys = ["Bj", "Md", "Gt", "Bs", "Fd", "Db"]
    for slot, band_name in band_placement.items():
        if band_name == "（なし）":
            continue
        for band in bands:
            if band["band"] == band_name:
                for inst in instrument_keys:
                    cell = band[inst]
                    if cell == "なし" or cell == "":
                        continue
                    # バグ注意("、"で区切らない場合とか)
                    for player_name in cell.split("、"):
                        if player_name in employees:
                            unavailable_pairs.append((player_name, slot))
    # --- モデル ---
    model = cp_model.CpModel()
    x = {}
    for employee in employees:
        for slot in slots:
            for role in roles:
                x[(employee, slot, role)] = model.NewBoolVar(f"x_{employee}_{slot}_{role}")

    # 制約1: 各枠・各役割の人数はちょうど必要数
    for slot in slots:
        for role in roles:
            model.Add(sum(x[(employee, slot, role)] for employee in employees) == role_demand[role])

    # 制約2: 掛け持ち禁止
    for employee in employees:
        for slot in slots:
            model.Add(sum(x[(employee, slot, role)] for role in roles) <= 1)

    # 制約3: 不可時間
    for employee, slot in unavailable_pairs:
        for role in roles:
            model.Add(x[(employee, slot, role)] == 0)

    # 公平性: コマ数の偏りを最小化
    shifts_per_employee = {}
    for employee in employees:
        shifts_per_employee[employee] = sum(
            x[(employee, slot, role)] for slot in slots for role in roles
        )
    max_possible = len(slots)
    max_shifts = model.NewIntVar(0, max_possible, "max_shifts")
    min_shifts = model.NewIntVar(0, max_possible, "min_shifts")
    for employee in employees:
        model.Add(max_shifts >= shifts_per_employee[employee])
        model.Add(min_shifts <= shifts_per_employee[employee])
    model.Minimize(max_shifts - min_shifts)

    # --- 解く ---
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # --- 結果をDataFrameにする ---
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # 行=時間枠、列=役割 の表を作る
        table = {}
        for role in roles:
            table[role] = []
            for slot in slots:
                assigned = ""
                for employee in employees:
                    if solver.Value(x[(employee, slot, role)]) == 1:
                        assigned = employee
                table[role].append(assigned)
        df = pd.DataFrame(table, index=slots)
        return df
    else:
        return None
