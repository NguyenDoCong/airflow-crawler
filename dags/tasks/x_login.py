def x_login(X_USERNAME, X_PASSWORD, **kwargs):
    from playwright.sync_api import sync_playwright

    username = X_USERNAME
    password = X_PASSWORD

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        try:
            page.goto("https://x.com/i/flow/login")
            page.wait_for_selector("input[autocomplete='username']", timeout=10000)
            page.fill("input[autocomplete='username']", username)
            page.get_by_role("button", name="Next").click()
            page.wait_for_selector("input[name='password']", timeout=10000)
            page.fill("input[name='password']", password)
            page.get_by_test_id("LoginForm_Login_Button").click()
            page.wait_for_url("**/home", timeout=300000)
            print("[INFO] Final URL:", page.url)
        except Exception as e:
            print(f"[ERROR] Error during login: {e}")
        try:
            context.storage_state(path="dags/utils/state.json")
            print("[INFO] Storage state saved successfully.")
        except Exception as e:
            print(f"[ERROR] Error saving storage state: {e}")
        browser.close()