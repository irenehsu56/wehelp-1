from fastapi import FastAPI, Request, Form, Body
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse # RedirectResponse 可以直接導向到其他網址
from fastapi.staticfiles import StaticFiles # 讀取 static 資料夾的檔案
from fastapi.templating import Jinja2Templates # Jinja2Templates 可以使用 jinja2 模板引擎，讓 python 回傳 HTML 檔案
from starlette.middleware.sessions import SessionMiddleware # SessionMiddleware 可以讓我們使用 session，用來記錄使用者的登入狀態
from urllib.parse import quote # quote 可以讓網址正確顯示中文
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers # 讓 MCP Tool 取得 HTTP 請求中的 Header
import mysql.connector
import hashlib
import uuid # 利用 uuid 做亂數

# 建立 MCP Server
mcp=FastMCP("Testing Message Website")

# 建立與 MySQL 的連線
def get_db_connection():
    con=mysql.connector.connect(
        user="root",
        password="123456",
        host="localhost",
        database="website"
    )
    return con

# MCP Tool：建立留言
@mcp.tool(
    name="create_message",
    description="Create a new message in Testing Message Website."
)
def create_message_tool(content: str)->dict:
    # 取得這次 MCP 請求的 Headers
    headers=get_http_headers(include_all=True)

    # Header 名稱通常會轉成小寫
    authorization=headers.get("authorization", "")

    # 必須是 Authorization: Bearer TOKEN
    if not authorization.startswith("Bearer "):
        return {"error": True}

    # 移除前面的 Bearer 和空白
    token=authorization[7:].strip()

    if token=="":
        return {"error": True}

    # 清除留言前後空白
    content=content.strip()

    if content=="":
        return {"error": True}

    con=None
    cursor=None

    try:
        con=get_db_connection()
        cursor=con.cursor(dictionary=True)

        # 使用 Token 找出對應的會員
        member_query="""
            SELECT id
            FROM member
            WHERE token=%s
        """

        cursor.execute(member_query, (token,))
        member=cursor.fetchone()

        # 找不到代表 Token 無效
        if member is None:
            return {"error": True}

        member_id=member["id"]

        # 使用該會員 ID 建立留言
        insert_query="""
            INSERT INTO message(member_id, content)
            VALUES(%s, %s)
        """

        cursor.execute(insert_query, (member_id, content))
        con.commit()
        return {"ok": True}

    except mysql.connector.Error as error:
        print("MCP 建立留言時，資料庫發生錯誤：", error)

        if con is not None:
            con.rollback()

        return {"error": True}

    finally:
        if cursor is not None:
            cursor.close()

        if con is not None and con.is_connected():
            con.close()

# 將 MCP Server 轉成可以掛到 FastAPI 的 ASGI 應用程式
mcp_app=mcp.http_app(path="/")

app=FastAPI(lifespan=mcp_app.lifespan) # 建立 FastAPI，並使用 MCP 的 lifespan

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
    signed_in=request.session.get("SIGNED-IN", False)

    if not signed_in:
        return RedirectResponse(url="/", status_code=303) # 如果不是登入狀態，就不能看會員頁面，直接導回首頁
    
    member_id=request.session.get("MEMBER-ID")
    member_name=request.session.get("MEMBER-NAME", "")

    if member_id is None:
        request.session.clear()
        return RedirectResponse(url="/", status_code=303)
    
    con=None
    cursor=None
    token=""

    try:
        con=get_db_connection()
        cursor=con.cursor(dictionary=True)

        # 從資料庫查詢相同的 Token
        token_query="""
            SELECT token
            FROM member
            WHERE id=%s
        """
        cursor.execute(token_query, (member_id,))
        member=cursor.fetchone()

        # 查不到會員資料，登入失敗
        if member is not None and member["token"] is not None:
            token=member["token"]

    except mysql.connector.Error as error:
        print("讀取會員 Token 時，資料庫發生錯誤：", error)

    finally:
        if cursor is not None:
            cursor.close()    
        if con is not None and con.is_connected():
            con.close()

    return templates.TemplateResponse(
        request=request,
        name="member.html",
        context={"name":member_name, "token": token}
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
# 建立Token API
@app.put("/api/token")
def create_token(request: Request):
    signed_in=request.session.get("SIGNED-IN", False)

    if not signed_in:
        return {"error": True}
    
    member_id=request.session.get("MEMBER-ID")

    if member_id is None:
        return {"error": True}
    
    con=None
    cursor=None

    try:
        # 每次呼叫 API 時，重新產生一組隨機字串
        random_string=str(uuid.uuid4())

        # 使用 SHA256 將隨機字串轉成 64 個字元的 Token
        token=hashlib.sha256(
            random_string.encode()
        ).hexdigest()

        con=get_db_connection()
        cursor=con.cursor()

        # 將 Token 綁定目前登入的會員
        update_query="""
            UPDATE member
            SET token=%s
            WHERE id=%s
        """
        cursor.execute(update_query, (token, member_id))

        if cursor.rowcount==0:
            con.rollback()
            return {"error": True}
        
        con.commit()

        return {"ok": True, "token": token}

    except mysql.connector.Error as error:
        print("產生 Token 時，資料庫發生錯誤：", error)

        if con is not None:
            con.rollback()

        return {"error": True}

    finally:
        if cursor is not None:
            cursor.close()    
        if con is not None and con.is_connected():
            con.close()

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

app.mount("/mcp", mcp_app)