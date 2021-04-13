import sys
import time
import re

import PySimpleGUI as sg

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc


BITCLOUT_LOGIN_URL = 'https://bitclout.com/log-in'
BITCLOUT_WALLET_URL = 'https://bitclout.com/wallet'


def launch_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = uc.Chrome(options=options)
    driver.execute_cdp_cmd("Page.setBypassCSP", {"enabled": True})
    return driver


def bitclout_login(driver, secret):
    wait = WebDriverWait(driver, 20)
    driver.get(BITCLOUT_LOGIN_URL)

    creators_xpath = '/html/body/app-root/div/log-in-or-sign-up-page/div[1]/div/right-bar-creators/div/right-bar-creators-leaderboard/a[1]'
    wait.until(EC.presence_of_element_located((By.XPATH, creators_xpath)))

    secret_text_xpath = '/html/body/app-root/div/log-in-or-sign-up-page/div[1]/div/div/div/log-in-or-sign-up/load-account/div/div[4]/textarea'
    wait.until(EC.presence_of_element_located((By.XPATH, secret_text_xpath)))
    textarea = driver.find_element_by_xpath(secret_text_xpath)
    textarea.send_keys(secret)

    login_btn_xpath = '/html/body/app-root/div/log-in-or-sign-up-page/div[1]/div/div/div/log-in-or-sign-up/load-account/div/div[5]/button'
    wait.until(EC.presence_of_element_located((By.XPATH, login_btn_xpath)))
    button = driver.find_element_by_xpath(login_btn_xpath)
    button.click()
    time.sleep(3)


def sell_tab(driver, sell_url):
    try:
        wait = WebDriverWait(driver, 10)
        driver.execute_script('window.open("' + sell_url + '", "_blank");')
        driver.switch_to.window(driver.window_handles[-1])

        available_coin_xpath = '/html/body/app-root/div/trade-creator-page/app-page/div/div/div[1]/div/trade-creator/div/div/div/trade-creator-form/div[2]/div/div'
        wait.until(EC.presence_of_element_located((By.XPATH, available_coin_xpath)))
        available_coin = driver.find_element_by_xpath(available_coin_xpath)

        inner_html = available_coin.get_attribute("innerHTML").strip()
        if '1e-9' != inner_html[0:4] and float(re.search(r'[0-9]+[.]*[0-9]*', inner_html).group(0)) > 0.0:
            max_button_xpath = '/html/body/app-root/div/trade-creator-page/app-page/div/div/div[1]/div/trade-creator/div/div/div/trade-creator-form/div[3]/div[1]/span[2]/a'
            wait.until(EC.element_to_be_clickable((By.XPATH, max_button_xpath)))
            max_button = driver.find_element_by_xpath(max_button_xpath)
            max_button.click()

            price_per_coin_xpath = '/html/body/app-root/div/trade-creator-page/app-page/div/div/div[1]/div/trade-creator/div/div/div/trade-creator-form/div[3]/div[3]/trade-creator-table/div[3]/div/span'
            wait.until(EC.presence_of_element_located((By.XPATH, price_per_coin_xpath)))

            review_button_xpath = '/html/body/app-root/div/trade-creator-page/app-page/div/div/div[1]/div/trade-creator/div/div/div/trade-creator-form/div[3]/div[4]/a'
            wait.until(EC.element_to_be_clickable((By.XPATH, review_button_xpath)))
            review_button = driver.find_element_by_xpath(review_button_xpath)
            review_button.click()

            confirm_button_xpath = '/html/body/app-root/div/trade-creator-page/app-page/div/div/div[1]/div/trade-creator/div/div/div/trade-creator-preview/div/div[2]/div[2]/button'
            wait.until(EC.element_to_be_clickable((By.XPATH, confirm_button_xpath)))
            confirm_button = driver.find_element_by_xpath(confirm_button_xpath)
            confirm_button.click()

            wallet_button_xpath = '/html/body/app-root/div/trade-creator-page/app-page/div/div/div[1]/div/trade-creator/div/div/div/trade-creator-complete/div/div[2]/div[2]/button'
            wait.until(EC.element_to_be_clickable((By.XPATH, wallet_button_xpath)))

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    except TimeoutException:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        sell_tab(driver, sell_url)


