import fastapi as fast
import pandas as pd
import uvicorn 
import pdfplumber as pf
import os
tables = []
with pf.open(os.getcwd()+"\\ML\\cc_st.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        cleaned_text = text.strip()
        tables_on_page = page.extract_tables({
            'vertical_strategy':'text',
            'horizontal_strategy': 'text',
            'intersection_x_tolerance': 10,
            'intersection_y_tolerance': 10,
        })
        if tables_on_page:
            for table in tables_on_page:
                if table:
                    tables.append({
                        'page':pdf.pages.index(page)+1,
                        'data':table
                    })
    for table in tables:
        print(pd.DataFrame(table['data']).dropna(axis=0))