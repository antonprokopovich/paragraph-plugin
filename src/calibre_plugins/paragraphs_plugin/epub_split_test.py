import unittest

from epub_split import *

class TestTokenizeParagraph(unittest.TestCase):
    def test_spaces_and_nbsp(self):
        paragraph = 'Слово1\u00A0Слово2 Слово3'
        tokens = tokenize_paragraph(paragraph)
        expected = [
            Token('Слово1', True),
            Token('\u00A0', False),
            Token('Слово2', True),
            Token(' ', False),
            Token('Слово3', True),
        ]
        self.assertEqual(tokens, expected)

    def test_tags(self):
        paragraph = 'Текст с тегом<tag attr="value">и после</tag> тега.'
        tokens = tokenize_paragraph(paragraph)
        expected = [
            Token('Текст', True),
            Token(' ', False),
            Token('с', True),
            Token(' ', False),
            Token('тегом', True),
            Token('<tag attr="value">', False),
            Token('и', True),
            Token(' ', False),
            Token('после', True),
            Token('</tag>', False),
            Token(' ', False),
            Token('тега', True),
            Token('.', False),
        ]
        self.assertEqual(tokens, expected)

    def test_punctuation(self):
        paragraph = 'Он сказал: "Привет!" и зачем-то ушёл.'
        tokens = tokenize_paragraph(paragraph)
        expected = [
            Token('Он', True),
            Token(' ', False),
            Token('сказал', True),
            Token(':', False),
            Token(' ', False),
            Token('"', False),
            Token('Привет', True),
            Token('!', False),
            Token('"', False),
            Token(' ', False),
            Token('и', True),
            Token(' ', False),
            Token('зачем-то', True),
            Token(' ', False),
            Token('ушёл', True),
            Token('.', False),
        ]
        self.assertEqual(tokens, expected)

    def test_parentheses(self):
        paragraph = 'Это пример (с текстом) в скобках.'
        tokens = tokenize_paragraph(paragraph)
        expected = [
            Token('Это', True),
            Token(' ', False),
            Token('пример', True),
            Token(' ', False),
            Token('(', False),
            Token('с', True),
            Token(' ', False),
            Token('текстом', True),
            Token(')', False),
            Token(' ', False),
            Token('в', True),
            Token(' ', False),
            Token('скобках', True),
            Token('.', False),
        ]
        self.assertEqual(tokens, expected)

    def test_inside_tags(self):
        paragraph = '<tagName attribute="value">Содержимое тега</tagName>'
        tokens = tokenize_paragraph(paragraph)
        expected = [
            Token('<tagName attribute="value">', False),
            Token('Содержимое', True),
            Token(' ', False),
            Token('тега', True),
            Token('</tagName>', False),
        ]
        self.assertEqual(tokens, expected)

    def test_mixed_content(self):
        paragraph = 'Текст\u00A0с тегом <tag>и (символами), например: "пример".'
        tokens = tokenize_paragraph(paragraph)
        expected = [
            Token('Текст', True),
            Token('\u00A0', False),
            Token('с', True),
            Token(' ', False),
            Token('тегом', True),
            Token(' ', False),
            Token('<tag>', False),
            Token('и', True),
            Token(' ', False),
            Token('(', False),
            Token('символами', True),
            Token(')', False),
            Token(',', False),
            Token(' ', False),
            Token('например', True),
            Token(':', False),
            Token(' ', False),
            Token('"', False),
            Token('пример', True),
            Token('"', False),
            Token('.', False),
        ]
        self.assertEqual(tokens, expected)

