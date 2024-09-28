import os
import logging

import chardet
# from nltk import tokenize

from calibre.customize import FileTypePlugin

DEBUG = False
DEBUGGER_PORT = 5555

VERSION = (1, 0, 21)

if DEBUG:
    from calibre.rpdb import set_trace
    set_trace(port=DEBUGGER_PORT)

logging.basicConfig(
    format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.DEBUG
)

class SplitParagraphsPlugin(FileTypePlugin):
    name = 'Split Paragraphs Plugin'
    description = 'Splits text into paragraphs of 4 lines.'
    supported_platforms = ['windows', 'osx', 'linux']
    author = 'Anton'
    version = VERSION
    file_types = {'txt', 'epub'}
    on_postprocess = True  # Run this plugin after conversion is complete

    def run(self, path_to_ebook):
        self.split_book(path_to_ebook)

        logging.info("[Split paragraphs plugin] done")

        return path_to_ebook

    @staticmethod
    def split_book(path_to_ebook):
        """
        Opens the e-book file located at path_to_ebook and
        splits its content into paragraphs not longer than 4 lines.

        :param path_to_ebook: string
        :return: path_to_ebook: string
        """

        logging.info("[Split paragraphs plugin] starting to split paragraphs...")

        try:
            ext = os.path.splitext(path_to_ebook)[1].lower()

            logging.info(f"[Split paragraphs plugin] file extension: {ext}")

            if ext not in ['.txt', '.epub']:
                raise ValueError(f"Unsupported file type: {ext}")

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



