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
const userQuestionForm = document.querySelector(".user-question-form")
let answerBtn = document.querySelector(".answer-submit-btn")
let popupVisible;

if(document.querySelector(".popup-overlay") || document.querySelector(".user_id-submit-btn")){
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
        userQuestionForm.submit()
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
                yesbtn.href = delLink
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
            startLoadingAnim(useridInput, overlay, useridBtnSpan)
        })
    }

}


//Script to sort Results by Category of Subjects
if(document.querySelector(".category-link")){
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
}

//Script to show answered questions
let questionBoxes = document.querySelectorAll(".question-box")
let questionNumbers = document.querySelectorAll(".question-number")
let smallBoxHead = document.querySelectorAll(".question-box .small-box-head")
let currentPage = 1;
const itemsPerPage = 5;
let currentQuestion = 0

if(document.querySelector(".navigation-link-container")){
    let navigationBtn = document.querySelector(".navigation-link-container button")
    
    navigationBtn.addEventListener("click", function(){
        history.back()
        console.log("hi")
    })
}


if(document.querySelector(".subject-box")){
    const subjectBoxes = document.querySelectorAll(".subject-box")
    subjectBoxes[0].classList.add("visible")
    const subjectMenu = document.querySelectorAll(".menu-wrapper")
    let subjectNumberDiv = document.querySelector(".question-numbers-div")
    let numberOfQuestions = document.querySelector(".number_of_questions")
    let visibleSubject = document.querySelector(".subject-box.visible") 
    // Fetch existing selections when the page loads
    fetch('/get_selections/')
    .then(response => response.json())
    .then(data => {
        const selectedAnswers = data.selected_answers;
        for (const [questionId, answerId] of Object.entries(selectedAnswers)) {
            const radio = document.querySelector(`input[name="question_${questionId}"][value="${answerId}"]`);
            if (radio) {
                radio.checked = true;
            }
        }

        questionBoxes.forEach((box, index) => {
            box.querySelectorAll(".check-answer").forEach((checkEl => {
                if(checkEl.checked){
                questionNumbers[index].classList.add("answered")
                }
            }))
        })
    });

    numberOfQuestions.textContent = `Questions Total: ${subjectBoxes[0].querySelectorAll(".question-box").length}`

       //Script to highlight questions and add keyboard shortcuts
    
    let questionsLength = visibleSubject.querySelectorAll(".question-box").length
    let optionKeys = ['a', 'b', 'c', 'd']
    let questionPerPage = 5

    // function highlightQuestion(index) {
    //     // Scroll to the specific item
    //     let targetIndex = index > questionBoxes.length ? (index - 1) : index
    //     const targetItem = document.querySelectorAll(".question-box")[targetIndex];
    //     targetItem.scrollIntoView({ behavior: "smooth" });
    
    //     //highlight Questions
    //     questionBoxes.forEach((el, i) =>{
    //         el.classList.toggle("highlight", i === index)
    //     })

        
    // }


    function highlightQuestion(index) {
        // Get all parent elements with the specified class name
        const parentElement = document.querySelector(`.subject-box.visible`);
        
        // Get all question boxes within the current parent element
        const questionBoxes = parentElement.querySelectorAll(".question-box");

        // Adjust the targetIndex to handle cases where index might be out of bounds
        let targetIndex = index > questionBoxes.length ? (questionBoxes.length - 1) : index;

        // Scroll to the specific item within the parent element
        const targetItem = questionBoxes[targetIndex];
        if (targetItem) {
            targetItem.scrollIntoView({ behavior: "smooth" });

            // Highlight the question by toggling the 'highlight' class
            questionBoxes.forEach((el, i) => {
                el.classList.toggle("highlight", i === targetIndex);
            });
        }
   
    }


    let controlSmallHead = document.querySelector(".control.small-box-head")
    controlSmallHead.textContent = document.querySelector(".subject-title").textContent
    Array.from(subjectMenu).forEach(menu => {
        
        menu.addEventListener("click", () => {
            categorizeSubjects(menu)
            categorizeSubjectNumbers(menu)
            let currentQuestionIndex = document.querySelector(".subject-box.visible").dataset.currentQuestion
            highlightQuestion(parseInt(currentQuestionIndex))
        })
    })

    questionNumbers.forEach((el, index) => {
        if(subjectMenu[0].dataset.menu.toLowerCase() == el.dataset.number.toLowerCase()){
            el.classList.add("visible")
            el.addEventListener("click", () => {
                highlightQuestion(index)
            })
        }else{
            el.classList.remove("visible")
        }

        
    })

    function categorizeSubjectNumbers(menu){
        questionNumbers.forEach((el, index) => {    
            if(menu.dataset.menu.toLowerCase() == el.dataset.number.toLowerCase()){
                el.classList.add("visible")
                el.addEventListener("click", () => {
                    let indexEl = parseInt(el.textContent) - 1
                    highlightQuestion(indexEl)
                    document.querySelector(".subject-box.visible").dataset.currentQuestion = indexEl
                })
            }else{
                el.classList.remove("visible")
            }
            
        })
    }

    function categorizeSubjects(menu){
        subjectBoxes.forEach((el, index) => {
            if(menu.dataset.menu.toLowerCase() == el.dataset.box.toLowerCase()){
                el.classList.add("visible")
                controlSmallHead.textContent = el.querySelector(".subject-title").textContent
                let questionBoxesLength = el.querySelectorAll(".question-box").length
                numberOfQuestions.textContent = `Questions Total: ${questionBoxesLength}`
                
            }else{
                el.classList.remove("visible")
            }
            
        })  

        questionNumbers.forEach((el, index) => {
            if(menu.dataset.menu.toLowerCase() == el.dataset.number.toLowerCase()){
                el.classList.add("visible")

            }else{
                el.classList.remove("visible")
            }

            
        })

        selectAnswer()
    }

    function selectAnswer(){
        // console.log(visibleSubject.querySelectorAll(".subject-box"))
        // document.querySelector(".subject-box.visible").querySelectorAll(".question-box").forEach((box, index) => {
        //     box.addEventListener("change", function(e){
        //         if(e.target.matches("input")){
        //             questionNumbers[index].classList.add("answered");

        //             // Update the current question to the one that was just answered
        //             // currentQuestion = index;
    
        //             highlightQuestion(index);
                    
        //         }
        //     })
        
        // })

        // Get the currently visible subject box
        let visibleSubjectBox = document.querySelector(".subject-box.visible");

        if (!visibleSubjectBox) return; // Exit if no subject box is visible

        // Get all the question boxes within the visible subject box
        let questions = visibleSubjectBox.querySelectorAll(".question-box");
         console.log(questions.length)
        // Determine the start index for the questionNumbers spans
        let subjectIndex = Array.from(document.querySelectorAll(".subject-box")).indexOf(visibleSubjectBox);
        let startIndex = 0

        subjectBoxes.forEach((box, idx) => {
            if(idx < subjectIndex){
                startIndex += box.querySelectorAll(".question-box").length
            }
        })

        questions.forEach((box, index) => {
            box.addEventListener("change", function(e) {
                if (e.target.matches("input")) {
                    // Add the 'answered' class to the corresponding span in questionNumbers
                    console.log(questionNumbers)
                    questionNumbers[startIndex + index].classList.add("answered");
                    // Highlight the current question
                    highlightQuestion(index);
                    document.querySelector('.subject-box.visible').dataset.currentQuestion = index
                }
            });
        });
    }

    selectAnswer()
    
    if(questionBoxes.length == 0){
            document.querySelector(".user-question-btn-container").style.display = "none"
    }

    answerBtn.addEventListener("click", (e) => {
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

    function selectOptionKey(optionKey){
        let optionIndex = optionKeys.indexOf(optionKey)
        let currentQuestionEl = document.querySelector(".subject-box.visible").querySelectorAll(".question-box")
        console.log(optionKey)
        if(optionIndex == -1) return;
        let currentOption = currentQuestionEl[document.querySelector(".subject-box.visible").dataset.currentQuestion].querySelectorAll('.check-answer')
        console.log(currentOption)
        currentOption.forEach((el, index) => {
            el.parentElement.classList.remove("selected")
            
            if(index == optionIndex){
                console.log(el)
                el.click()
                selectAnswer()
            }
        })
    }
    
    function nextQuestion(){
        // Find the currently visible or active subject box
        const parentElement = document.querySelector('.subject-box.visible'); // Adjust this selector to match your "active" state

        if (!parentElement) return; // Exit if no active subject is found

        // Get all question boxes within the active subject
        const questionBoxes = parentElement.querySelectorAll(".question-box");

        // Retrieve or initialize the currentQuestion for this specific parent element
        let currentQuestion = parentElement.dataset.currentQuestion 
                                ? parseInt(parentElement.dataset.currentQuestion) 
                                : 0;

        // Increment the current question index only if it's within bounds
        if (currentQuestion < questionBoxes.length - 1) {
            currentQuestion++;
        }

        // Store the updated currentQuestion in the dataset of the parent element
        parentElement.dataset.currentQuestion = currentQuestion;

        // Highlight the current question in the active subject
        highlightQuestion(currentQuestion)
    }
    
    function prevQuestion(){

        // Find the currently visible or active subject box
        const parentElement = document.querySelector('.subject-box.visible'); 
        
        if (!parentElement) return; // Exit if no active subject is found

        // Retrieve or initialize the currentQuestion for this specific parent element
        let currentQuestion = parentElement.dataset.currentQuestion 
                                ? parseInt(parentElement.dataset.currentQuestion) 
                                : 0;

        // Decrement the current question index only if it's within bounds
        if(currentQuestion > 0){
            currentQuestion--
        }

        // Store the updated currentQuestion in the dataset of the parent element
        parentElement.dataset.currentQuestion = currentQuestion;

        // Highlight the current question in the active subject
        highlightQuestion(currentQuestion)

    }
    
    document.addEventListener("keydown", (e) => {
        
        let key = e.key.toLowerCase()
        if(popupVisible){
            if(key === "y" || key === "Y"){
                submitAnswer()
            }else if(key == "n" || key == "N"){
                removePopup()
            }
        }else{
            if(optionKeys.includes(key)){
                selectOptionKey(key)
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
        
    

    // Add event listener to save selection on change
    document.querySelectorAll('.check-answer').forEach(radio => {
        radio.addEventListener('change', function() {
            const questionId = this.name.split('_')[1];
            const answerId = this.value;
            fetch('/save_selection/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')  // Add CSRF token for security
                },
                body: JSON.stringify({
                    question_id: questionId,
                    answer_id: answerId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status !== 'success') {
                    console.log('Failed to save selection');
                }
            });
        });
    });
    
    function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
    }

    // Script for calculator
    if(document.querySelector(".calculator-screen")){
        let calculatorScreen = document.querySelector(".calculator-screen")
        let calculatorButtons = document.querySelectorAll(".calculator-button")
        let currentInput = ""
        let calculatorOperator = ""
        let firstOperand = ""
        let dotAdded = false
        let result = ""
        function updateDisplay(value){
            calculatorScreen.textContent = value
        }
        
        function handleButtonClick(value){
            if(value >= 0 && value <= 9){
                currentInput += value
                if(calculatorOperator){
                    updateDisplay(firstOperand + ' ' + calculatorOperator + ' ' + currentInput)
                }else{
                    updateDisplay(currentInput)
                }
        
            }else if(value === "." && !dotAdded){
                if(currentInput === ''){
                    currentInput = '0'
                }
                currentInput += '.'
                dotAdded = true
                updateDisplay(firstOperand + ' ' + calculatorOperator + ' ' + currentInput)
            }else if(value === "CLR"){
                currentInput = ""
                calculatorOperator = "" 
                firstOperand = ""
                updateDisplay('')
            }else if(value === "="){
                if(currentInput !== '' && calculatorOperator !== ''){
                    let secondOperand = currentInput
                    result = calculateFunc(firstOperand, secondOperand, calculatorOperator)
                    dotAdded = result.toString().includes(".")
                    result = dotAdded ? parseFloat(result).toFixed(4) : result
                    updateDisplay(result)
                    currentInput = result
                    firstOperand = ''
                    calculatorOperator = ""
                }else{
                    updateDisplay(currentInput)
                }
            }else if(value === "%"){
                if(currentInput !== ''){
                    currentInput = (parseFloat(currentInput) / 100).toString()
                    updateDisplay(firstOperand + ' ' + calculatorOperator + ' ' + currentInput)
                    dotAdded = currentInput.includes(".")
                }
            }else if(['+', '-', '*', '/'].includes(value)){
                if(currentInput !== ''){
                    if(firstOperand !== '' && calculatorOperator !== ''){
                        firstOperand = calculateFunc(firstOperand, currentInput, calculatorOperator)
                        calculatorOperator = value
                        currentInput = ''
                        dotAdded = false 
                        updateDisplay(firstOperand + ' ' + calculatorOperator)
                    }else{
                        firstOperand = currentInput
                        calculatorOperator = value
                        currentInput = ""
                        dotAdded = false
                        updateDisplay(firstOperand + ' ' + calculatorOperator)
                    }
                }
            }else if(value === "DEL"){
                if(currentInput !== ''){
                if(currentInput.toString().endsWith(".")){
                    dotAdded = false
                }
                currentInput = currentInput.toString().slice(0, -1)
                }else if(calculatorOperator !== ''){
                    calculatorOperator = ''
                }else if(firstOperand !== ''){
                    firstOperand = firstOperand.toString().slice(0, -1)
                }
        
                if(calculatorOperator){
                    updateDisplay(firstOperand + ' ' + calculatorOperator + ' ' + currentInput)
                }else{
                    updateDisplay(firstOperand + currentInput)
                }
            }
            
        }
        
        function calculateFunc(operand1, operand2, operatorCal){
            let num1 = parseFloat(operand1)
            let num2 = parseFloat(operand2)
        
            switch(operatorCal){
                case '+':
                    return  (num1 + num2)
                    
        
                case '-':
                    return  (num1 - num2)
                    
        
                case '*':
                    return  (num1 * num2)
                    
        
                case '/':
                    return  (num1 / num2)
                    
        
                default:
                    return '0'
            }
        
            // return result.toString()
        }
        
        calculatorButtons.forEach(btn => {
            btn.addEventListener("click", function(){
                handleButtonClick(btn.textContent)
            })
        })
        
        document.addEventListener("keydown", function(e){
            let key = e.key
            if((key ==="Enter") || (key === "enter") || (key === "ENTER")){
                e.preventDefault()
                handleButtonClick("=")
            }
        
            if((key >= 0 && key <= 9) || key === '.'){
                handleButtonClick(key)
            }else if((key === '=')){
                handleButtonClick('=')
            }else if((key === 'escape') || (key === 'Escape') || key === 'c'){
                handleButtonClick("CLR")
            }else if((key === 'backspace') || (key === 'Backspace')){
                handleButtonClick('DEL')
            }else if((key === '=')){
                handleButtonClick("=")
            }else if(['+', '-', '*', '/'].includes(key)){
                handleButtonClick(key)
            }else if(key === '%'){
                handleButtonClick("%")
            }
        
            
        })
        
        // Script to open and close calculator
        
        let calculatorShowCtl = document.querySelector(".calculator-menu .calculator-menu-wrapper")
        let calculatorContainer = document.querySelector(".calculator-container")
        
        calculatorShowCtl.addEventListener("click", function(){
            console.log("calc menu")
            calculatorContainer.classList.toggle("slideIn")
        })
    }

    // Animate Instrutions
    let counter = 0
    let carouselItems = document.querySelectorAll(".shrt-container")
    if(document.querySelector(".shrt-container")){
        function nextInstruction(){
            carouselItems[counter].style.animation = "next1 .5s ease forwards"
        
            if(counter >= carouselItems.length - 1){
                counter = 0
            }else{
                counter++
            }
        
            // console.log(counter)
            carouselItems[counter].style.animation = "next2 .5s ease forwards"
        }
        
        function autoslide(){
            setInterval(nextInstruction, 10000)
        }
        
        autoslide()
    }

}    

// Script to persist answers on refresh


        


  // function updatePagination() {
    //     const container = document.querySelector(".question-section");
    //     displayItems(container, itemsPerPage, currentPage);
      
    //     const pageCount = Math.ceil(questionBoxes.length / itemsPerPage);
    //     document.getElementById("pag-prev").disabled = currentPage === 1;
    //     document.getElementById("pag-next").disabled = currentPage === pageCount;
    // }

// Theme Customization
// const colorButtons = document.querySelectorAll('.color-choice')

// function changeThemeColor(pageColor, sidebarColor, sbHoverClr, headTextClr, selectedClr){
//     document.documentElement.setProperty('--page-clr', pageColor)
//     document.documentElement.setProperty('--main-sidebar-clr', sidebarColor)
//     document.documentElement.setProperty('--main-sb-hv-clr', sbHoverClr)
//     document.documentElement.setProperty('--head-text-clr', headTextClr)
//     document.documentElement.setProperty('--q-selected-btn-clr', selectedClr)
// }

// const savedPageColor  = localStorage.getItem('chosenPageColor')
// const savedSidebarColor  = localStorage.getItem('chosenSidebarColor')
// const savedSbHoverClr  = localStorage.getItem('chosenSbHoverClr')
// const savedHeadTextClr  = localStorage.getItem('chosenHeadTextClr')
// const savedSelectedClr  = localStorage.getItem('chosenSelectedClr')
// if(savedPageColor, savedSidebarColor, savedSbHoverClr, savedHeadTextClr, savedSelectedClr){
//     changeThemeColor(savedPageColor, savedSidebarColor,  savedSbHoverClr,savedHeadTextClr, savedSelectedClr)
// }

// colorButtons.forEach((btn, index) => {
//     btn.addEventListener('click', function(){
//         const chosenPageColor = this.getAttribute("data-page-clr")
//         const chosenSidebarColor = this.getAttribute("data-side-bar-clr")
//         const chosenSbHoverClr = this.getAttribute("data-sb-hv-clr")
//         const chosenHeadTextClr = this.getAttribute("data-head-text-clr")
//         const chosenSelectedClr = this.getAttribute("data-selected-btn-clr")

//         changeThemeColor(chosenPageColor, chosenSidebarColor, chosenSbHoverClr, chosenHeadTextClr, chosenSelectedClr)

//         localStorage.setItem("chosenPageColor", chosenPageColor)
//         localStorage.setItem("chosenSidebarColor", chosenSidebarColor)
//         localStorage.setItem("chosenSbHoverClr", chosenSbHoverClr)
//         localStorage.setItem("chosenHeadTextClr", chosenHeadTextClr)
//         localStorage.setItem("chosenSelectedClr", chosenSelectedClr)
//     })
// })

  // function displayItems(container, itemsPerPage, page) {
    //     const start = (page - 1) * itemsPerPage;
    //     const end = start + itemsPerPage;
      
    //     container.querySelectorAll(".question-box").forEach((item, index) => {
    //       if (index >= start && index < end) {
    //         item.style.display = "block";
    //       } else {
    //         item.style.display = "none";
    //       }
    //     });
      
    //     // document.getElementById("current-page").textContent = `Page ${page}`;
    // }