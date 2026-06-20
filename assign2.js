// Task 1:
function func1(name){
    const characters = {
    "悟空": {"x": 0, "y": 0, "side": "L"},
    "辛巴": {"x": -3, "y": 3, "side": "L"},
    "貝吉塔": {"x": -4, "y": -1, "side": "L"},
    "特南克斯": {"x": 1, "y": -2, "side": "L"},
    "丁滿": {"x": -1, "y": 4, "side": "R"},
    "弗利沙": {"x": 4, "y": -1, "side": "R"}     
    };

    const x1 = characters[name].x;
    const y1 = characters[name].y;
    const distances = {};
    for(const other in characters){
        if(other === name){
            continue;
        }
        const x2 = characters[other].x;
        const y2 = characters[other].y;
        let d = Math.abs(x1-x2) + Math.abs(y1-y2);
        if(characters[name].side !== characters[other].side){
            d += 2;
        }
        distances[other] = d;
    }
    const values = Object.values(distances);
    const min_d = Math.min(...values);
    const max_d = Math.max(...values);

    const nearest = [];
    const farthest = [];
    for(const person in distances){
        if(distances[person] === min_d){
            nearest.push(person);
        }
        if(distances[person] === max_d){
            farthest.push(person);
        }
    }

    console.log("最遠：", farthest.join("、"));
    console.log("最近：", nearest.join("、"));
}

func1("辛巴"); // print 最遠弗利沙，最近丁滿、貝吉塔
func1("悟空"); // print 最遠丁滿、弗利沙，最近特南克斯
func1("弗利沙"); // print 最遠辛巴，最近特南克斯
func1("特南克斯"); // print 最遠丁滿，最近悟空

// Task 2:
function func2(ss, start, end, criteria) {

    let field, value, op;

    if (criteria.includes(">=")) {
        [field, value] = criteria.split(">=");
        op = ">=";
    }
    else if (criteria.includes("<=")) {
        [field, value] = criteria.split("<=");
        op = "<=";
    }
    else {
        [field, value] = criteria.split("=");
        op = "=";
    }

    if (field !== "name") {
        value = Number(value);
    }

    const available = [];

    for (const s of ss) {

        if (!s.books) {
            s.books = [];
        }

        let ok = true;

        for (const [a, b] of s.books) {
            if (!(end <= a || start >= b)) {
                ok = false;
                break;
            }
        }

        if (!ok) {
            continue;
        }
        else if (op === "=" && s[field] === value) {
            available.push(s);
        }
        else if (op === ">=" && s[field] >= value) {
            available.push(s);
        }
        else if (op === "<=" && s[field] <= value) {
            available.push(s);
        }
    }

    if (available.length === 0) {
        console.log("Sorry");
        return;
    }

    let chosen = available[0];

    if (op === ">=") {
        for (const s of available) {
            if (s[field] < chosen[field]) {
                chosen = s;
            }
        }
    }
    else if (op === "<=") {
        for (const s of available) {
            if (s[field] > chosen[field]) {
                chosen = s;
            }
        }
    }

    chosen.books.push([start, end]);
    console.log(chosen.name);
}
const services=[
    {"name": "S1", "r": 4.5, "c": 1000},
    {"name": "S2", "r": 3, "c": 1200},
    {"name": "S3", "r": 3.8, "c": 800}
]

func2(services, 15, 17, "c>=800"); // S3
func2(services, 11, 13, "r<=4"); // S3
func2(services, 10, 12, "name=S3"); // Sorry
func2(services, 15, 18, "r>=4.5"); // S1
func2(services, 16, 18, "r>=4"); // Sorry
func2(services, 13, 17, "name=S1"); // Sorry
func2(services, 8, 9, "c<=1500"); // S2

// Task 3:
function func3(index){
    let num=25;
    const pattern=[-2,-3,1,2];
    for(let i=0;
        i<index;
        i++
        ){
            num+=pattern[i%4];
        }
        console.log(num);
    }
func3(1); // print 23
func3(5); // print 21
func3(10); // print 16
func3(30); // print 6

// Task 4:
function func4(sp, stat, n){
    const available = [];
    for(let i = 0; i < sp.length; i++){
        if (stat[i] === "0"){
            available.push([i,sp[i]]);
        }
    }

    const fit = [];

    for(const [i, seats] of available){
        if (seats >= n){
            fit.push([i, seats]);
        }
    }
    let best;
    if (fit.length > 0){
        best = fit[0];
        for (const item of fit){
            if (item[1] < best[1])
                best = item;
        }
    }
    else{
        best = available[0];
        for(const item of available){
            if (item[1] > best[1]){
                best = item;
            }
        }
    }
    console.log(best[0]);
}

func4([3, 1, 5, 4, 3, 2], "101000", 2) // print 5
func4([1, 0, 5, 1, 3], "10100", 4) // print 4
func4([4, 6, 5, 8], "1000", 4) // print 2