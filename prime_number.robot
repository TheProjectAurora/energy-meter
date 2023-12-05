* Settings *
Library  Browser
Suite Setup  Open Browser
Suite Teardown  Close Browser

* Variables *
${HEADLESS}    False

* Test Cases *
Get 100 first primenumbers with fetch
    Get primenumbers with one fetch     100      42



* Keywords *
Open Browser
    New Browser  headless=${HEADLESS}
    New Page   http://localhost:3000/

Get primenumbers with one fetch
    [Arguments]     ${amount}       ${last}
    Fill Text       id=primeNumberInput         ${amount}
    Click           id=calculateButton
    Get Text        id=primeContainer    contains     ${last}

