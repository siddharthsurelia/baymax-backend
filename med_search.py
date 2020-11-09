def search_medname(med_name):
	from selenium import webdriver
	from selenium.webdriver.chrome.options import Options
	from selenium.webdriver.common.by import By
	from selenium.webdriver.common.keys import Keys
	from selenium.webdriver.support.ui import WebDriverWait
	from selenium.webdriver.support.expected_conditions import presence_of_element_located
	import time
	import sys
	import urllib.parse as urlparse

	chrome_driver_path = "C:\\Users\\I518711\\Documents\\BITS\\BITS 3rd Sem\\Database Systems and Applications\\Baymax\\chromedriver.exe"

	chrome_options = Options()
	chrome_options.add_argument('--headless')
	webdriver = webdriver.Chrome(
		executable_path=chrome_driver_path, options=chrome_options
	)

	med_name = urlparse.quote(med_name)
	url = "https://www.1mg.com/search/all?name=" + med_name

	with webdriver as driver:
		# Set timeout time
		wait = WebDriverWait(driver, 10)
		# retrive url in headless browser
		driver.get(url)

		location = None

		elems = driver.find_elements_by_tag_name("a")
		for elem in elems:
			href = elem.get_attribute("href")
			if href is not None and "https://www.1mg.com/drugs/" in href:
				location = href
				print(location)
				break

		if location is not None:
			driver.get(location)

			wait.until(presence_of_element_located((By.ID, "drug_header")))
			# time.sleep(3)
			name = driver.find_elements_by_class_name("DrugHeader__title___1NKLq")
			manufacturer = driver.find_elements_by_class_name("DrugHeader__meta-value___vqYM0")
			composition = driver.find_elements_by_class_name("saltInfo")
			symptoms = driver.find_elements_by_class_name("DrugOverview__uses___1jmC3")
			side_effects = driver.find_elements_by_class_name("DrugOverview__list-container___2eAr6")
			substitutes = driver.find_elements_by_class_name("SubstituteItem__name___PH8Al")
			substitutes_price = driver.find_elements_by_class_name("SubstituteItem__unit-price___MIbLo")

			name = name[0].text
			manufacturer = manufacturer[0].text
			composition = composition[0].text
			symptoms_list = [s.text for s in symptoms]
			symptoms_list = symptoms_list[0].split("\n")
			side_effects_list = [s.text for s in side_effects]
			side_effects_list = side_effects_list[0].split("\n")
			substitutes_list = [s.text for s in substitutes]
			substitutes_price_list = [s.text for s in substitutes_price]

			data = {
				"name": name,
				"manufacturer": manufacturer,
				"composition": composition,
				"symptoms": symptoms_list,
				"side_effects": side_effects_list,
				"substitutes": dict(zip(substitutes_list, substitutes_price_list))
			}
		else:
			data = None

		# must close the driver after task finished
		driver.close()

	return data



