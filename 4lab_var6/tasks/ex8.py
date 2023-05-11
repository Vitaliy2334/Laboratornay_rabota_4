"""
С помощью модуля pandas отобразите:
1) 10 самых маленьких и самых больших стран мира по территории;
2) 10 самых маленьких и самых больших стран мира по населению;
3) все франкоязычные страны мира;
4) только островные государства;
5) все страны, находящиеся в южном полушарии.
Сгруппируйте страны:
    по первой букве;
    по населению;
    по территории.
Программно сохраните в таблицу Excel.
все страны с выборочной информацией:
название, столица, население, территория, валюта, широта, долгота.
"""

import csv
import pandas as pd
from pandas import read_csv
import os

countries_file = os.getcwd() + "\\countries.csv"


def write_to_excel(table):
    names = pd.Series([d.split(',')[0] for d in table.name])
    names.name = 'name'
    lat, lng = zip(*[d.split(',')
                     if isinstance(d, str)
                     else ['nan', 'nan']
                     for d in table.latlng])
    lat, lng = map(pd.Series, (lat, lng))
    lat.name = 'latitude'
    lng.name = 'longitude'
    for_export = pd.concat([names, table[['capital', 'ccn3', 'area', 'currencies']], lat, lng], axis=1)
    with pd.ExcelWriter('exported.xls') as excel_writer:
        for_export.to_excel(excel_writer)


def collision(text):
    print('=' * 100)
    print('=' * 25, text, '=' * 53)
    print('=' * 100)


def main():
    table = read_csv(countries_file, ',')

    collision('largest by AREA')
    print(table.nlargest(n=10, columns='area')[['area', 'name']])  # 10 самых больших стран мира по территории
    collision('smallest by AREA')
    print(table.nsmallest(10, ['area'])[['area', 'name']])

    collision('largest by PEOPLE COUNT')
    print(table.nlargest(10, ['ccn3'])[['ccn3', 'name']])  # 10 самых больших стран мира по населению
    collision('smallest by PEOPLE COUNT')
    print(table.nsmallest(10, ['ccn3'])[['ccn3', 'name']])

    collision('FRENCH countries')
    print(table[table.languages == 'French'][['languages', 'area', 'name']])  # все франкоязычные страны мира

    collision('Islands')
    print(table[table.borders.isnull()][['name']])  # только государства острова(гос-ва, которые ни с кем не граничат)
    # write_to_excel(table=table)

    # все страны, находящиеся в южном полушарии
    collision('Southern Hemisphere')
    print(table.where(pd.Series([float(str(d).split(',')[0]) < 0 for d in table.latlng])).name.dropna())

    for i, group in table.groupby(table.area):  # группировка по территории
        print(str(i) + ': ')
        for j, name in enumerate(group.name, 1):
            print(str(j) + '.', name.split(',')[0])

    for i, group in table.groupby(table.ccn3):  # группировка по населению
        print(str(i) + ': ')
        for j, name in enumerate(group.name, 1):
            print(str(j) + '.', name.split(',')[0])

    for i, group in table.groupby([d[0] for d in table.name]):  # Групировка по первой букве
        print(str(i) + ': ')
        for j, name in enumerate(group.name, 1):
            print(str(j) + '.', name.split(',')[0])


if __name__ == '__main__':
    main()