def bitclout_sell(driver, min_price, max_price, min_wallet, max_amount, excluded_users, reverse_order):
    wait = WebDriverWait(driver, 20)
    driver.get(BITCLOUT_WALLET_URL)

    creator_block_xpath = '/html/body/app-root/div/wallet/app-page/div/div/div[1]/div/div[3]/div/div/div[4]'
    wait.until(EC.presence_of_element_located((By.XPATH, creator_block_xpath)))
    creators_block = driver.find_element_by_xpath(creator_block_xpath)

    wallet_amount_xpath = '/html/body/app-root/div/wallet/app-page/div/div/div[1]/div/div[3]/div/div/div[3]/div[2]/span'
    wallet_amount = float(re.sub(r'[^0-9.]', '', driver.find_element_by_xpath(wallet_amount_xpath).get_attribute("innerHTML")))

    amount_sold = 0

    creators = creators_block.find_elements_by_xpath('./div')
    if reverse_order: creators.reverse()

    for creator in creators:
        if min_wallet is not None and min_wallet >= wallet_amount: break
        if max_amount is not None and max_amount <= amount_sold: break
        classes = creator.get_attribute("class").split(" ")
        if 'border-color-grey' in classes: continue

        name = creator.find_element_by_xpath('.//div/a/div[2]/span').get_attribute("innerHTML")
        coin_price = float(re.sub(r'[^0-9.]', '', creator.find_element_by_xpath('.//div/div[1]/div').get_attribute("innerHTML")))
        owned_value = float(re.sub(r'[^0-9.]', '', creator.find_element_by_xpath('.//div/div[2]/div/div[1]').get_attribute("innerHTML")))

        if min_price is not None and min_price > coin_price: continue
        if max_price is not None and max_price < coin_price: continue
        if excluded_users is not None and name in excluded_users: continue

        sell_url = creator.find_element_by_xpath('.//div/div[3]/a[2]').get_attribute("href")
        sell_tab(driver, sell_url)

        wallet_amount = wallet_amount - owned_value
        amount_sold = amount_sold + owned_value


def run_bot(window):
    event, values = window.read(close=False)
    secret = values[0].strip()
    min_price = values[1].strip()
    max_price = values[2].strip()
    min_wallet = values[3].strip()
    max_amount = values[4].strip()
    excluded_users = values[5].strip()
    reverse_order = values[6]

    if not secret:
        sg.popup('Missing fields.', 'The Secret is mandatory.')
        return run_bot(window)

    if min_price is not None and min_price is not '' and min_price.isnumeric():
        sg.popup('Wrong fields.', 'The Minimum Coin Price must be a number.')
        return run_bot(window)

    if max_price is not None and max_price is not '' and max_price.isnumeric():
        sg.popup('Wrong fields.', 'The Maximum Coin Price must be a number.')
        return run_bot(window)

    if min_wallet is not None and min_wallet is not '' and min_wallet.isnumeric():
        sg.popup('Wrong fields.', 'The Minimum Wallet Amount must be a number.')
        return run_bot(window)

    if max_amount is not None and max_amount is not '' and max_amount.isnumeric():
        sg.popup('Wrong fields.', 'The Maximum Amount Sold must be a number.')
        return run_bot(window)

    min_price = float(min_price) if min_price else None
    max_price = float(max_price) if max_price else None
    min_wallet = float(min_wallet) if min_wallet else None
    max_amount = float(max_amount) if max_amount else None
    excluded_users = excluded_users.split(',') if excluded_users else None

    driver = launch_driver()
    bitclout_login(driver, secret)
    bitclout_sell(driver, min_price, max_price, min_wallet, max_amount, excluded_users, reverse_order)


if __name__ == '__main__':
    sg.theme('Light Blue 2')
    layout = [[sg.Text('')],
              [sg.Text('Login Secret', size=(20, 1)), sg.Input(size=(100, 1))],
              [sg.Text('Minimum Coin Price', size=(20, 1)), sg.Input(size=(100, 1))],
              [sg.Text('Maximum Coin Price', size=(20, 1)), sg.Input(size=(100, 1))],
              [sg.Text('Minimum Wallet Amount', size=(20, 1)), sg.Input(size=(100, 1))],
              [sg.Text('Maximum Amount Sold', size=(20, 1)), sg.Input(size=(100, 1))],
              [sg.Text('Excluded Users', size=(20, 1)), sg.Input(size=(100, 1))],
              [sg.Checkbox('Reverse Order', size=(20, 1))],
              [sg.Submit(button_text='Start'), sg.Cancel()]]

    window = sg.Window('BitClout Selling Bot', layout)
    run_bot(window)
    window.close()
    sys.exit(0)
