import csv
from fastapi import FastAPI, Request, Form 
from fastapi.responses import HTMLResponse, RedirectResponse # RedirectResponse 可以直接導向到其他網址
from fastapi.staticfiles import StaticFiles # 讀取 static 資料夾的檔案
from fastapi.templating import Jinja2Templates # Jinja2Templates 可以使用 jinja2 模板引擎，讓 python 回傳 HTML 檔案
from starlette.middleware.sessions import SessionMiddleware # SessionMiddleware 可以讓我們使用 session，用來記錄使用者的登入狀態
from urllib.parse import quote # quote 可以讓網址正確顯示中文

app=FastAPI() # FastAPI 物件
app.add_middleware(SessionMiddleware, secret_key="your-secret-key") # 添加 SessionMiddleware，secret_key 用來保護 session 資料的密鑰
app.mount("/static", StaticFiles(directory="static"), name="static") # 靜態檔案路徑
templates=Jinja2Templates(directory="templates") # Jinja2Templates 物件

# 首頁 Home page
@app.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

# 登入 Login
@app.post("/login")
def login(
    request: Request,
    email: str=Form(""), # 接收 email
    password: str=Form(""), # 接收 password
):
    correct_email="abc@abc.com"
    correct_password="abc"

    if email=="" or password=="":
        error_message=quote("請輸入信箱和密碼")
        return RedirectResponse(url=f"/ohoh?msg={error_message}", status_code=303)

    if email==correct_email and password==correct_password:
        request.session["SIGNED-IN"]=True # 登入成功
        return RedirectResponse(url="/member", status_code=303)
    
    error_message=quote("信箱或密碼輸入錯誤")
    return RedirectResponse(url=f"/ohoh?msg={error_message}", status_code=303)

# 會員頁面 Success Page
@app.get("/member", response_class=HTMLResponse)
def success_page(request: Request):
    signed_in = request.session.get("SIGNED-IN", False)

    if not signed_in:
        return RedirectResponse(url="/", status_code=303) # 如果不是登入狀態，就不能看會員頁面，直接導回首頁
    
    return templates.TemplateResponse(
        request=request,
        name="member.html"
    )

# 登出 Logout
@app.get("/logout")
def logout(request: Request):
    request.session["SIGNED-IN"] = False
    return RedirectResponse(url="/", status_code=303)

# 失敗頁面 Error Page
@app.get("/ohoh", response_class=HTMLResponse)
def error_page(request: Request, msg: str="自訂的錯誤訊息"):
    return templates.TemplateResponse(
        request=request,
        name="ohoh.html",
        context={"msg": msg}
    )

# 旅館資訊 Hotel Page
@app.get("/hotel/{hotel_id}", response_class=HTMLResponse)
def hotel_page(request: Request, hotel_id: int):
    hotel=None

    with open("hotels.csv", "r", encoding="utf-8-sig") as file:
        reader=csv.reader(file)

        for row in reader:
            if row[5]==str(hotel_id):
                hotel={
                    "chinese_name": row[0],
                    "english_name": row[1],
                    "phone": row[4],
                }
                break
    
    return templates.TemplateResponse(
        request=request,
        name="hotel.html",
        context={"hotel": hotel}
    )