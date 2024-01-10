* Settings *
Library  Browser
Suite Setup  Open Browser
Suite Teardown  Close Browser
Test Teardown   Click  id=resetButton

* Variables *
${SERVER}                    nodejs
${URL}                       http://localhost:3000/
${HEADLESS}                  ${FALSE}
${AMOUNT OF PRIMENUMBERS}    100
${LAST PRIMENUMBER}          541

* Test Cases *
Get x number of first primenumbers with single fetch
    Get primenumbers    calculateButton     ${AMOUNT OF PRIMENUMBERS}      ${LAST PRIMENUMBER}

Get x number of first primenumbers with multiple fetches
    Get primenumbers  nextPrimesButton   ${AMOUNT OF PRIMENUMBERS}    ${LAST PRIMENUMBER}

* Keywords *
Open Browser
    New Browser  headless=${HEADLESS}
    Set URL
    New Page     ${URL}

Set URL
    Run Keyword If    '${SERVER}' == 'tomcat'    Set Suite Variable    ${URL}    http://localhost:8080/prime_numbers_java/

Get primenumbers
    [Arguments]    ${calculatebutton}    ${amount}       ${last}
    Fill Text       id=primeNumberInput         ${amount}
    Click           id=${calculatebutton}
    Wait For Condition    Text        id=primeContainer    contains     ${last}    timeout=30 s

