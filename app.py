import os  # Para manejar rutas del sistema
from flask import Flask, render_template, request, redirect, url_for
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url_categoria = request.form["url_categoria"]
        num_paginas = int(request.form["num_paginas"])
        
        # Iniciar scraping
        ruta_guardado = scrape_data(url_categoria, num_paginas)
        
        return render_template("index.html", mensaje=f"Archivo guardado en: {ruta_guardado}")

    return render_template("index.html")

def scrape_data(url_categoria, num_paginas):
    driver = webdriver.Chrome()
    datos_totales = []

    for pagina in range(1, num_paginas + 1):
        url = f"{url_categoria}&current_page={pagina}"
        driver.get(url)
        time.sleep(10)
        driver.refresh()
        time.sleep(10)

        productos = driver.find_elements(By.CLASS_NAME, "contenedor-producto.ng-star-inserted")
        
        for i in range(len(productos)):
            try:
                productos = driver.find_elements(By.CLASS_NAME, "contenedor-producto.ng-star-inserted")
                producto = productos[i]
                producto.click()
                time.sleep(5)

                contenedor_sku = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "card-body"))
                )
                sku = contenedor_sku.find_element(By.TAG_NAME, "b").text.strip()

                contenedor_padre = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "col-md-12.d-none.d-lg-block.ng-star-inserted"))
                )
                contenido_completo = contenedor_padre.get_attribute("innerHTML")
                
                soup = BeautifulSoup(contenido_completo, "html.parser")
                tabla = soup.find("table", {"class": "table"})

                if tabla:
                    filas = tabla.find_all("tr")
                    for fila in filas:
                        celdas = [celda.text.strip() for celda in fila.find_all(["td", "th"])]
                        if celdas:
                            celdas.insert(0, sku)
                            datos_totales.append(celdas)

                driver.back()
                time.sleep(5)

            except Exception as e:
                print(f"Error al procesar un producto: {e}")
                driver.back()
                time.sleep(5)

    # 📌 Obtener la ruta del escritorio del usuario
    escritorio = os.path.join(os.path.expanduser("~"), "Desktop")  # Windows / Linux / Mac
    ruta_archivo = os.path.join(escritorio, "productos_completos.xlsx")

    # Guardar el archivo Excel en el escritorio
    df = pd.DataFrame(datos_totales)
    df.to_excel(ruta_archivo, index=False, header=False)
    print(f"Archivo Excel guardado en: {ruta_archivo}")

    driver.quit()

    return ruta_archivo

if __name__ == "__main__":
    app.run(debug=True)
