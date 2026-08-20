from ortools.sat.python import cp_model

# --- sample data ---
# employee (5) --- e
employees = ["Aさん", "Bさん", "Cさん", "Dさん", "Eさん"]

# 時間枠 (3) --- t
slots = ["午前", "午後", "夕方"]

# 役割 (2) --- r
roles = ["レジ", "調理"]

# 各(時間枠,役割)に必要な人数
#demand = {
#        ("午前", "レジ"): 1, ("午前", "調理"): 1,
#        ("午後", "レジ"): 1, ("午後", "調理"): 1,
#        ("夕方", "レジ"): 1, ("夕方", "調理"): 1,
#        }
# 全時間で人員数は同じ
role_demand = {
        "レジ": 1,
        "調理": 1,
}

# 「この人はこの枠に入れない」リスト
unavailable_pairs = [
        ("Aさん", "午前"),
        ("Cさん", "夕方"),
]
        
# --- モデルを作る ---
model = cp_model.CpModel()
x = {}
for employee in employees:
        for slot in slots:
                for role in roles:
                        x[(employee, slot, role)] = model.NewBoolVar(f"x_{employee}_{slot}_{role}")
# test
#print(f"変数の数: {len(x)}")

# --- 制約1: 各枠・核役割の人数はちょうど必要数 ---
# model.Add()は制約の追加
for slot in slots:
        for role in roles:
                model.Add(
                        sum(x[(employee, slot, role)] for employee in employees) == role_demand[role]
                )

# --- 制約2: 掛け持ち禁止 ---
# sigma_ r {x[E, T, r]} <= 1
for employee in employees:
        for slot in slots:
                model.Add(
                        sum(x[(employee, slot, role)] for role in roles) <= 1
                )

# --- 制約3: できない時間 ---
# 決定変数x = 0である
for employee, slot in unavailable_pairs:
        for role in roles:
                model.Add(
                        x[(employee, slot, role)] == 0
                )

# 各従業員のコマ数
shifts_per_employee = {}
for employee in employees:
        shifts_per_employee[employee] = sum(
                x[(employee, slot, role)] for slot in slots for role in roles
        )

# 最大最小の箱
max_possible = len(slots)
max_shifts = model.NewIntVar(0, max_possible, "max_shifts")
min_shifts = model.NewIntVar(0, max_possible, "min_shifts")

# 箱に最大最小の意味を与える
for employee in employees:
        model.Add(max_shifts >= shifts_per_employee[employee])
        model.Add(min_shifts <= shifts_per_employee[employee])

# 目的関数
model.Minimize(max_shifts - min_shifts)

# --- solverを走らせて解く ---
solver = cp_model.CpSolver()
status = solver.Solve(model)

# --- 結果を表示する ---
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("解が見つかりました！\n")
        for slot in slots:
                print(f"【{slot}】")
                for role in roles:
                        for employee in employees:
                                if solver.Value(x[(employee, slot, role)]) == 1:
                                        print(f"  {role}: {employee}")
                print()
else:
        print("解が見つかりませんでした（制約が難しすぎるかも）")