class TestSplitParagraphIntoLines(unittest.TestCase):
    def test_simple_split(self):
        paragraph = 'Слово1 Слово2 Слово3 Слово4 Слово5'
        line_len = 2
        lines = split_paragraph_into_lines(paragraph, line_len)
        expected = [
            'Слово1 Слово2 ',
            'Слово3 Слово4 ',
            'Слово5'
        ]
        self.assertEqual(lines, expected)

    def test_with_punctuation(self):
        paragraph = 'Он сказал: "Привет!" И ушёл.'
        line_len = 3
        lines = split_paragraph_into_lines(paragraph, line_len)
        expected = [
            'Он сказал: "Привет!" ',
            'И ушёл.'
        ]
        self.assertEqual(lines, expected)

    def test_with_hyphenated_words(self):
        paragraph = 'Это нью-йоркский музей и зачем-то написанные слова.'
        line_len = 2
        lines = split_paragraph_into_lines(paragraph, line_len)
        expected = [
            'Это нью-йоркский ',
            'музей и ',
            'зачем-то написанные ',
            'слова.'
        ]
        self.assertEqual(lines, expected)

    def test_with_tags_and_spaces(self):
        paragraph = 'Текст с тегом<tag>и символами.'
        line_len = 2
        lines = split_paragraph_into_lines(paragraph, line_len)
        expected = [
            'Текст с ',
            'тегом<tag>и ',
            'символами.'
        ]
        self.assertEqual(lines, expected)

    def test_line_len_one(self):
        paragraph = 'Одно слово. Второе слово.'
        line_len = 1
        lines = split_paragraph_into_lines(paragraph, line_len)
        expected = [
            'Одно ',
            'слово. ',
            'Второе ',
            'слово.'
        ]
        self.assertEqual(lines, expected)

    def test_no_words(self):
        paragraph = '!!! *** ???'
        line_len = 2
        lines = split_paragraph_into_lines(paragraph, line_len)
        expected = [
            '!!! *** ???'
        ]
        self.assertEqual(lines, expected)

    def test_empty_paragraph(self):
        paragraph = ''
        line_len = 3
        lines = split_paragraph_into_lines(paragraph, line_len)
        expected = []
        self.assertEqual(lines, expected)

    def test_line_len_zero(self):
        paragraph = 'Это тест с line_len = 0.'
        line_len = 0
        with self.assertRaises(ValueError):
            lines = split_paragraph_into_lines(paragraph, line_len)

    def test_non_integer_line_len(self):
        paragraph = 'Тест с нецелым значением line_len.'
        line_len = 2.5
        with self.assertRaises(ValueError):
            lines = split_paragraph_into_lines(paragraph, line_len)

    def test_mixed_language(self):
        paragraph = 'This is a test смешанного текста with multiple languages.'
        line_len = 4
        lines = split_paragraph_into_lines(paragraph, line_len)
        expected = [
            'This is a test ',
            'смешанного текста with multiple ',
            'languages.'
        ]
        self.assertEqual(lines, expected)

    def test_paragraph_with_numbers(self):
        paragraph = 'У него было 10 яблок и 20 груш.'
        line_len = 3
        lines = split_paragraph_into_lines(paragraph, line_len)
        expected = [
            'У него было ',
            '10 яблок и ',
            '20 груш.'
        ]
        self.assertEqual(lines, expected)

    def test_paragraph_with_long_word(self):
        paragraph = 'Это слово-сверхдлинное-и-никогда-не-оканчивающееся'
        line_len = 1
        lines = split_paragraph_into_lines(paragraph, line_len)
        expected = [
            'Это ',
            'слово-сверхдлинное-и-никогда-не-оканчивающееся'
        ]
        self.assertEqual(lines, expected)

    def test_paragraph_with_multiple_spaces(self):
        paragraph = 'Это  текст   с    множественными     пробелами.'
        line_len = 3
        lines = split_paragraph_into_lines(paragraph, line_len)
        expected = [
            'Это  текст   с    ',
            'множественными     пробелами.'
        ]
        self.assertEqual(lines, expected)

    def test_paragraph_with_newlines(self):
        paragraph = 'Первая строка.\nВторая строка.\n\nТретья строка.'
        line_len = 2
        lines = split_paragraph_into_lines(paragraph, line_len)
        expected = [
            'Первая строка.\n',
            'Вторая строка.\n\n',
            'Третья строка.'
        ]
        self.assertEqual(lines, expected)

    def test_paragraph_with_tabs(self):
        paragraph = 'Слово1\tСлово2\t\tСлово3'
        line_len = 2
        lines = split_paragraph_into_lines(paragraph, line_len)
        expected = [
            'Слово1\tСлово2\t\t',
            'Слово3'
        ]
        self.assertEqual(lines, expected)

    def test_paragraph_with_nbsp(self):
        paragraph = 'Слово1\u00A0Слово2\u00A0\u00A0Слово3'
        line_len = 2
        lines = split_paragraph_into_lines(paragraph, line_len)
        expected = [
            'Слово1\u00A0Слово2\u00A0\u00A0',
            'Слово3'
        ]
        self.assertEqual(lines, expected)
    
    def test_paragraph_with_tags(self):
        paragraph = 'Текст с <b> жирным</b> тегом и <i> курсивом</i>.'
        line_len = 3
        lines = split_paragraph_into_lines(paragraph, line_len)
        expected = [
            'Текст с <b> жирным</b> ',
            'тегом и <i> курсивом</i>.',
        ]
        self.assertEqual(lines, expected)

    def test_paragraph_with_nested_tags(self):
        paragraph = 'Начало <div> <p> Параграф с <span> вложенными </span> тегами</p></div> Конец.'
        line_len = 2
        lines = split_paragraph_into_lines(paragraph, line_len)
        expected = [
            'Начало <div> <p> Параграф ',
            'с <span> вложенными </span> ',
            'тегами</p></div> Конец.'
        ]
        self.assertEqual(lines, expected)

    def test_paragraph_with_tags_without_spaces(self):
        paragraph = 'Текст с<tag>тегом</tag>внутри слова.'
        line_len = 2
        lines = split_paragraph_into_lines(paragraph, line_len)
        expected = [
            'Текст с<tag>',
            'тегом</tag>внутри ',
            'слова.'
        ]
        self.assertEqual(lines, expected)

    def test_paragraph_with_attributes_in_tags(self):
        paragraph = '<p class="text">Это пример с тегами</p> и атрибутами.'
        line_len = 3
        lines = split_paragraph_into_lines(paragraph, line_len)
        expected = [
            '<p class="text">Это пример с ',
            'тегами</p> и атрибутами.'
        ]
        self.assertEqual(lines, expected)

