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
let yesbtn = document.querySelector(".Yes-btn")

Array.from(deleteBtn).forEach(el => {
    el.onclick = function(){
        let delLink = this.dataset.link
        yesbtn.href = delLink
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


//Script to sort Results by Category of Subjects
let categoryLinks = document.querySelectorAll(".category-link")
let subjectResultDivs = document.querySelectorAll(".subject-result-div")
Array.from(categoryLinks).forEach(link => {
    link.addEventListener("click", (e) => {
        categorizeProducts(e, link)
    })
})

function categorizeProducts(e, link){
    e.preventDefault()
    if(link.dataset.category == "all"){
        subjectResultDivs.forEach(el => {
            el.classList.remove("hide")
        })

    }else{
        subjectResultDivs.forEach(el => {
            if(link.dataset.category.toLowerCase() == el.dataset.select.toLowerCase()){
                el.classList.remove("hide")
                console.log(el)
            }else{
                el.classList.add("hide")
            }
        })  
    }
}

//Script to show answered questions
let questionBoxes = document.querySelectorAll(".question-box")
let questionNumbers = document.querySelectorAll(".question-number")
let smallBoxHead = document.querySelectorAll(".question-box .small-box-head")
let currentPage = 1;
const itemsPerPage = 5;

if(document.querySelector(".user-question-btn-container")){
    questionBoxes.forEach((box, index) => {
        box.onchange = () => {
            questionNumbers[index].classList.add("answered")
        }
    
        smallBoxHead.forEach((el, index) => {
            el.textContent = `Question ${index + 1}`
        })
    
    })
    
    
    if(questionBoxes.length == 0){
        if (document.querySelector(".user-question-btn-container")){
            document.querySelector(".user-question-btn-container").style.display = "none"
            document.querySelector(".no-questions").style.display = "block"
        }
    }
    
    function displayItems(container, itemsPerPage, page) {
        const start = (page - 1) * itemsPerPage;
        const end = start + itemsPerPage;
      
        container.querySelectorAll(".question-box").forEach((item, index) => {
          if (index >= start && index < end) {
            item.style.display = "block";
          } else {
            item.style.display = "none";
          }
        });
      
        document.getElementById("current-page").textContent = `Page ${page}`;
    }
    
    function updatePagination() {
        const container = document.querySelector(".question-section");
        displayItems(container, itemsPerPage, currentPage);
      
        const pageCount = Math.ceil(questionBoxes.length / itemsPerPage);
        document.getElementById("pag-prev").disabled = currentPage === 1;
        document.getElementById("pag-next").disabled = currentPage === pageCount;
    }
    
    updatePagination();
    
    document.getElementById("pag-prev").addEventListener("click", function () {
      if (currentPage > 1) {
        currentPage--;
        updatePagination();
      }
    });
    
    document.getElementById("pag-next").addEventListener("click", function () {
      const pageCount = Math.ceil(questionBoxes.length / itemsPerPage);
      if (currentPage < pageCount) {
        currentPage++;
        updatePagination();
      }
    });
    
    questionNumbers.forEach((el, index) => {
        el.addEventListener("click", () => {
            console.log(index)
            currentPage = Math.ceil((index + 1) / itemsPerPage);
            updatePagination();
    
            // Scroll to the specific item
            const targetItem = document.querySelectorAll(".question-box")[index];
            targetItem.scrollIntoView({ behavior: "smooth" });
        })
    
    })
}

if(document.querySelector(".user-login-error-message")){
    let errorMessage = document.querySelector(".user-login-error-message")
    console.log(errorMessage)
    if(errorMessage.textContent != ""){
        setTimeout(() => {
            errorMessage.style.display = "none"
        }, 5000)
    }
}

