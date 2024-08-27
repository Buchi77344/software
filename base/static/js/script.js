let  submitBtn = document.querySelector(".submit-btn")
let  useridSubmitBtn = document.querySelector(".user_id-submit-btn")
let  overlay = document.querySelector(".overlay")
let btnSpan = document.querySelector(".submit-btn > span")
let useridBtnSpan = document.querySelector(".user_id-submit-btn > span")
let createInput = document.querySelectorAll(".create-acct-input")
let useridInput = document.querySelectorAll(".user_id-input")
let popupOverlay = document.querySelector(".popup-overlay")
let popupDiv = document.querySelector(".popup-div")
let deleteBtn = document.querySelectorAll(".delete-btn")
let popupBtn = document.querySelectorAll(".popup-btn-container button")
let yesbtn = document.querySelector(".Yes-btn")
let answerBtn = document.querySelector(".answer-submit-btn")
let popupVisible;
function ShowPopup(){
    popupOverlay.style.display = "grid"
    popupVisible = true
    setTimeout(() => {
        popupDiv.classList.add("visible")
    }, 100)

}

function removePopup(){
    popupDiv.classList.remove("visible")
    popupVisible = false
    setTimeout(() => {
        popupOverlay.style.display = "none"
    }, 100)
}

function submitAnswer(){
    answerBtn.type = "submit"
    answerBtn.click()
}

if(document.querySelector(".Yes-btn.exam")){
    document.querySelector(".Yes-btn.exam").addEventListener("click", function(){
        submitAnswer()
    })
}

Array.from(deleteBtn).forEach(el => {
    el.onclick = function(){
        let delLink = this.dataset.link
        if(this.dataset.link !== ""){
            yesbtn.querySelector("a").href = delLink
        }
        ShowPopup()
    }
})

let arrayPopupBtn = Array.from(popupBtn)
arrayPopupBtn.forEach(el => {
    el.onclick = function(){
        removePopup()
        if(this.classList.contains("yes-link")){
            this.querySelector("a").click()
        }
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
        categorizeResults(e, link)
    })
})

function categorizeResults(e, link){
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

    function selectNumber(){
        questionBoxes.forEach((box, index) => {
            box.onchange = () => {
                console.log("hi")
                questionNumbers[index].classList.add("answered")
            }
        
            smallBoxHead.forEach((el, index) => {
                el.textContent = `Question ${index + 1}`
            })
        
        })
    }

    selectNumber()
    
    if(questionBoxes.length == 0){
            document.querySelector(".user-question-btn-container").style.display = "none"
            document.querySelector(".no-questions").style.display = "block"
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

  
    // document.getElementById("current-page").textContent = `Page ${currentPage}`;

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
            currentPage = Math.ceil((index + 1) / itemsPerPage);
            updatePagination();
    
            // Scroll to the specific item
            let targetIndex = index > questionBoxes.length ? (index - 1) : index
            const targetItem = document.querySelectorAll(".question-box")[targetIndex];
            targetItem.scrollIntoView({ behavior: "smooth" });
        })

        
    })

    answerBtn.addEventListener("click", (e) => {
        console.log(e.target)
        ShowPopup()
    })
    
    if(document.querySelector(".user-login-error-message")){
        let errorMessage = document.querySelector(".user-login-error-message")
        console.log(errorMessage)
        if(errorMessage.textContent != ""){
            setTimeout(() => {
                errorMessage.style.display = "none"
            }, 5000)
        }
    }

    //Script to highlight questions and add keyboard shortcuts
    
    let currentQuestion = 0
    let questionsLength = questionBoxes.length
    let optionKeys = ['a', 'b', 'c', 'd']
    let questionPerPage = 5
    
    
    function highlightQuestion(index){
        currentPage = Math.ceil((index + 1) / questionPerPage);
        updatePagination();
    
        // Scroll to the specific item
        let targetIndex = index > questionBoxes.length ? (index - 1) : index
        const targetItem = document.querySelectorAll(".question-box")[targetIndex];
        targetItem.scrollIntoView({ behavior: "smooth" });
    
        //highlight Questions
        questionBoxes.forEach((el, i) =>{
            el.classList.toggle("highlight", i === index)
        })
    
    }
    
    function selectOption(optionKey){
        let optionIndex = optionKeys.indexOf(optionKey)
        if(optionIndex == -1) return;
        let currentOption = questionBoxes[currentQuestion].querySelectorAll('.check-answer')
        currentOption.forEach((el, index) => {
            el.parentElement.classList.remove("selected")
            
            if(index == optionIndex){
                el.click()
                selectNumber()
            }
        })
    }
    
    function nextQuestion(){
        if(currentQuestion < (questionsLength - 1)){
            currentQuestion++
        }
        highlightQuestion(currentQuestion)
    }
    
    function prevQuestion(){
        if(currentQuestion > 0){
            currentQuestion--
        }
        highlightQuestion(currentQuestion)
    }
    
    document.addEventListener("keydown", (e) => {
        highlightQuestion(currentQuestion)
        let key = e.key.toLowerCase()
        if(popupVisible){
            if(key == "y" || key == "Y"){
                submitAnswer()
            }else if(key == "n" || key == "N"){
                removePopup()
            }
        }else{
            if(optionKeys.includes(key)){
                selectOption(key)
            }else if(key == "n" || key == "N"){
                nextQuestion()
            }else if(key == "r" || key == "R"){
                prevQuestion()
            }else if(key == "s" || key == "S"){
                ShowPopup()
            }
        }
    
        
    })

    highlightQuestion(currentQuestion)

}    

// Script for calculator

let calculatorScreen = document.querySelector(".calculator-screen")
let calculatorButtons = document.querySelectorAll(".calculator-button")
let currentInput = ""
let calculatorOperator = ""
let firstOperand = ""

function updateDisplay(value){
    calculatorScreen.textContent = value
}

function handleButtonClick(value){
    if(value >= 0 && value <= 9){
        currentInput += value
        updateDisplay(currentInput)
    }else if(value === "CLR"){
        currentInput = ""
        calculatorOperator = "" 
        firstOperand = ""
    }else if(value === "="){
        if(calculatorOperator && currentInput){
            currentInput= calculateFunc(firstOperand, currentInput, calculatorOperator)
            updateDisplay(currentInput)
            firstOperand = currentInput
            currentInput = ""
            calculatorOperator = ""
        }
    }else if(['+', '-', '*', '/']){
        if(currentInput){
            firstOperand = currentInput
            calculatorOperator = value
            currentInput = ""
        }
    }else if(value === "DEL"){
        currentInput = currentInput.slice(0, -1)
        updateDisplay(currentInput)
    }
}

function calculateFunc(operand1, operand2, operatorCal){
    let result = 0
    operand1 = parseFloat(operand1)
    operand2 = parseFloat(operand2)

    switch(operatorCal){
        case '+':
            result = operand1 + operand2
            break

        case '-':
            result = operand1 - operand2
            break

        case '*':
            result = operand1 * operand2
            break

        case '/':
            result = operand1 / operand2
            break
    }

    return result.toString()
}

calculatorButtons.forEach(btn => {
    btn.addEventListener("click", function(){
        handleButtonClick(btn.textContent)
    })
})

document.addEventListener("keydown", function(e){
    
})