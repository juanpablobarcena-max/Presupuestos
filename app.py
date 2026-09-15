import streamlit as st
import pdfplumber
import pandas as pd
import io

# Configuración básica de la página
st.set_page_config(page_title="Destripador de PDFs", page_icon="📄", layout="centered")

st.title("📄 Destripador de Presupuestos (PDF a Excel)")
st.write("Sube un PDF que contenga tablas (cuadros de precios, mediciones, listados) y lo convertiremos en un Excel editable.")

# 1. Cargador de archivos
archivo_pdf = st.file_uploader("Arrastra aquí tu PDF", type=["pdf"])

if archivo_pdf is not None:
    st.info("Analizando el documento...")
    
    tablas_extraidas = []
    
    # 2. Abrir el PDF con pdfplumber
    with pdfplumber.open(archivo_pdf) as pdf:
        # Recorremos todas las páginas del PDF
        for num_pagina, pagina in enumerate(pdf.pages):
            # Extraemos las tablas de la página actual
            tablas_pagina = pagina.extract_tables()
            
            for tabla in tablas_pagina:
                # Convertimos la tabla en un DataFrame de Pandas
                df = pd.DataFrame(tabla[1:], columns=tabla[0])
                tablas_extraidas.append(df)
                
    # 3. Mostrar resultados y exportar
    if len(tablas_extraidas) > 0:
        st.success(f"¡Éxito! Se han encontrado {len(tablas_extraidas)} tabla(s) en el documento.")
        
        # Unimos todas las tablas encontradas en una sola por si ocupa varias páginas
        df_final = pd.concat(tablas_extraidas, ignore_index=True)
        
        # Mostramos una previsualización en la web
        st.write("### Previsualización de los datos:")
        st.dataframe(df_final, use_container_width=True)
        
        # 4. Botón para descargar a Excel
        # Creamos un archivo Excel en la memoria RAM (sin guardarlo en el servidor)
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
            df_final.to_excel(writer, index=False, sheet_name="Datos_Extraidos")
        
        st.download_button(
            label="⬇️ Descargar archivo Excel (.xlsx)",
            data=buffer_excel.getvalue(),
            file_name="Tabla_Extraida.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    else:
        st.warning("No se ha detectado ninguna tabla con formato claro en este PDF.")
