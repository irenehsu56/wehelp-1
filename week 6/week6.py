from fastapi import FastAPI, Request, Form, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse # RedirectResponse 可以直接導向到其他網址
from fastapi.staticfiles import StaticFiles # 讀取 static 資料夾的檔案
from fastapi.templating import Jinja2Templates # Jinja2Templates 可以使用 jinja2 模板引擎，讓 python 回傳 HTML 檔案
from starlette.middleware.sessions import SessionMiddleware # SessionMiddleware 可以讓我們使用 session，用來記錄使用者的登入狀態
from urllib.parse import quote # quote 可以讓網址正確顯示中文
import mysql.connector

app=FastAPI() # FastAPI 物件
app.add_middleware(SessionMiddleware, secret_key="your-secret-key") # 添加 SessionMiddleware，secret_key 用來保護 session 資料的密鑰
app.mount("/static", StaticFiles(directory="static"), name="static") # 靜態檔案路徑
templates=Jinja2Templates(directory="templates") # Jinja2Templates 物件

# 建立與 MySQL 的連線
def get_db_connection():
    con=mysql.connector.connect(
        user="root",
        password="123456",
        host="localhost",
        database="website"
    )
    return con

# 首頁 Home page
@app.get("/", response_class=HTMLResponse)
def home_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )

# 註冊 Signup
@app.post("/signup")
def signup(
    name: str=Form(""),
    email: str=Form(""),
    password: str=Form("")
):
    # 去除使用者輸入前後的空白
    name=name.strip()
    email=email.strip()
    password=password.strip()

    # 檢查是否有空白欄位
    if name=="" or email=="" or password=="":
        error_message=quote("請輸入姓名、信箱和密碼")

        return RedirectResponse(url=f"/ohoh?msg={error_message}",status_code=303)

    con=None
    cursor=None

    # try：執行資料庫操作，成功就回傳結果、失敗進入 except、最後到 finally
    try:
        con=get_db_connection()
        # 讓查詢結果以字典形式顯示
        cursor=con.cursor(dictionary=True)

        # 檢查信箱是否已經註冊
        check_query="""
            SELECT id
            FROM member
            WHERE email=%s
        """
        # 執行 SQL 指令
        cursor.execute(check_query, (email,))
        existing_member=cursor.fetchone()

        # 如果查到資料，代表信箱已經使用過
        if existing_member is not None:
            error_message=quote("重複的電子郵件")

            return RedirectResponse(url=f"/ohoh?msg={error_message}",status_code=303)

        # 新增會員資料
        insert_query="""
            INSERT INTO member(name, email, password)
            VALUES(%s, %s, %s)
        """

        cursor.execute(insert_query, (name, email, password))
        # 儲存資料庫變更
        con.commit()
        # 註冊成功後回到首頁
        return RedirectResponse(url="/",status_code=303)
    
    except mysql.connector.IntegrityError as error:
            print("註冊資料重複：", error)

            if con is not None:
                con.rollback()

            error_message=quote("重複的電子郵件")
            return RedirectResponse(url=f"/ohoh?msg={error_message}",status_code=303)

    # 捕捉 MySQL 的錯誤
    except mysql.connector.Error as error:
        print("註冊時，資料庫發生錯誤：", error)

        if con is not None:
            con.rollback()

        error_message=quote("系統發生錯誤，請稍後再試")
        return RedirectResponse(url=f"/ohoh?msg={error_message}",status_code=303)

    finally:
        if cursor is not None:
            cursor.close()

        if con is not None and con.is_connected():
            con.close()

# 登入 Login
@app.post("/login")
def login(
    request: Request,
    email: str=Form(""), # 接收 email
    password: str=Form(""), # 接收 password
):
    email=email.strip()
    password=password.strip()

    if email=="" or password=="":
        error_message=quote("請輸入信箱和密碼")
        return RedirectResponse(url=f"/ohoh?msg={error_message}", status_code=303)

    con=None
    cursor=None

    try:
        con=get_db_connection()
        cursor=con.cursor(dictionary=True)

        # 從資料庫查詢相同的信箱和密碼
        login_query="""
            SELECT id, name, email
            FROM member
            WHERE email=%s AND password=%s
        """
        cursor.execute(login_query, (email, password))
        member=cursor.fetchone()

        # 查不到會員資料，登入失敗
        if member is None:
            error_message=quote("電子郵件或密碼錯誤")
            return RedirectResponse(url=f"/ohoh?msg={error_message}",status_code=303)
        
        # 登入成功，把會員資料存進 Session
        request.session["SIGNED-IN"]=True
        request.session["MEMBER-ID"]=member["id"]
        request.session["MEMBER-NAME"]=member["name"]
        request.session["MEMBER-EMAIL"]=member["email"]

        return RedirectResponse(url="/member",status_code=303)

    except mysql.connector.Error as error:
        print("登入時，資料庫發生錯誤：", error)

        error_message=quote("系統發生錯誤，請稍後再試")
        return RedirectResponse(url=f"/ohoh?msg={error_message}",status_code=303)

    finally:
        if cursor is not None:
            cursor.close()    
        if con is not None and con.is_connected():
            con.close()