class TestSplitParagraphIntoSentences(unittest.TestCase):
    def test_simple_sentences(self):
        paragraph = 'Первое предложение. Второе предложение! Третье предложение?'
        sentences = split_paragraph_into_sentences(paragraph)
        expected = [
            'Первое предложение.',
            'Второе предложение!',
            'Третье предложение?'
        ]
        self.assertEqual(sentences, expected)

    def test_abbreviations(self):
        paragraph = 'Мы посетили ул. Ленина и г. Москву. Это было интересно.'
        sentences = split_paragraph_into_sentences(paragraph)
        expected = [
            'Мы посетили ул. Ленина и г. Москву.',
            'Это было интересно.'
        ]
        self.assertEqual(sentences, expected)

    def test_sentences_with_numbers(self):
        paragraph = 'Цена товара составляет 15.99 рублей. Это выгодная цена!'
        sentences = split_paragraph_into_sentences(paragraph)
        expected = [
            'Цена товара составляет 15.99 рублей.',
            'Это выгодная цена!'
        ]
        self.assertEqual(sentences, expected)

    def test_tags(self):
        paragraph = 'Это текст с тегом <a href="http://example.com">ссылка</a>. Следующее предложение.'
        sentences = split_paragraph_into_sentences(paragraph)
        expected = [
            'Это текст с тегом <a href="http://example.com">ссылка</a>.',
            'Следующее предложение.'
        ]
        self.assertEqual(sentences, expected)

    def test_multiple_punctuation(self):
        paragraph = 'Что это было?! Никто не знает... Может, узнаем позже.'
        sentences = split_paragraph_into_sentences(paragraph)
        expected = [
            'Что это было?!',
            'Никто не знает...',
            'Может, узнаем позже.'
        ]
        self.assertEqual(sentences, expected)

    def test_inside_unclosed_tag(self):
        paragraph = 'Текст с <b>незакрытым тегом. Он продолжается</b>. А теперь новое предложение.'
        sentences = split_paragraph_into_sentences(paragraph)
        expected = [
            'Текст с <b>незакрытым тегом. Он продолжается</b>.',
            'А теперь новое предложение.'
        ]
        self.assertEqual(sentences, expected)

    def test_end_with_punctuation(self):
        paragraph = 'Это предложение заканчивается! И это тоже.'
        sentences = split_paragraph_into_sentences(paragraph)
        expected = [
            'Это предложение заканчивается!',
            'И это тоже.'
        ]
        self.assertEqual(sentences, expected)

