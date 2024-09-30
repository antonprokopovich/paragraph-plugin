from calibre.utils.config import JSONConfig

# Создаем объект конфигурации для плагина
plugin_prefs = JSONConfig('plugins/SplitParagraphsPlugin')

# Значения по умолчанию
defaults = {
    'words_per_line': 10,             # Количество слов в строке по умолчанию
    'merge_before_splitting': False,  # Флаг объединения всех абзацев перед разделением
    'split_dialogs':          False,  # Флаг, нужно ли разбивать абзацы-релпики диалогов
}

plugin_prefs.defaults = defaults

# Функции для получения текущих значений настроек
def get_words_per_line():
    return plugin_prefs['words_per_line']

def get_merge_paragraphs():
    return plugin_prefs['merge_before_splitting']

def get_split_dialogs():
    return plugin_prefs['split_dialogs']
