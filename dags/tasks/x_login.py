from airflow.decorators import task

@task
def x_login(X_USERNAME, X_PASSWORD):
    from playwright.sync_api import sync_playwright
    # from config import Config

    username = X_USERNAME
    password = X_PASSWORD

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://twitter.com/i/flow/login?redirect_after_login=%2Fhome")

        page.wait_for_selector("input[autocomplete='username']", timeout=10000)
        page.fill("input[autocomplete='username']", username)
        page.get_by_role("button", name="Next").click()

        page.wait_for_selector("input[name='password']", timeout=10000)
        page.fill("input[name='password']", password)
        page.get_by_test_id("LoginForm_Login_Button").click()

        page.wait_for_url("**/home", timeout=300000)
        print("[INFO] Final URL:", page.url)

        # Save storage state into the file.
        context.storage_state(path="dags/utils/state.json")
        browser.close()