import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Dict, Any
import pandas as pd

from dataframe_handler import DataFrameHandler

# Загрузка переменных окружения
load_dotenv()

app = FastAPI(
    title="Google Sheets API",
    description="API для работы с Google Таблицами",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Авторизация в Google Sheets
def get_google_sheet():
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            os.getenv('GOOGLE_SHEETS_CREDENTIALS'),
            ['https://www.googleapis.com/auth/spreadsheets']
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(os.getenv('GOOGLE_SHEET_ID'))
        return sheet
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка подключения к Google Sheets: {str(e)}")


@app.get("/")
def read_root():
    return {"message": "Google Sheets API работает"}


@app.get("/sheets", response_model=List[str])
def list_sheets():
    """Получить список всех листов в таблице"""
    try:
        sheet = get_google_sheet()
        return [worksheet.title for worksheet in sheet.worksheets()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data/{sheet_name}", response_model=List[Dict[str, Any]])
def get_sheet_data(sheet_name: str):
    """Получить все данные из указанного листа"""
    try:
        sheet = get_google_sheet()
        worksheet = sheet.worksheet(sheet_name)

        # Получаем все записи
        records: list[dict] = worksheet.get_all_records()
        if sheet_name == 'prices':
            records_df = pd.DataFrame(records)
            json_info = DataFrameHandler(df=records_df).get_info()
            return json_info
        return records
    except gspread.exceptions.WorksheetNotFound:
        raise HTTPException(status_code=404, detail="Лист не найден")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/data/{sheet_name}/{row}/{col}", response_model=Dict[str, Any])
def get_cell_data(sheet_name: str, row: int, col: int):
    """Получить данные конкретной ячейки"""
    try:
        sheet = get_google_sheet()
        worksheet = sheet.worksheet(sheet_name)

        # Получаем значение ячейки
        value = worksheet.cell(row, col).value
        return {"value": value}
    except gspread.exceptions.WorksheetNotFound:
        raise HTTPException(status_code=404, detail="Лист не найден")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
