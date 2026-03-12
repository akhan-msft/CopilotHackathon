"""
BDD tests for the WebSocket Chat app.
Run with:  pytest tests/ --headed   (or omit --headed for headless)

Prerequisite: pip install -r requirements.txt && playwright install chromium
"""
import pytest
from playwright.sync_api import Page, expect
from pytest_bdd import when, then, scenario, parsers

# ── Scenario declarations ─────────────────────────────────────────────────────

@scenario("features/chat.feature", "Login screen loads with user cards")
def test_login_loads():
    pass


@scenario("features/chat.feature", "Selecting a user enters the chat")
def test_select_user():
    pass


@scenario("features/chat.feature", "Chat header shows the selected user")
def test_header():
    pass


@scenario("features/chat.feature", "Sending a message via the Send button")
def test_send_button():
    pass


@scenario("features/chat.feature", "Sending a message via Enter key")
def test_send_enter():
    pass


@scenario("features/chat.feature", "Empty message is not sent")
def test_empty_message():
    pass


@scenario("features/chat.feature", "HTML in messages is escaped")
def test_xss():
    pass


# ── Step definitions ──────────────────────────────────────────────────────────

@when("I open the chat app")
def open_chat_app(page: Page, server_url: str):
    page.goto(server_url)
    page.wait_for_selector(".user-card")


@when("I click the first user card")
def click_first_card(page: Page, ctx: dict):
    card = page.locator(".user-card").first
    ctx["user_name"] = card.locator("span").inner_text()
    card.click()
    page.locator("#chat-screen").wait_for(state="visible")


@then("I see 10 user cards on the login screen")
def ten_cards(page: Page):
    expect(page.locator(".user-card")).to_have_count(10)


@then("the login screen is hidden")
def login_hidden(page: Page):
    expect(page.locator("#login-screen")).to_be_hidden()


@then("the chat screen is visible")
def chat_visible(page: Page):
    expect(page.locator("#chat-screen")).to_be_visible()


@then("the chat header shows the user's name")
def header_shows_name(page: Page, ctx: dict):
    expect(page.locator("#header-name")).to_have_text(ctx["user_name"])


@when(parsers.parse('I type "{text}" in the message input'))
def type_message(page: Page, text: str, ctx: dict):
    ctx["typed_text"] = text
    page.fill("#msg-input", text)


@when("I click the Send button")
def click_send(page: Page):
    page.click("#send-btn")


@when("I press Enter in the message input")
def press_enter(page: Page):
    page.press("#msg-input", "Enter")


@then(parsers.parse('a message bubble contains "{text}"'))
def bubble_has_text(page: Page, text: str):
    expect(page.locator(".bubble .text").filter(has_text=text)).to_be_visible()


@then("the message input is cleared")
def input_cleared(page: Page):
    expect(page.locator("#msg-input")).to_have_value("")


@then("no message bubble is added")
def no_bubble(page: Page):
    expect(page.locator(".msg")).to_have_count(0)


# ── Real-time broadcast – plain pytest with two browser contexts ──────────────

def test_broadcast_between_two_users(browser, server_url):
    """Message sent by User A appears in User B's chat (not marked as 'own')."""
    ctx_a = browser.new_context()
    ctx_b = browser.new_context()
    page_a = ctx_a.new_page()
    page_b = ctx_b.new_page()

    try:
        # User A selects first user card
        page_a.goto(server_url)
        page_a.wait_for_selector(".user-card")
        page_a.locator(".user-card").first.click()
        page_a.locator("#chat-screen").wait_for(state="visible")

        # User B selects second user card
        page_b.goto(server_url)
        page_b.wait_for_selector(".user-card")
        page_b.locator(".user-card").nth(1).click()
        page_b.locator("#chat-screen").wait_for(state="visible")

        # User A sends a message
        page_a.fill("#msg-input", "Hi from user A")
        page_a.click("#send-btn")

        # User B should see the message — not marked as own
        expect(
            page_b.locator(".msg:not(.own) .bubble .text").filter(has_text="Hi from user A")
        ).to_be_visible(timeout=5000)

        # User A should see it marked as own
        expect(
            page_a.locator(".msg.own .bubble .text").filter(has_text="Hi from user A")
        ).to_be_visible()

    finally:
        ctx_a.close()
        ctx_b.close()
