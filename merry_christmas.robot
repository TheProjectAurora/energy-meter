* Settings *
Library  Browser
Suite Setup  Open Browser
Test Teardown    Close Page
Suite Teardown  Close Browser

* Variables *
${HEADLESS}    False

* Test Cases *
Go to Season Greetings gif
    Go to Season Greetings page with gif
    Sleep    2s

Go to Season Greetings image
    Go to Season Greetings page with image
    Sleep    2s


* Keywords *
Open Browser
    New Browser  headless=${HEADLESS}

Go to Season Greetings page with image
    New Page   http://localhost:3000/index.html   

Go to Season Greetings page with gif
    New Page   http://localhost:3000/index2.html
