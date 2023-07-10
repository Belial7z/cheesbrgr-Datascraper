import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://bravsearch.bea-brak.de/bravsearch/index.brak")
time.sleep(2)

# Dropdown-Tabelle öffnen
dropdown_button = driver.find_element(By.ID, "searchForm:txtSpecialization_label")
dropdown_button.click()

# Option auswählen
option = driver.find_element(By.XPATH, "//li[contains(text(), 'Arbeitsrecht')]")
option.click()

# Suche starten
suche_starten_button = driver.find_element(By.ID, "searchForm:cmdSearch")
suche_starten_button.click()
time.sleep(20)

# Ergebnisse speichern
data = []

# Anwälte durchgehen
i = 78
page_number = 15  # Startseite für den Inkrementwert
previous_num_results = 0
last_loaded_page = 0
no_new_entries_page = 0

while True:
    try:
        # Element "Info" klicken
        info_element = driver.find_element(By.XPATH, f"//a[@id='resultForm:dlResultList:{i}:j_idt208']")

        # Scrollen zum Element
        driver.execute_script("arguments[0].scrollIntoView(true);", info_element)
        time.sleep(1)

        # Klick auf das Element
        info_element.click()
        time.sleep(1)

        # Adresse extrahieren, falls vorhanden
        try:
            adresse_element = driver.find_element(By.XPATH,
                                                  "//div[@id='resultDetailForm:tabPersonal:j_idt352:textEntry']//div[@class='cssColResultDetailText cssColResultDetailTextLine']")
            Adresse = adresse_element.text.strip()
        except:
            Adresse = ""

        # Kanzlei extrahieren, falls vorhanden
        try:
            kanzlei_element = driver.find_element(By.XPATH,
                                                  "//div[@id='resultDetailForm:tabPersonal:j_idt345:textEntry']//div[@class='cssColResultDetailText cssColResultDetailTextLine']")
            Kanzlei = kanzlei_element.text.strip()
        except:
            Kanzlei = ""

        # Namen extrahieren, falls vorhanden
        try:
            name_element = driver.find_element(By.XPATH, "//div[@id='resultDetailForm:tabPersonal:j_idt306:textEntry']//div[@class='cssColResultDetailText cssColResultDetailTextLine']")
            Name = name_element.text.strip()
        except:
            Name = ""

        # E-Mail-Adresse extrahieren, falls vorhanden
        try:
            email_element = driver.find_element(By.XPATH, "//div[@id='resultDetailForm:tabPersonal:j_idt388:textEntry']//div[@class='cssColResultDetailText cssColResultDetailTextLine']")
            email = email_element.text.strip()
        except:
            email = ""

        # Telefonnummer extrahieren, falls vorhanden
        try:
            telefon_element = driver.find_element(By.XPATH, "//div[@id='resultDetailForm:tabPersonal:j_idt367:textEntry']//div[@class='cssColResultDetailText cssColResultDetailTextLine']")
            Telefon = telefon_element.text.strip()
        except:
            Telefon = ""

        # Daten in Liste speichern, falls mindestens ein Wert vorhanden ist
        if Name or email or Telefon:
            data.append({'Kanzlei': Kanzlei, 'Adresse': Adresse, 'Name': Name, 'Telefon': Telefon, 'E-Mail': email})

        # Fenster schließen
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        time.sleep(0)

        i += 1

        # Zufällige Wartezeit zwischen den Anfragen (1 bis 5 Sekunden)
        delay = random.uniform(1, 4)
        time.sleep(delay)

    except:
        # Prüfen, ob neue Ergebnisse geladen wurden
        current_num_results = len(data)
        if current_num_results == previous_num_results:
            # Keine neuen Ergebnisse geladen, Seitennummer speichern und Schleife beenden
            no_new_entries_page = page_number
            break

        previous_num_results = current_num_results

        # Auf nächste Seite wechseln
        try:
            next_page_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[@class='ui-paginator-next ui-state-default ui-corner-all']"))
            )
        except:
            break  # Wenn kein weiterer Seitenlink vorhanden ist, brich die Schleife ab

        # Scrollen zum nächsten Seitenlink
        driver.execute_script("arguments[0].scrollIntoView(true);", next_page_element)
        time.sleep(1)

        # Klick auf den nächsten Seitenlink
        next_page_element.click()

        # Warte, bis das Dialogfeld "Einträge werden geladen" verschwindet
        WebDriverWait(driver, 10).until(EC.invisibility_of_element_located((By.XPATH,
                                                                            "//div[@class='ui-dialog-titlebar ui-widget-header ui-helper-clearfix ui-corner-top ui-draggable-handle']")))

        time.sleep(15)

        page_number += 1  # Inkrementiere die Seitenzahl für den nächsten Seitenwechsel

# Löschen der Cookies
driver.delete_all_cookies()

# Seite neu laden
driver.refresh()
time.sleep(5)

# Dropdown-Tabelle öffnen
dropdown_button = driver.find_element(By.ID, "searchForm:txtSpecialization_label")
dropdown_button.click()

# Option auswählen
option = driver.find_element(By.XPATH, "//li[contains(text(), 'Arbeitsrecht')]")
option.click()

# Suche starten
suche_starten_button = driver.find_element(By.ID, "searchForm:cmdSearch")
suche_starten_button.click()
time.sleep(20)

# Zur letzten geladenen Seite + 1 navigieren
for _ in range(no_new_entries_page - last_loaded_page):
    try:
        next_page_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[@class='ui-paginator-next ui-state-default ui-corner-all']"))
        )
        next_page_element.click()
        time.sleep(5)
    except:
        break

# Browser schließen
driver.quit()
