function checkAgree(){
    const agree=document.getElementById("agree");
    if(!agree.checked){
        alert("請勾選同意條款");
        return false;
    }
    return true;
}

function getHotel(){
    const hotelID=document.getElementById("hotelId").value;
    if(!/^[1-9][0-9]*$/.test(hotelID)){
        alert("請輸入正整數");
        return;
    }
    window.location.href="/hotel/"+hotelID;
}