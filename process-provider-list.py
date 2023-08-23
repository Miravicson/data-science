#!/usr/bin/env python
# coding: utf-8

import sys

import pandas as pd


def format_with_proper_columns(df: pd.DataFrame):
    column_map = {
        "Address": "address",
        "City": "city",
        "Retail": "retailTier",
        "Provider Name": "name",
        "S/N": "serialNumber",
        "SERVICE TYPE": "serviceType",
        "State": "state",
    }
    df.rename(columns=column_map, inplace=True)
    df["corporateTier"] = df["retailTier"]


def convert_col_data_to_title_case(df: pd.DataFrame) -> None:
    def convert_to_title_case(string_or_other: str | int) -> str | int:
        if not isinstance(string_or_other, str):
            return string_or_other
        return string_or_other.title()

    for column in df.columns:
        df[column] = df[column].apply(convert_to_title_case)


def replace_missing_cities_with_state(df: pd.DataFrame) -> None:
    df["city"].fillna(df["state"], inplace=True)


def get_df_with_multi_cities(df: pd.DataFrame) -> pd.DataFrame:
    multi_city_idx = [i[0] for i in enumerate(df["city"].str.contains("/")) if i[1]]
    df_with_multi_city = pd.DataFrame(
        df.loc[multi_city_idx, :].to_numpy(), columns=df.columns
    )
    df.drop(multi_city_idx, inplace=True)
    return df_with_multi_city


def explode_df_by_city(s: pd.Series) -> pd.DataFrame:
    df_cols = list(s.keys())
    combined_city = s["city"]
    new_df = pd.DataFrame(columns=df_cols)
    for city in combined_city.split("/"):
        new_df = new_df.append({**s, "city": city}, ignore_index=True)
        # new_df = pd.concat([new_df, new_dict])
    return new_df


def add_multi_city_rows(df: pd.DataFrame, multi_city_df: pd.DataFrame):
    for i in multi_city_df.index:
        df = pd.concat([df, explode_df_by_city(multi_city_df.loc[i])])
    return df


def process_excel_to_json(filename: str) -> None:
    """Takes a filename of an excel file from command line and generates
    cleaned json file stored in a "provider-list.json"

    Args:
        filename (str): filename of a provider list excel file
        The high-level processes performed include
        1. Read the Excel file
        2. Formats the data frame with code-conducive column names
        2. Format the text in the column consistently with title case
        3. For each row with a missing city value it replaces the value of the city with the value of the state
        4. For each row with multiple cities it generates new rows for each of the cities while keeping every other column but the city column the same. The new rows generated have their city value to be one of each of the cities from the previous row.
    """
    df = pd.read_excel("provider-list-08-2023.xlsx")
    format_with_proper_columns(df)
    convert_col_data_to_title_case(df)
    replace_missing_cities_with_state(df)
    df = add_multi_city_rows(df, get_df_with_multi_cities(df))
    with open("provider-list.json", "w") as provider_list:
        df.to_json(provider_list, orient="records")


if __name__ == "__main__":
    filename = sys.argv[1]
    if not filename:
        raise Exception("You must supply a filename when running the file")
    process_excel_to_json(filename)