# 會員頁面 Member Page
@app.get("/member", response_class=HTMLResponse)
def member_page(request: Request):
    signed_in = request.session.get("SIGNED-IN", False)

    if not signed_in:
        return RedirectResponse(url="/", status_code=303) # 如果不是登入狀態，就不能看會員頁面，直接導回首頁
    
    member_name = request.session.get("MEMBER-NAME", "")

    return templates.TemplateResponse(
        request=request,
        name="member.html",
        context={"name":member_name}
    )

# 登出 Logout
@app.get("/logout")
def logout(request: Request):
    request.session.clear() # 清除 session 裡的所有登入資料
    return RedirectResponse(url="/", status_code=303)

# 失敗頁面 Error Page
@app.get("/ohoh", response_class=HTMLResponse)
def error_page(request: Request, msg: str="自訂的錯誤訊息"):
    return templates.TemplateResponse(
        request=request,
        name="ohoh.html",
        context={"msg": msg}
    )

# 建立後端 RESTful APIs
# 新增留言的 API
@app.post("/api/message")
def create_message(
    request: Request,
    body: dict=Body(...)
):
    # 確認使用者是否登入
    signed_in=request.session.get("SIGNED-IN", False)

    if not signed_in:
        return {"error": True}
    
    # 從 Session 取得會員編號
    member_id=request.session.get("MEMBER-ID")

    # 從 Request Body 取得留言內容
    content=body.get("content", "").strip()

    if member_id is None or content=="":
        return {"error":True}
    
    con=None
    cursor=None

    try:
        con=get_db_connection()
        cursor=con.cursor()

        insert_query="""
            INSERT INTO message(member_id, content)
            VALUES(%s, %s)
        """
        cursor.execute(insert_query, (member_id, content))
        con.commit()
        return {"ok": True}

    except mysql.connector.Error as error:
        print("新增留言時，資料庫發生錯誤：", error)

        if con is not None:
            con.rollback()
        return {"error": True}

    finally:
        if cursor is not None:
            cursor.close()    
        if con is not None and con.is_connected():
            con.close()

# 取得所有留言的 API
@app.get("/api/message")
def get_message(request: Request):
    # 確認使用者是否登入
    signed_in=request.session.get("SIGNED-IN", False)

    if not signed_in:
        return {"error": True}
    
    current_member_id=request.session.get("MEMBER-ID")

    if current_member_id is None:
        return {"error":True}
    
    con=None
    cursor=None

    try:
        con=get_db_connection()
        cursor=con.cursor(dictionary=True)

        # 透過 JOIN 取得留言者姓名 
        message_query="""
            SELECT
                message.id,
                message.member_id,
                member.name,
                message.content
            FROM message
            INNER JOIN member ON message.member_id = member.id
            ORDER BY message.id DESC
        """
        cursor.execute(message_query)
        messages=cursor.fetchall()

        data=[]

        for message in messages:
            data.append({
                "id": message["id"],
                "name": message["name"],
                "content": message["content"],
                # 判斷這則留言是否始於目前登入者
                "self": message["member_id"]==current_member_id
            })

        return {"ok": True, "data": data}

    except mysql.connector.Error as error:
        print("取得留言時，資料庫發生錯誤：", error)
        return {"error": True}

    finally:
        if cursor is not None:
            cursor.close()    
        if con is not None and con.is_connected():
            con.close()

# 根據編號，刪除留言的 API
@app.delete("/api/message/{message_id}")
def delete_message(
    request: Request,
    message_id: int
):
    # 確認使用者是否登入
    signed_in=request.session.get("SIGNED-IN", False)

    if not signed_in:
        return {"error": True}
    
    current_member_id=request.session.get("MEMBER-ID")

    if current_member_id is None:
        return {"error": True}
    
    con=None
    cursor=None

    try:
        con=get_db_connection()
        cursor=con.cursor()
        
        # 限制只能刪除自己的留言
        delete_query="""
            DELETE FROM message
            WHERE id=%s AND member_id=%s
        """
        cursor.execute(
            delete_query,
            (message_id, current_member_id)
        )

        # rowcount 是實際被刪除的資料筆數
        if cursor.rowcount==0:
            con.rollback()
            return {"error": True}
        
        con.commit()
        
        return {"ok": True}

    except mysql.connector.Error as error:
        print("刪除留言時，資料庫發生錯誤：", error)

        if con is not None:
            con.rollback()
            
        return {"error": True}

    finally:
        if cursor is not None:
            cursor.close()    
        if con is not None and con.is_connected():
            con.close()