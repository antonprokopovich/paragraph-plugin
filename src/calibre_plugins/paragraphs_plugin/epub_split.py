import re
import sys
import os
import zipfile
import tempfile
import shutil

from typing import List

# Добавляем родительскую директорию, чтобы относительный импорт заработал
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, 'beautifulsoup4')

from bs4 import BeautifulSoup

class Token:
    def __init__(self, text, is_word):
        self.text = text
        self.is_word = is_word
    
    def __eq__(self, other):
        return self.text == other.text and self.is_word == other.is_word

    def __repr__(self):
        return f"Token(text={self.text!r}, is_word={self.is_word})"


def tokenize_paragraph(paragraph_text) -> List[Token]:
    """
    Разбивает текст на токены (слова), учитывая что:
      * бывают токены-слова и остальные токены (теги, сноски, разделительные символы, знаки пунктуации);
      * разделительные символы могут быть не только пробелами, но и символами неразрывных пробелов (0xA0);
      * токены могут быть как словами, так и служебными (теги, сноски и тп);
      * токены-слова могут быть обрамлены кавычками, круглыми скобками;
      * внутри тегов (после объявления `<tagName` и до `>` все токены НЕ являются словами (то есть 
        технически названия и значения аттрибутов - это не слова);
    
    :param paragraph_text: Текст абзаца для разбиения.
    :return: Список токенов, каждый из которых содержит мета-данные (является ли он читаемым словом).
    """
    tokens = []  # Инициализируем пустой список для хранения токенов
    
    # Определяем шаблоны регулярных выражений для различных типов токенов:
    
    # 1. Паттерн для тегов: ищет строки, начинающиеся с '<', затем любые символы кроме '>' (0 или более раз),
    # и заканчивающиеся '>'. Это позволит найти такие теги, как <tag>, <tag attr="value"> и т.д.
    tag_pattern = r'<[^>]*>'
    
    # 2. Паттерн для слов, включая слова с дефисами:
    # \b        - граница слова (начало или конец слова)
    # \w+       - один или более буквенно-цифровых символов (буквы, цифры или '_')
    # (?:-\w+)* - ноль или более повторений группы, где дефис и снова одна или более буквенно-цифровых символов
    # \b        - граница слова
    # Этот паттерн позволит найти слова как "слово", так и "нью-йорк", "e-mail" и т.д. как одно цельное слово
    word_pattern = r'\b\w+(?:-\w+)*\b'
    
    # 3. Паттерн для пробельных символов, включая символ неразрывного пробела (0xA0):
    # [\s\u00A0]+ - один или более пробельных символов (\s) или символов с кодом Unicode U+00A0 (\u00A0)
    whitespace_pattern = r'[\s\u00A0]+'
    
    # 4. Паттерн для символов, которые не являются буквами, цифрами, пробелами или дефисом:
    # [^\w\s\u00A0-] - любой символ, который НЕ является буквенно-цифровым (\w), пробельным (\s), неразрывным пробелом (\u00A0) или дефисом (-)
    symbol_pattern = r'[^\w\s\u00A0-]'
    
    # Комбинируем все паттерны в один, используя группы захвата:
    # Каждая пара скобок '()' создает группу захвата, которую мы потом можем использовать для определения типа токена
    combined_pattern = f'({tag_pattern})|({word_pattern})|({symbol_pattern})|({whitespace_pattern})'
    
    # Компилируем комбинированный паттерн в объект регулярного выражения для повышения производительности
    pattern = re.compile(combined_pattern, re.UNICODE)
    
    pos = 0  # Начальная позиция в тексте
    while pos < len(paragraph_text):
        # Ищем совпадение с любым из наших паттернов, начиная с текущей позиции
        match = pattern.match(paragraph_text, pos)
        if match:
            token_text = match.group(0)  # Получаем текст найденного токена
            # Определяем тип токена, проверяя, какая группа захвата сработала
            if match.group(1):  # Если сработала первая группа захвата (тег)
                is_word = False  # Теги не считаются словами
            elif match.group(2):  # Если сработала вторая группа захвата (слово или слово с дефисом)
                is_word = True   # Это слово
            elif match.group(3):  # Если сработала третья группа захвата (символ)
                is_word = False  # Символы не являются словами
            elif match.group(4):  # Если сработала четвертая группа захвата (пробельные символы)
                is_word = False  # Пробельные символы не являются словами
            # Добавляем найденный токен в список токенов
            tokens.append(Token(token_text, is_word))
            pos += len(token_text)  # Перемещаем позицию вперед на длину найденного токена
        else:
            # Если символ не соответствует ни одному из паттернов,
            # мы считаем его отдельным токеном (например, неизвестный или специальный символ)
            token_text = paragraph_text[pos]
            tokens.append(Token(token_text, is_word=False))  # Помечаем его как не слово
            pos += 1  # Перемещаем позицию на один символ
    return tokens  # Возвращаем список токенов