class TestIsAbbreviation(unittest.TestCase):
    def test_unknown_abbreviations(self):
        text = 'Это сокращение хз. не должно быть распознано.'
        position = text.find('.')
        result = is_abbreviation(text, position)
        self.assertFalse(result)

    def test_end_of_sentence(self):
        text = 'Это конец предложения.'
        position = text.find('.', 0)
        result = is_abbreviation(text, position)
        self.assertFalse(result)

    def test_middle_of_word(self):
        text = 'Это некоторая строка.'
        position = text.find('.', 5)
        if position != -1:
            result = is_abbreviation(text, position)
            self.assertFalse(result)

    def test_multiple_abbreviations(self):
        text = 'Список сокращений: г., ул., д., и т.д.'
        positions = [text.find('г.') + 1, text.find('ул.') + 2, text.find('д.') + 1, text.find('т.д.') + 3]
        expected = [True, True, True, False]
        results = [is_abbreviation(text, pos) for pos in positions]
        self.assertEqual(results, expected)

    def test_number_with_dot(self):
        text = 'Число 3.14 является приближением числа π.'
        position = text.find('.')
        result = is_abbreviation(text, position)
        self.assertFalse(result)

    def test_abbreviation_at_start(self):
        text = 'Dr. Watson был помощником Sherlock Holmes.'
        position = text.find('.')
        result = is_abbreviation(text, position)
        self.assertTrue(result)

    def test_abbreviation_with_spaces(self):
        text = 'Мы были в г. Санкт-Петербург.'
        position = text.find('г.') + 1
        result = is_abbreviation(text, position)
        self.assertTrue(result)

    def test_punctuation_after_abbreviation(self):
        text = 'Он сказал г. Иванову: "Здравствуйте!"'
        position = text.find('г.') + 1
        result = is_abbreviation(text, position)
        self.assertTrue(result)

    def test_dot_not_abbreviation(self):
        text = 'У него было яблоко. Он его съел.'
        position = text.find('.', 0)
        result = is_abbreviation(text, position)
        self.assertFalse(result)

    def test_empty_text(self):
        text = ''
        position = 0
        result = is_abbreviation(text, position)
        self.assertFalse(result)

    def test_non_dot_punctuation(self):
        text = 'Восклицание! Вопрос?'
        positions = [text.find('!'), text.find('?')]
        results = [is_abbreviation(text, pos) for pos in positions]
        self.assertEqual(results, [False, False])

    def test_abbreviation_with_uppercase(self):
        text = 'Мы встретили Prof. Smith на конференции.'
        position = text.find('.')
        result = is_abbreviation(text, position)
        self.assertTrue(result)
    
    def test_conditional_abbreviation_with_uppercase_next_word(self):
        text = 'Мы изучали математику, физику и т.д. Теперь перейдем к другим предметам.'
        position = text.find('т.д.') + 3  # Позиция точки в "т.д."
        result = is_abbreviation(text, position)
        self.assertFalse(result)  # Должно быть False, чтобы предложение могло быть разделено

    def test_conditional_abbreviation_with_lowercase_next_word(self):
        text = 'Мы изучали математику, физику и т.д. затем пошли домой.'
        position = text.find('т.д.') + 3
        result = is_abbreviation(text, position)
        self.assertTrue(result)  # Должно быть True, не разделяем предложение

    def test_unconditional_abbreviation_with_uppercase_next_word(self):
        text = 'Мы посетили г. Москву. Это было интересно.'
        position = text.find('г.') + 1
        result = is_abbreviation(text, position)
        self.assertTrue(result)  # Всегда True для безусловных сокращений

    def test_conditional_abbreviation_at_end(self):
        text = 'Компания была зарегистрирована как ABC Ltd.'
        position = text.find('Ltd.') + 3
        result = is_abbreviation(text, position)
        self.assertFalse(result)  # Новое предложение может начинаться после

    def test_conditional_abbreviation_with_punctuation(self):
        text = 'Он сказал: "Достаточно и т.п.! Теперь переходим дальше."'
        position = text.find('т.п.') + 3
        result = is_abbreviation(text, position)
        self.assertFalse(result)  # Следующее слово "Теперь" с заглавной буквы
    
    def test_initials_with_spaces(self):
        text = 'Известный поэт А. С. Пушкин.'
        position = text.find('А. С.')
        result = is_abbreviation(text, position + 4)  # Индекс последней точки в инициале
        self.assertTrue(result)

    def test_initials_without_spaces(self):
        text = 'Известный поэт А.С. Пушкин.'
        position = text.find('А.С.')
        result = is_abbreviation(text, position + 3)  # Индекс последней точки в инициале
        self.assertTrue(result)

