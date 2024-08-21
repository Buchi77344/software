let  submitBtn = document.querySelector(".submit-btn")
let  useridSubmitBtn = document.querySelector(".user_id-submit-btn")
let  overlay = document.querySelector(".overlay")
let btnSpan = document.querySelector(".submit-btn > span")
let useridBtnSpan = document.querySelector(".user_id-submit-btn > span")
let createInput = document.querySelectorAll(".create-acct-input")
let useridInput = document.querySelectorAll(".user_id-input")
let deleteOverlay = document.querySelector(".delete-overlay")
let deleteClarityDiv = document.querySelector(".delete-clarity-div")
let deleteBtn = document.querySelectorAll(".delete-btn")
let clarityBtn = document.querySelectorAll(".clarity-btn-container a")

Array.from(deleteBtn).forEach(el => {
    el.onclick = function(){
        console.log("hi there")
        deleteOverlay.style.display = "grid"
        setTimeout(() => {
            deleteClarityDiv.classList.add("visible")
        }, 100)
    }
})

let arrayClarityBtn = Array.from(clarityBtn)
arrayClarityBtn.forEach(el => {
    el.onclick = function(){
        setTimeout(() => {
            deleteOverlay.style.display = "none"
        }, 100)
        deleteClarityDiv.classList.remove("visible")
    }
 
})

function emptyValueLength(el_input){
    let value;
    el_input.forEach(el => {
        if(el.value.length == 0){
            value = true
        }else {
            value = false
        }
       
    })
//the input nodelist will be empty if we are on another page, that why with this condition we set value to false to enable the animation to work
    // if(el_input.length == 0){
    //     value = false
    // }
    
    return value
}

function startLoadingAnim(el_input, el = "", btnSpan = ""){
    let emptyValue = emptyValueLength(el_input)
    if (emptyValue == false){
        el.classList.add("active")

        setTimeout(() => {
            el.classList.remove("active")
            btnSpan.textContent = "Successful"
        }, 4000)
    }
}

if (submitBtn){
    submitBtn.addEventListener("click", (e) => startLoadingAnim(createInput, e.target, btnSpan))
}


if (useridSubmitBtn){
    useridSubmitBtn.addEventListener("click", () =>{
        console.log("hi")
        
        startLoadingAnim(useridInput, overlay, useridBtnSpan)
    })
}