def split_paragraph_into_lines(paragraph_text, line_len):
    """
    Разбивает текст абзаца на строки, содержащие по line_len слов.

    :param paragraph_text: Текст абзаца для разбиения.
    :param line_len: Количество слов в каждой строке (должно быть положительным целым числом).
    :return: Список строк, каждая из которых содержит line_len слов.
    :raises ValueError: Если line_len не является положительным целым числом.
    """
    if not isinstance(line_len, int) or line_len <= 0:
        raise ValueError("line_len должно быть положительным целым числом.")

    tokens = tokenize_paragraph(paragraph_text)
    lines = []
    current_line_tokens = []
    word_count = 0
    idx = 0
    total_tokens = len(tokens)

    while idx < total_tokens:
        token = tokens[idx]
        current_line_tokens.append(token)

        if token.is_word:
            word_count += 1
            idx += 1

            if word_count == line_len:
                # После достижения нужного количества слов, добавляем последующие токены-неслова
                while idx < total_tokens and not tokens[idx].is_word:
                    current_line_tokens.append(tokens[idx])
                    idx += 1

                # Собираем текущую линию в строку и добавляем в список
                line_text = ''.join(t.text for t in current_line_tokens)
                lines.append(line_text)

                # Сбрасываем счетчики для следующей строки
                current_line_tokens = []
                word_count = 0
        else:
            idx += 1

    # Добавляем оставшиеся токены как последнюю строку, если они есть
    if current_line_tokens:
        line_text = ''.join(t.text for t in current_line_tokens)
        lines.append(line_text)

    return lines

# Списки сокращений, после которых пунктуационные знаки не всегда могут считаться знаками, завершающими предложение

# Безусловные сокращения (всегда считаются сокращениями)
unconditional_abbreviations = set([
    # Русские сокращения
    'т.к.', 'т.е.', 'т.н.', 'г.', 'ул.', 'д.', 'рис.', 'табл.', 'стр.', 'п.', 'ч.', 'см.',
    # Английские сокращения
    'e.g.', 'i.e.', 'mr.', 'mrs.', 'ms.', 'dr.', 'prof.', 'fig.', 'vs.', 'sr.', 'jr.'
])

# Условные сокращения, на которых предложение может все таки завершаться
conditional_abbreviations = set([
    # Русские сокращения
    'т.п.', 'т.д.', 'др.', 'пр.', 'руб.',
    # Английские сокращения
    'etc.', 'inc.', 'ltd.'
])

