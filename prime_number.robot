* Settings *
Library  Browser
Suite Setup  Open Browser
Suite Teardown  Close Browser

* Variables *
${SERVER}                    nodejs
${URL}                       http://localhost:3000/
${HEADLESS}                  ${FALSE}
${AMOUNT OF PRIMENUMBERS}    100
${LAST PRIMENUMBER}          541

* Test Cases *
Get x number of first primenumbers with single fetch
    Get primenumbers with one fetch     ${AMOUNT OF PRIMENUMBERS}      ${LAST PRIMENUMBER}

Get x number of first primenumbers with multiple fetches
    Get primenumbers with multiple fetches    ${AMOUNT OF PRIMENUMBERS}    ${LAST PRIMENUMBER}

* Keywords *
Open Browser
    New Browser  headless=${HEADLESS}
    Set URL
    New Page     ${URL}

Set URL
    Run Keyword If    '${SERVER}' == 'tomcat'    Set Suite Variable    ${URL}    http://localhost:8080/prime_numbers_java/

Get primenumbers with one fetch
    [Arguments]     ${amount}       ${last}
    Fill Text       id=primeNumberInput         ${amount}
    Click           id=calculateButton
    Get Text        id=primeContainer    contains     ${last}

Get primenumbers with multiple fetches
    [Arguments]     ${amount}       ${last}
    Fill Text       id=primeNumberInput         ${amount}
    Click           id=nextPrimesButton
    Get Text        id=primeContainer    contains     ${last}

