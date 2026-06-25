const url1="https://cwpeng.github.io/test/assignment-3-1";
const url2="https://cwpeng.github.io/test/assignment-3-2";

let attractions=[]; // 建立一個空陣列，存放景點資料
let currentIndex=13; // 下一次按 Load More 會從第13筆開始顯示

window.addEventListener("load", async()=>{ // 物件.addEventListener("事件", 函式)，這邊表示當整個網頁完成後執行程式
    try{
        // 同時取得兩筆資料
        const responses=await Promise.all([
            fetch(url1),
            fetch(url2)
        ]);
        const data=await Promise.all(
            responses.map(r=>r.json()) // map()會將陣列中的每個元素都套用同一個函式=>將每個response物件轉成json格式
        );
        // 將兩筆資料合併成一個陣列
        const basicRows = data[0].rows;
        const imageRows = data[1].rows;
        const imageHost = data[1].host;
        
        const imageMap = {};
        imageRows.forEach(image => {
            imageMap[image.serial] = image.pics;
        });

        attractions = basicRows.map(spot => {
            return {
                ...spot,
                pics: imageMap[spot.serial],
                imageHost: imageHost
            };
        });
        // 前三筆放在Bar，後十筆放在Content
        renderBars(attractions.slice(0, 3));
        renderContents(attractions.slice(3, 13));

        document // 找到id"LoadMoreButton"，當他被click時，執行LoadMore函式
        .getElementById("LoadMoreButton")
        .addEventListener("click", LoadMore)
    }
    catch(error){
        console.error("資料讀取失敗", error);
    }
});

function LoadMore(){
    const nextData=attractions.slice(currentIndex, currentIndex+10); // 取出下面10筆資料
    renderContents(nextData);
    currentIndex += 10;

    if (currentIndex>=attractions.length){
        document.getElementById("LoadMoreButton").style.display="none"; // 若資料到底了，就隱藏按鈕
    }
}

// 取得第一張圖片
function getFirstImage(host, pics){
    if (!pics) {
        return ""; // 若沒有圖片，回傳空字串
    }
    const imageList=pics.match(
        /\/resources\/images\/\d+-\d+\.jpg/g
    ); // 取得所有圖片網址
    if(imageList && imageList.length>0){
        return host+imageList[0]; // 回傳第一張圖片
    }
    return ""; // 若沒有圖片，回傳空字串
}
// 建立前三個 Promotion Bar
function renderBars(data){
    const container=document.querySelector(".bar-container");
    data.forEach((spot, index)=>{
        const bar=document.createElement("div");
        if(index===0){
            bar.classList.add("bar", "bar1");
        }
        else if(index===1){
            bar.classList.add("bar", "bar2");
        }
        else if(index===2){
            bar.classList.add("bar", "bar3");
        }

        const img=document.createElement("img");
        img.src=getFirstImage(spot.imageHost, spot.pics); // 設立圖片網址
        img.alt=spot.sname; // 設立圖片文字

        const title=document.createElement("span"); // 建立標題
        title.textContent=spot.sname; // 設立標題文字

        bar.appendChild(img); // 將圖片加入bar
        bar.appendChild(title); // 將標題加入bar

        container.appendChild(bar); // 將bar加入container
    });
}
// 建立後十個 Content
function renderContents(data){
    const container=document.querySelector(".content-container");
    data.forEach((spot, index)=>{
        const content=document.createElement("div");
        
        let className="";
        if (index===0 || index===5){
            className="content1";
        }
        else{
            className="content2";
        }
        
        content.classList.add("content", className);

        const img=document.createElement("img");
        img.src=getFirstImage(spot.imageHost, spot.pics); // 設立圖片網址
        img.alt=spot.sname; // 設立圖片文字

        const star=document.createElement("div");
        star.classList.add("star");
        star.textContent="★";

        const title=document.createElement("div"); // 建立標題
        title.classList.add("content-title");
        title.textContent=spot.sname; // 設立標題文字

        content.appendChild(img); // 將圖片加入content
        content.appendChild(star); // 將星星加入content
        content.appendChild(title); // 將標題加入content
        container.appendChild(content); // 將content加入container
    });
}

// 手機版選單
function openMenu(){
    document
        .getElementById("mobileMenu")
        .classList.add("show");
}

function closeMenu(){
    document
        .getElementById("mobileMenu")
        .classList.remove("show");
}