def is_abbreviation(paragraph_text: str, i: int) -> bool:
    """
    Проверяет, является ли знак препинания в позиции i частью локального сокращения.
    То есть функция возвращает True, если знак препинения не является завершающим предложение.
    Важно, что после некоторых сокращений (например, 'т.д.', 'т.п.', 'etc.' и др.) знаки препинания
    иногда могут завершать предложение, в этом случае функция вернет False.

    :param paragraph_text: Текст абзаца.
    :param i: Позиция знака препинания в тексте.
    :return: True, если это сокращение, иначе False.
    """
    # Проверяем, что i находится в пределах строки
    if i < 0 or i >= len(paragraph_text) or len(paragraph_text) == 0:
        return False

    # Ищем начало слова перед знаком препинания
    j = i - 1
    # Пропускаем пробелы
    while j >= 0 and paragraph_text[j].isspace():
        j -= 1
    # Если j < 0, значит, нет символов перед i
    if j < 0:
        return False

    # Собираем слово перед знаком препинания
    abbrev_chars = []
    while j >= 0 and (paragraph_text[j].isalpha() or paragraph_text[j] == '.'):
        abbrev_chars.append(paragraph_text[j])
        j -= 1
    # Если нет букв перед знаком, это не сокращение
    if not abbrev_chars:
        return False

    # Проверяем, что i находится в пределах строки перед обращением к paragraph_text[i]
    if i >= len(paragraph_text):
        return False

    # Формируем потенциальное сокращение
    abbrev = ''.join(reversed(abbrev_chars)) + paragraph_text[i]
    abbrev = abbrev.strip().lower()

    # Проверяем, есть ли оно в списке сокращений
    if abbrev in unconditional_abbreviations:
        return True
    elif abbrev in conditional_abbreviations:
        # Проверяем следующее слово
        k = i + 1
        length = len(paragraph_text)
        # Пропускаем пробелы и знаки препинания
        while k < length and not paragraph_text[k].isalnum():
            k += 1
        if k >= length:
            # Нет следующего слова, считаем, что это конец предложения
            return False
        elif paragraph_text[k].isupper():
            # Следующее слово начинается с заглавной буквы, считаем, что это конец предложения
            return False
        else:
            return True
    else:
        return False

def split_paragraph_into_sentences(paragraph_text) -> List[str]:
    """
    Разбивает текст абзаца предложения.
    Разбиение происходит по завершающим знакам пунктуации: .!?
    При этом завершающие знаки пунктуации исключаются (не считаются) в следующих случаях, если:
      * идут после сокращений (см. функцию is_abbreviation);
      * разделяют цифры (без пробелов), например, числа с плавающей точкой;
      * находятся в тексте аттрибутов тегов;
      * находятся внутри тегов, которые еще не закрыты (чтобы не ломать верстку);
      * после которых идут сразу другие завершающие знаки пунктуации (например, в тексте можно встретить "!!!" 
        или "!?" или "...");

    :param paragraph_text: Текст абзаца для разбиения.
    :return: Список строк-предложений.
    """
    sentences = []             # Список для хранения найденных предложений
    sentence_start = 0         # Индекс начала текущего предложения
    i = 0                      # Текущая позиция в тексте
    length = len(paragraph_text)
    tag_stack = []             # Стек для отслеживания открытых тегов
    inside_attribute = False   # Флаг, показывающий, находимся ли мы внутри значения атрибута

    while i < length:
        char = paragraph_text[i]

        # --- Обработка тегов ---
        if char == '<':
            # Начало тега найдено
            # Ищем позицию закрывающей угловой скобки '>'
            end_tag_pos = paragraph_text.find('>', i)
            if end_tag_pos == -1:
                # Если '>' не найден, тег не закрыт
                # Добавляем оставшийся текст в стек тегов и выходим из цикла
                tag_stack.append(paragraph_text[i:])
                break
            else:
                # Получаем содержимое тега между '<' и '>'
                tag_content = paragraph_text[i+1:end_tag_pos]
                if tag_content.startswith('/'):
                    # Если это закрывающий тег (начинается с '/')
                    if tag_stack:
                        tag_stack.pop()  # Удаляем соответствующий открывающий тег из стека
                else:
                    # Это открывающий тег
                    tag_stack.append(tag_content)
                i = end_tag_pos  # Перемещаем позицию i на конец тега
        elif char in '"\'':
            # Обработка кавычек внутри тегов (значения атрибутов)
            quote_char = char
            i += 1
            # Пропускаем все символы до следующей такой же кавычки
            while i < length and paragraph_text[i] != quote_char:
                i += 1
            # Теперь мы находимся на закрывающей кавычке
        elif char in '.!?':
            # --- Обработка завершающих знаков пунктуации ---
            should_split = True  # Флаг, показывающий, нужно ли разделять предложение

            # 1. Проверка на сокращение
            if is_abbreviation(paragraph_text, i):
                should_split = False  # Не разделяем, если это сокращение

            # 2. Проверка на числа с плавающей точкой
            elif i > 0 and i + 1 < length and paragraph_text[i - 1].isdigit() and paragraph_text[i + 1].isdigit():
                should_split = False  # Не разделяем, если точка между цифрами

            # 3. Проверка, находимся ли мы внутри незакрытого тега
            elif tag_stack:
                should_split = False  # Не разделяем внутри незакрытого тега

            # 4. Проверка на множественные знаки пунктуации
            elif i + 1 < length and paragraph_text[i + 1] in '.!?':
                should_split = False  # Не разделяем, если сразу несколько знаков

            if should_split:
                # Если все проверки пройдены и нужно разделить предложение
                # Извлекаем предложение от sentence_start до текущей позиции i + 1
                sentence = paragraph_text[sentence_start:i + 1].strip()
                if sentence:
                    sentences.append(sentence)  # Добавляем предложение в список
                sentence_start = i + 1  # Обновляем начало следующего предложения
        i += 1  # Переходим к следующему символу

    # --- Обработка оставшегося текста ---
    if sentence_start < length:
        # Если остался текст после последнего завершающего знака
        sentence = paragraph_text[sentence_start:].strip()
        if sentence:
            sentences.append(sentence)  # Добавляем последнее предложение

    return sentences