class TestProcessEpubHtml(unittest.TestCase):
    def test_short_paragraph(self):
        html_content = '<p>Это короткий абзац с небольшим количеством слов.</p>'
        expected_output = '<p>Это короткий абзац с небольшим количеством слов.</p>'
        result = process_epub_html(html_content, line_len=5)
        self.assertEqual(result.strip(), expected_output)

    def test_long_paragraph_split(self):
        html_content = '<p>Это очень длинный абзац, который содержит много предложений. Первое предложение. Второе предложение, которое немного длиннее первого. Третье предложение с некоторым количеством слов. Четвёртое предложение, которое, возможно, превысит лимит строк. Пятое и последнее предложение в этом абзаце.</p>'
        result = process_epub_html(html_content, line_len=5)
        # Проверяем, что результат содержит несколько абзацев <p>
        soup = BeautifulSoup(result, 'html.parser')
        paragraphs = soup.find_all('p')
        self.assertTrue(len(paragraphs) > 1)
        # Дополнительные проверки можно добавить по необходимости

    def test_paragraph_with_tags(self):
        html_content = '<p>Текст с <b>жирным</b> и <i>курсивом</i>. Это предложение должно быть вместе с предыдущим.</p>'
        result = process_epub_html(html_content, line_len=3)
        soup = BeautifulSoup(result, 'html.parser')
        paragraphs = soup.find_all('p')
        # Проверяем, что тег <b> и <i> сохранены
        for p in paragraphs:
            self.assertTrue(p.find('b') or p.find('i'))

    def test_paragraph_with_attributes(self):
        html_content = '<p class="text">Абзац с атрибутом класса. Длинный текст, который должен быть разбит на несколько абзацев.</p>'
        result = process_epub_html(html_content, line_len=5)
        soup = BeautifulSoup(result, 'html.parser')
        paragraphs = soup.find_all('p')
        # Проверяем, что атрибут класса сохранён во всех новых абзацах
        for p in paragraphs:
            self.assertEqual(p.get('class'), ['text'])

    def test_no_paragraphs(self):
        html_content = '<div>Текст без тегов абзацев.</div>'
        expected_output = '<div>Текст без тегов абзацев.</div>'
        result = process_epub_html(html_content, line_len=5)
        self.assertEqual(result.strip(), expected_output)

