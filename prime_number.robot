* Settings *
Library  Browser
Suite Setup  Open Browser
Suite Teardown  Close Browser

* Variables *
${HEADLESS}    False
${AMOUNT OF PRIMENUMBERS}    100
${LAST PRIMENUMBER}    541

* Test Cases *
Get 100 first primenumbers with fetch
    Get primenumbers with one fetch     ${AMOUNT OF PRIMENUMBERS}      ${LAST PRIMENUMBER}

Get 100 first primenumbers with multiple fetches
    Get primenumbers with multiple fetches    ${AMOUNT OF PRIMENUMBERS}    ${LAST PRIMENUMBER}

* Keywords *
Open Browser
    New Browser  headless=${HEADLESS}
    New Page   http://localhost:3000/

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