def merge_adjacent_paragraphs(soup):
    """
    Объединяет последовательные теги <p>, находящиеся на одном уровне и имеющие одинаковые значения
    атрибутов class и style (если атрибут отсутствует, считается, что его значение пустая строка).
    Объединение происходит путём слияния содержимого тегов в первый тег последовательности.
    Атрибуты объединённого тега берутся из первого тега.

    :param soup: Объект BeautifulSoup, представляющий HTML-документ.
    """
    paragraphs = soup.find_all('p')
    i = 0
    while i < len(paragraphs) - 1:
        current_p = paragraphs[i]
        next_p = paragraphs[i + 1]

        # Проверяем, находятся ли теги на одном уровне
        if current_p.parent != next_p.parent:
            i += 1
            continue

        # Получаем атрибуты class и style для обоих тегов
        current_class = current_p.get('class', '')
        next_class = next_p.get('class', '')
        current_style = current_p.get('style', '')
        next_style = next_p.get('style', '')

        # Приводим атрибуты class к строковому виду, если они являются списками
        if isinstance(current_class, list):
            current_class = ' '.join(current_class)
        if isinstance(next_class, list):
            next_class = ' '.join(next_class)

        # Если атрибут отсутствует, считаем его пустой строкой
        if current_class is None:
            current_class = ''
        if next_class is None:
            next_class = ''
        if current_style is None:
            current_style = ''
        if next_style is None:
            next_style = ''

        # Сравниваем атрибуты
        if current_class == next_class and current_style == next_style:
            # Объединяем содержимое тегов
            # Проверяем, нужен ли пробел между абзацами
            if not (str(current_p.contents[-1]).strip().endswith((' ', '\n')) or not str(next_p.contents[0]).strip().startswith(' ')):
                current_p.append(' ')  # Добавляем пробел между содержимым, если его нет
            for child in list(next_p.children):
                current_p.append(child)
            # Удаляем next_p из дерева
            next_p.decompose()
            # Удаляем next_p из списка paragraphs
            del paragraphs[i + 1]
            # Не увеличиваем i, т.к. нужно проверить следующий тег
        else:
            # Переходим к следующей паре тегов
            i += 1