class TestMergeAdjacentParagraphs(unittest.TestCase):
    def test_merge_same_attributes(self):
        html_content = '''
        <p class="text">Абзац 1.</p>
        <p class="text">Абзац 2.</p>
        <p class="note">Абзац 3.</p>
        <p class="text">Абзац 4.</p>
        '''
        soup = BeautifulSoup(html_content, 'html.parser')
        merge_adjacent_paragraphs(soup)
        paragraphs = soup.find_all('p')
        # Ожидаем 3 абзаца после объединения
        self.assertEqual(len(paragraphs), 3)
        # Проверяем содержимое первого абзаца
        first_paragraph_text = paragraphs[0].get_text(separator=' ').strip()
        self.assertEqual(first_paragraph_text, 'Абзац 1. Абзац 2.')
        # Проверяем, что второй абзац имеет класс "note"
        self.assertEqual(paragraphs[1].get('class', []), ['note'])
        # Проверяем содержимое третьего абзаца
        third_paragraph_text = paragraphs[2].get_text(separator=' ').strip()
        self.assertEqual(third_paragraph_text, 'Абзац 4.')

    def test_no_merge_different_attributes(self):
        html_content = '''
        <p class="text" style="color: red;">Абзац 1.</p>
        <p class="text" style="color: blue;">Абзац 2.</p>
        '''
        soup = BeautifulSoup(html_content, 'html.parser')
        merge_adjacent_paragraphs(soup)
        paragraphs = soup.find_all('p')
        # Ожидаем 2 абзаца, так как атрибуты style отличаются
        self.assertEqual(len(paragraphs), 2)

    def test_merge_missing_attributes(self):
        html_content = '''
        <p>Абзац 1.</p>
        <p>Абзац 2.</p>
        <p class="text">Абзац 3.</p>
        <p class="text">Абзац 4.</p>
        '''
        soup = BeautifulSoup(html_content, 'html.parser')
        merge_adjacent_paragraphs(soup)
        paragraphs = soup.find_all('p')
        # Ожидаем 3 абзаца после объединения
        self.assertEqual(len(paragraphs), 2)
        # Проверяем содержимое первого абзаца
        first_paragraph_text = paragraphs[0].get_text(separator=' ').strip()
        self.assertEqual(first_paragraph_text, 'Абзац 1. Абзац 2.')
        # Проверяем содержимое второго абзаца
        second_paragraph_text = paragraphs[1].get_text(separator=' ').strip()
        self.assertEqual(second_paragraph_text, 'Абзац 3. Абзац 4.')

    def test_merge_with_missing_class(self):
        html_content = '''
        <p style="font-weight: bold;">Абзац 1.</p>
        <p style="font-weight: bold;">Абзац 2.</p>
        '''
        soup = BeautifulSoup(html_content, 'html.parser')
        merge_adjacent_paragraphs(soup)
        paragraphs = soup.find_all('p')
        # Ожидаем 1 абзац после объединения
        self.assertEqual(len(paragraphs), 1)
        # Проверяем содержимое абзаца
        paragraph_text = paragraphs[0].get_text(separator=' ').strip()
        self.assertEqual(paragraph_text, 'Абзац 1. Абзац 2.')

    def test_no_merge_different_levels(self):
        html_content = '''
        <div>
            <p class="text">Абзац 1.</p>
        </div>
        <p class="text">Абзац 2.</p>
        '''
        soup = BeautifulSoup(html_content, 'html.parser')
        merge_adjacent_paragraphs(soup)
        paragraphs = soup.find_all('p')
        # Ожидаем 2 абзаца, так как они на разных уровнях
        self.assertEqual(len(paragraphs), 2)

if __name__ == '__main__':
    unittest.main()
