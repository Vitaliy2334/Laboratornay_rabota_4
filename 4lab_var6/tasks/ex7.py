"""
Выберите произвольную дифференцируемую и интегрируемую
функцию одной переменной. С помощью модуля symPy найдите и
отобразите ее производную и интеграл в аналитическом и
графическом виде. Напишите код для решения произвольного
нелинейного урванения и системы нелинейных уравнений.
"""

from sympy import *


def first_part():
    x = Symbol('x')
    func = x ** 2
    print('Функция: ', str(func))
    print('Производная: ', end='')
    differencial = diff(func)
    pprint(differencial)
    plot(differencial)

    print('\nИнтеграл: ')
    integral = integrate(func)
    pprint(integral)
    print('\n')
    plot(integral)


def solution(*equalities):
    if len(equalities) == 1:
        return solve(equalities[0])
    return solve_poly_system(equalities)


def second_part():
    x, y = symbols('x y')
    eq1 = Equality(3, x ** 2 - x * y)
    eq2 = Equality(-2, y ** 2 - x * y)
    eq3 = Equality(x ** 2, -2)
    pprint(solution(eq1, eq2))
    pprint(solution(eq3))


if __name__ == '__main__':
    first_part()
    print('=' * 90)
    second_part()