def process_epub_html(html_content, line_len=10, merge_before_splitting=False):
    """
    Обрабатывает HTML-контент EPUB-файла, разбивая длинные абзацы на меньшие.

    Функция ищет все теги <p> в HTML-контенте и разбивает длинные абзацы на меньшие,
    основываясь на количестве строк, полученных после разбиения по словам.
    Если абзац содержит более 4 строк после разбиения по line_len слов в строке,
    он разбивается на несколько абзацев.

    Разбиение происходит следующим образом:
    - Абзац разбивается на предложения с учётом пунктуации и специальных случаев.
    - Предложения накапливаются до тех пор, пока сумма строк от накопленных предложений
      не достигнет или не превысит порог (например, 4 строки).
    - Как только порог достигнут, накопленные предложения формируют новый абзац.

    Если параметр merge_before_splitting установлен в True, то перед обработкой все последовательные теги <p>,
    имеющие одинаковые значения атрибутов class и style (если атрибут отсутствует, считается, что его значение пустое),
    объединяются в один тег <p>. Атрибуты объединённого тега берутся из первого тега последовательности.

    :param html_content: Строка с HTML-контентом EPUB-файла.
    :param line_len: Целое число, определяющее количество слов в строке при разбиении (по умолчанию 10).
    :param merge_before_splitting: Признак того, что необходимо объединить абзацы в один перед дальнейшим разбиением (по умолчанию False).
    :return: Обновлённый HTML-контент с разбитыми абзацами.
    """
    # Парсим HTML с помощью BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    if merge_before_splitting:
        merge_adjacent_paragraphs(soup)

    # Ищем все теги <p>, так как в HTML абзацы всегда выделены именно этими тегами
    for paragraph in soup.find_all('p'):
        # Получаем текст абзаца с сохранением всех вложенных тегов
        paragraph_html = ''.join(str(child) for child in paragraph.children)
        
        # Разбиваем текст на строки по line_len токенов, чтобы вести их подсчет
        lines = split_paragraph_into_lines(paragraph_html, line_len)

        # Если в абзаце меньше или ровно 4 строки, то его не нужно разбивать
        if len(lines) <= 4:
            continue

        # Начинаем разбиение длинного абзаца через разбиение его на предложения
        # и подсчет количества строк в каждом предложении.
        # Основная идея алгоритма в том, что мы можем добавлять в новый абзац
        # очередное предложение до тех пор, пока суммарное количество строк от
        # всех накопленных предложений не станет равно или больше, чем нужно.
        # Как только такой момент настал - добавляем новый абзац к существующим
        # и начинаем копить предложения и считать строки заново - в уже новый абзац.
        new_paragraphs = []
        current_paragraph_sentences = []
        current_paragraph_line_count = 0

        # Разбиваем абзац на законченные предложения
        sentences = split_paragraph_into_sentences(paragraph_html)

        for sentence in sentences:
            # Добавляем предложение в текущий буфер абзаца
            current_paragraph_sentences.append(sentence)

            # Формируем текущий абзац из накопленных предложений
            current_paragraph_html = ' '.join(current_paragraph_sentences)

            # Разбиваем текущий абзац на строки для подсчета их количества
            current_lines = split_paragraph_into_lines(current_paragraph_html, line_len)
            current_line_count = len(current_lines)

            # Проверяем, достигло ли количество строк в текущем абзаце желаемого значения (например, 4)
            if current_line_count >= 4:
                # Добавляем текущий абзац в список новых абзацев
                new_paragraphs.append(current_paragraph_html)
                # Сбрасываем буферы для формирования следующего абзаца
                current_paragraph_sentences = []
                current_paragraph_line_count = 0

        # Если остались накопленные предложения, формируем из них последний абзац
        if current_paragraph_sentences:
            current_paragraph_html = ''.join(current_paragraph_sentences)
            new_paragraphs.append(current_paragraph_html)

        # Если был разрыв (абзац разбился на более мелкие), создаем новые теги <p> и добавляем их в HTML
        if len(new_paragraphs) > 1:
            previous_tag = paragraph
            for new_paragraph_html in new_paragraphs:
                new_tag = soup.new_tag("p")
                # Копируем атрибуты из оригинального тега <p> (начала абзаца), чтобы сохранить стиль разбиения
                for attr, value in paragraph.attrs.items():
                    new_tag[attr] = value
                # Добавляем HTML содержимое в новый тег
                new_tag.append(BeautifulSoup(new_paragraph_html, 'html.parser'))
                # Вставляем новый тег после предыдущего
                previous_tag.insert_after(new_tag)
                previous_tag = new_tag  # Обновляем предыдущий тег для следующей итерации
            paragraph.extract()  # Удаляем старый абзац
        else:
            # Если абзац не был разбит, обновляем его содержимое (на случай, если были изменения)
            paragraph.clear()
            paragraph.append(BeautifulSoup(new_paragraphs[0], 'html.parser'))

    # Возвращаем обновленный HTML
    return str(soup)

