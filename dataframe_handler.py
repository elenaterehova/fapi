import pandas as pd
from typing import NamedTuple, Dict, List


class RowItemsInfo(NamedTuple):
    items: str
    cost: str


class CategoryInfo(NamedTuple):
    id: str
    name: str
    title: str
    items: RowItemsInfo


class DataFrameHandler:
    """Класс для работы с таблицой из Exel"""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def get_info(self) -> dict:
        result = []

        # Получаем данные из _bypassing_df
        all_category = self._bypassing_df()

        for category_id, category_items in all_category.items():
            if category_id is None:
                continue

            # Первый элемент содержит информацию о категории
            main_category = category_items[0]

            # Формируем items для категории
            items_list = []
            for item in category_items:
                # Пропускаем пустые items
                if not item.items.items:
                    continue

                item_dict = {
                    "service": item.items.items,
                    "cost": item.items.cost
                }
                items_list.append(item_dict)

            # Формируем словарь категории
            category_dict = {
                "id": str(main_category.id),
                "name": main_category.name,
                "title": main_category.title,
                "items": items_list
            }

            result.append(category_dict)

        return result

    def _get_category_info(self, series: pd.Series) -> CategoryInfo:
        id = series.iloc[0]
        name = series.iloc[1]
        title = series.iloc[2]
        row_items_info = RowItemsInfo(items=series.iloc[3], cost=series.iloc[4])
        category_info = CategoryInfo(id=id, name=name, title=title, items=row_items_info)
        return category_info

    def _bypassing_df(self):
        all_category: dict[str, list[CategoryInfo]] = {}
        category_index = None
        for rows, data in self.df.iterrows():
            id = data.iloc[0]
            if id != "" and id != category_index:
                category_index = id
            category_info = self._get_category_info(series=data)
            all_category.setdefault(category_index, []).append(category_info)
        return all_category
