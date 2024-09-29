import os
import logging

import chardet
# from nltk import tokenize

from calibre.customize import FileTypePlugin
from .config import get_words_per_line, plugin_prefs, get_merge_paragraphs
from .epub_split import process_epub

from PyQt5.Qt import QWidget, QVBoxLayout, QLabel, QSpinBox, QCheckBox

DEBUG = False
DEBUGGER_PORT = 5555

VERSION = (1, 0, 32)

if DEBUG:
    from calibre.rpdb import set_trace
    set_trace(port=DEBUGGER_PORT)

logging.basicConfig(
    format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG
)

class ConfigWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Добавляем текстовое описание
        label = QLabel('Количество слов в строке:')
        layout.addWidget(label)

        # Добавляем виджет выбора числа слов в строке
        self.words_per_line_spinbox = QSpinBox()
        self.words_per_line_spinbox.setMinimum(1)
        self.words_per_line_spinbox.setMaximum(100)
        layout.addWidget(self.words_per_line_spinbox)

        # Добавляем чекбокс для флага объединения абзацев
        self.merge_paragraphs_checkbox = QCheckBox('Объединить все абзацы перед разбиением')
        layout.addWidget(self.merge_paragraphs_checkbox)

        self.setLayout(layout)


class SplitParagraphsPlugin(FileTypePlugin):
    name = 'Split Paragraphs Plugin'
    description = 'Splits text into paragraphs of 4 lines.'
    supported_platforms = ['windows', 'osx', 'linux']
    author = 'Anton'
    version = VERSION
    file_types = {'txt', 'epub'}
    on_postprocess = True  # Run this plugin after conversion is complete

    def is_customizable(self):
        return True

    def config_widget(self):
        # Настройки для виджета конфигурации
        widget = ConfigWidget()
        widget.words_per_line_spinbox.setValue(get_words_per_line())
        widget.merge_paragraphs_checkbox.setChecked(get_merge_paragraphs())

        return widget

    def save_settings(self, config_widget):
        # Сохраняем новые значения настроек
        plugin_prefs['words_per_line'] = config_widget.words_per_line_spinbox.value()
        plugin_prefs['merge_before_splitting'] = config_widget.merge_paragraphs_checkbox.isChecked()

    def run(self, path_to_ebook):
        self.split_book(path_to_ebook)

        logging.info("[Split paragraphs plugin] done")

        return path_to_ebook
    
    @staticmethod
    def split_txt_book(path_to_ebook):
        encoding = detect_encoding(path_to_ebook)

        logging.info(f"[Split paragraphs plugin] detected encoding: {encoding}")

        # with open(path_to_ebook, 'r', encoding=encoding, errors='replace') as f:
        with open(path_to_ebook, 'r') as f:
            logging.info(f"[Split paragraphs plugin] opened file")

            content = f.read()

            new_content = split_paragraphs2(content)

            try:
                with open(path_to_ebook, 'w', encoding='utf-8') as file:
                    file.write(new_content)

                    logging.info(f"[Split paragraphs plugin] successfully written new contents")
            except Exception as e:
                logging.exception(f"[Split paragraphs plugin] error opening and writing file: {e}")

    @staticmethod
    def split_book(path_to_ebook):
        """
        Opens the e-book file located at path_to_ebook and
        splits its content into paragraphs not longer than 4 lines.

        :param path_to_ebook: string
        :return: path_to_ebook: string
        """

        words_per_line = get_words_per_line()
        merge_paragraphs = get_merge_paragraphs()

        logging.info(f"[Split paragraphs plugin] words per line: {words_per_line}, merge_paragraphs: {merge_paragraphs}")

        logging.info("[Split paragraphs plugin] starting to split paragraphs...")

        try:
            ext = os.path.splitext(path_to_ebook)[1].lower()

            logging.info(f"[Split paragraphs plugin] file extension: {ext}")

            if ext not in ['.txt', '.epub']:
                raise ValueError(f"Unsupported file type: {ext}")

            if ext == ".txt":
                self.split_txt_book(path_to_ebook)
            elif ext == ".epub":
                process_epub(path_to_ebook, words_per_line, merge_paragraphs)

        except Exception as e:
            logging.exception(f"[Split paragraphs plugin] An error occurred: {e}")


def split_paragraphs2(content):
    lines = content.split('.')
    # lines = tokenize.sent_tokenize(content)

    logging.info(f"[Split paragraphs plugin] lines: {lines}\n\n")
    new_content = []
    paragraph = []

    logging.info(f"[Split paragraphs plugin] will parse {len(lines)} lines")

    for line in lines:
        paragraph.append(line + ".")
        if len(paragraph) == 4:
            new_content.append(' '.join(paragraph) + '\n')
            paragraph = []

    if paragraph:
        new_content.append(' '.join(paragraph))

    new_content = '\n'.join(new_content)

    return new_content


def detect_encoding(path_to_ebook):
    with open(path_to_ebook, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

        if encoding is None:
            logging.warning(f"[Split paragraphs plugin] Unable to detect encoding, defaulting to 'utf-8'")
            encoding = 'utf-8'
        else:
            logging.info(f"[Split paragraphs plugin] Detected encoding: {encoding}")

        return encoding


if __name__ == "__main__":
    # path_to_book = "/Users/anton/sample3.txt"

    path_to_book = "/Users/anton/sample3.epub"

    SplitParagraphsPlugin.split_book(path_to_book)