def process_epub(epub_path, line_len=10, merge_before_splitting=False, backuping=False):
    """
    Обрабатывает EPUB файл, находя все HTML файлы внутри него, применяет функцию форматирования
    к их содержимому и перезаписывает оригинальное содержимое отформатированной версией.

    Аргументы:
        epub_path (str): Путь к .epub файлу для обработки.
        line_len (int): Максимальное количество слов в строке абзацев.
        merge_before_splitting (bool): Признак того, что необходимо объединить абзацы в один перед дальнейшим разбиением.
        backuping (bool): Признак того, что необходимо создать резервную копию оригинального EPUB файла.

    Функция выполняет следующие шаги:
    - Извлекает содержимое EPUB файла во временную директорию.
    - Рекурсивно ищет все HTML файлы (.html или .htm) внутри извлеченного содержимого.
    - Читает содержимое каждого HTML файла и применяет к нему функцию `process_epub_html`.
    - Перезаписывает оригинальные HTML файлы отформатированным содержимым.
    - Пересобирает измененное содержимое обратно в EPUB файл, перезаписывая оригинальный файл.
    - Создает резервную копию оригинального EPUB файла с расширением '.bak' в той же директории, где лежит оригинал.
    """
    valid_extensions = {'html', 'htm', 'xhtml'}
    
    # Работаем с копией книги во временной директории
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Извлекаем содержимое epub файла во временную директорию
        with zipfile.ZipFile(epub_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)
        
        # Проходим по извлеченным файлам (рекурсивно)
        for root, dirs, files in os.walk(tmpdirname):
            for file in files:
                if file.lower().split('.')[-1] in valid_extensions:
                    file_path = os.path.join(root, file)

                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # Форматируем содержимое и перезаписываем старое отфрматированным
                    formatted_content = process_epub_html(content, line_len, merge_before_splitting)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(formatted_content)
        
        
        # Сначала делаем резервную копию оригинального файла, если был передан параметр
        if backuping:
            backup_epub_path = epub_path + '.bak'
            shutil.copy2(epub_path, backup_epub_path)
        
        # Создаем новый epub файл (перезаписываем оригинал)
        with zipfile.ZipFile(epub_path, 'w') as zip_ref:
            for foldername, subfolders, filenames in os.walk(tmpdirname):
                for filename in filenames:
                    filepath = os.path.join(foldername, filename)
                    # Относительный путь для сохранения в zip архиве
                    arcname = os.path.relpath(filepath, tmpdirname)
                    zip_ref.write(filepath, arcname)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Обработка EPUB файла и форматирование его HTML содержимого.')
    parser.add_argument('epub_path', help='Путь к EPUB файлу для обработки.')
    parser.add_argument('-l', '--line_len', type=int, default=10, help='Максимальное количество слов в строке абзацев.')
    parser.add_argument('-m', '--merge', action='store_true', help='Объединить все абзацы перед последующим разбиением.')
    parser.add_argument('-b', '--backup', action='store_true', help='Делать ли backup перед форматированием.')

    # Добавьте дополнительные аргументы здесь, если потребуется в будущем
    args = parser.parse_args()

    process_epub(args.epub_path, args.line_len, args.merge)
