import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library() # Создаю регистратор для фильтров

@register.filter(name='censor') # Регистрирую фильтр с именем 'censor'
def censor(value):
    # Проверка: только для строк (str), иначе ошибка
    if not isinstance(value, str):
        raise ValueError("Фильтр 'censor' применяется только к переменным строкового типа!")

    # Список плохих слов, которые нужно цензурить
    bad_words = ['редиска', 'ругательство', 'Apple', 'реформы', 'животных']

    result = value  # Копируем входную строку

    for word in bad_words:
        # Беру первую букву слова в нижнем и верхнем регистре
        first_lower = word[0].lower()
        first_upper = word[0].upper()
        rest_lower = word[1:]

        # Цикл для обработки обеих версий первой буквы (верхний и нижний регистр)
        for first in [first_upper, first_lower]:
            # Создаю паттерн для поиска слова с границами слова
            pattern = rf'\b{re.escape(first)}{re.escape(rest_lower)}\b'

            # Создаю замену: первая буква + звёздочки для остальных букв
            replacement = first + '*' * (len(word) - 1)
            # Заменяю найденные слова в result
            result = re.sub(pattern, replacement, result)

    return mark_safe(result)  # Возвращаю результат, помеченный как безопасный для HTML