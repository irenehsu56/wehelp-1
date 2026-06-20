# Task 1:
def func1(name):
    characters = {
    "悟空": {"x": 0, "y": 0, "side": "L"},
    "辛巴": {"x": -3, "y": 3, "side": "L"},
    "貝吉塔": {"x": -4, "y": -1, "side": "L"},
    "特南克斯": {"x": 1, "y": -2, "side": "L"},
    "丁滿": {"x": -1, "y": 4, "side": "R"},
    "弗利沙": {"x": 4, "y": -1, "side": "R"}     
    }

    x1 = characters[name]["x"]
    y1 = characters[name]["y"]
    distances = {}
    for other in characters:
        if other == name:
            continue
        x2 = characters[other]["x"]
        y2 = characters[other]["y"]
        d = abs(x1-x2) + abs(y1-y2) # 計算曼哈頓距離
        if characters[name]["side"] != characters[other]["side"]:
            d += 2
        distances[other] = d
        
    min_d = min(distances.values()) # 找最近
    max_d = max(distances.values()) # 找最遠

    nearest = []
    farthest = []
    for person,d in distances.items():
        if d == min_d:
            nearest.append(person)
        if d == max_d:
            farthest.append(person)

    print("最遠：","、".join(farthest)) 
    print("最近：","、".join(nearest)) 

func1("辛巴") # print 最遠弗利沙，最近丁滿、貝吉塔
func1("悟空") # print 最遠丁滿、弗利沙，最近特南克斯
func1("弗利沙") # print 最遠辛巴，最近特南克斯
func1("特南克斯") # print 最遠丁滿，最近悟空

# Task 2:
def func2(ss, start, end, criteria):
    if ">=" in criteria:
        field, value = criteria.split(">=")
        op = ">="
    elif "<=" in criteria:
        field, value = criteria.split("<=")
        op = "<="
    else:
        field, value = criteria.split("=")
        op = "="

    if field != "name":
        value = float(value)

    available = []

    for s in ss:
        # 建立預約紀錄
        if "books" not in s:
            s["books"] = []

        # 檢查時間是否衝突
        ok = True
        for a, b in s["books"]:
            if not (end <= a or start >= b):
                ok = False
                break

        if not ok:
            continue

        # 檢查條件
        if op == "=" and s[field] == value:
            available.append(s)

        elif op == ">=" and s[field] >= value:
            available.append(s)

        elif op == "<=" and s[field] <= value:
            available.append(s)

    if not available:
        print("Sorry")
        return

    # 找最符合的
    if op == "=":
        chosen = available[0]
    elif op == ">=":
        chosen = min(available, key=lambda x: x[field])
    else:
        chosen = max(available, key=lambda x: x[field])

    chosen["books"].append((start, end))
    print(chosen["name"]) 


services = [
    {"name": "S1", "r": 4.5, "c": 1000},
    {"name": "S2", "r": 3, "c": 1200},
    {"name": "S3", "r": 3.8, "c": 800}
]

func2(services, 15, 17, "c>=800") # S3
func2(services, 11, 13, "r<=4") # S3
func2(services, 10, 12, "name=S3") # Sorry
func2(services, 15, 18, "r>=4.5") # S1
func2(services, 16, 18, "r>=4") # Sorry
func2(services, 13, 17, "name=S1") # Sorry
func2(services, 8, 9, "c<=1500") # S2

# Task 3:
def func3(index):
    num=25
    pattern=[-2,-3,1,2]
    for i in range(index):
        num+=pattern[i%4] # % 取餘數
    print(num)

func3(1) # print 23
func3(5) # print 21
func3(10) # print 16
func3(30) # print 6

# Task 4:
def func4(sp, stat, n):
    available = []
    for i in range(len(sp)):
        if stat[i] == "0":
            available.append((i,sp[i])) # 找可服務的車廂，並求出該車廂剩餘的座位數

    fit = []
    for i, seats in available:
        if seats >= n:
            fit.append((i, seats)) # 找出符合人數的車廂

    if fit:
        best = min(fit, key=lambda x: x[1]) # 找出符合的車廂中，最小的（最接近的）
    else:
        best = max(available, key=lambda x: x[1]) # 如果沒有符合的車廂，就找不符合的車廂中，最大的（最接近的）
    
    print(best[0])

func4([3, 1, 5, 4, 3, 2], "101000", 2) # print 5
func4([1, 0, 5, 1, 3], "10100", 4) # print 4
func4([4, 6, 5, 8], "1000", 4) # print 2