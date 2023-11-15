* Settings *
Library  Browser
Suite Setup  Open Browser
Test Teardown    Close Page
Suite Teardown  Close Browser

* Variables *
${URL}    http://localhost:3000/index.html
${HEADLESS}    False

* Test Cases *
Go to Season Greetings video
    Go to Season Greetings page with video
    Sleep    2s

Go to Season Greetings image
    Go to Season Greetings page with image
    Sleep    2s


* Keywords *
Open Browser
    New Browser  headless=${HEADLESS}

Go to Season Greetings page with image
    New Page   http://localhost:3000/index.html   
    Set Viewport Size   1920    900

Go to Season Greetings page with video
    New Page   http://localhost:3000/index2.html
    Set Viewport Size   1920    900