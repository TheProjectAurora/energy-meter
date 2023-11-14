* Settings *
Library  Browser
Suite Setup  Open Browser
Suite Teardown  Close Browser

* Variables *
${URL}    http://localhost:3000/index.html
${HEADLESS}    False

* Test Cases *
Go to Season Greetings video
    Go to Season Greetings page with    video
    Sleep    2s

Go to Season Greetings image
    Go to Season Greetings page with    picture
    #Sleep    2s

* Keywords *
Open Browser
    Sleep     1s
    New Browser  headless=${HEADLESS}


Go to Season Greetings page with
    [Arguments]  ${media}
    New Page   ${URL}?media=${media}
    Set Viewport Size   2560    1360