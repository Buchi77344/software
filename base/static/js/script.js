let  submitBtn = document.querySelector(".submit-btn")
let btnSpan = document.querySelector(".submit-btn > span")
console.log(btnSpan)
let createInput = document.querySelectorAll(".create-acct-input")
function emptyValueLength(){
    let value;
    createInput.forEach(el => {
        if(el.value.length == 0){
            value = true
        }else {
            value = false
        }
    })
    
    return value
}
submitBtn.addEventListener("click", (e) => {
    let emptyValue = emptyValueLength()
    console.log(emptyValue)
    if (emptyValue == false){
        e.target.classList.add("active")

        setTimeout(() => {
            e.target.classList.remove("active")
            btnSpan.textContent = "Successful"
        }, 4000)
    }
  
})