* Settings *
Library  Browser
Suite Setup  Go to ELO Main Page
Suite Teardown  Close Browser

* Test Cases *
Caulate the Estimate of your YEL contribution
    Enter YEL income    150000
    Calculate installments for 1-12 months

* Keywords *
Go to ELO Main Page
    New Browser    Chromium    headless=False
    New Page   https://yel-laskuri.elo.fi

Enter YEL income
    [Arguments]    ${income}
    Fill Text   xpath=//input[@id='income']    ${income}

 Calculate installments for 1-12 months
    Click    id=label_installments_1
    Wait For Elements State   xpath=(//span[contains(.,'157 €')])[1]   visible
    Click    id=label_installments_2
     Wait For Elements State   xpath=(//span[contains(.,'157 €')])[1]    visible
    Click    id=label_installments_4
     Wait For Elements State   xpath=(//span[contains(.,'157 €')])[1]    visible
    Click    id=label_installments_6
     Wait For Elements State   xpath=(//span[contains(.,'157 €')])[1]    visible
    Click    id=label_installments_12