Feature: WebSocket Chat App

  Scenario: Login screen loads with user cards
    When I open the chat app
    Then I see 10 user cards on the login screen

  Scenario: Selecting a user enters the chat
    When I open the chat app
    And I click the first user card
    Then the login screen is hidden
    And the chat screen is visible

  Scenario: Chat header shows the selected user
    When I open the chat app
    And I click the first user card
    Then the chat header shows the user's name

  Scenario: Sending a message via the Send button
    When I open the chat app
    And I click the first user card
    And I type "Hello World" in the message input
    And I click the Send button
    Then a message bubble contains "Hello World"
    And the message input is cleared

  Scenario: Sending a message via Enter key
    When I open the chat app
    And I click the first user card
    And I type "Enter key test" in the message input
    And I press Enter in the message input
    Then a message bubble contains "Enter key test"

  Scenario: Empty message is not sent
    When I open the chat app
    And I click the first user card
    And I click the Send button
    Then no message bubble is added

  Scenario: HTML in messages is escaped
    When I open the chat app
    And I click the first user card
    And I type "<script>alert(1)</script>" in the message input
    And I click the Send button
    Then a message bubble contains "<script>alert(1)</script>"
