# Для ребилда и публикации новой версии плагина в Calibre.
# Перед запуском нужно бампнуть версию в константе VERSION в файле плагина __init__.py
.PHONY: publish
publish:
	/Applications/calibre.app/Contents/MacOS/calibre-customize -b .

# Запускает Calibre в режиме позволяющем видеть отладочные логи в консоли.
# Чтобы отработал плагин нужно запустить конвертацию книги в интерфейсе Calibre.
.PHONY: run-debug
run-debug:
	/Applications/calibre.app/Contents/MacOS/calibre-debug -g

# (Пробовал настроить отладчик для подключения через IDE, но до конца не разобрался)
.PHONY: connect-debug
connect-debug:
	/Applications/calibre.app/Contents/MacOS/calibre-debug -c "from calibre.rpdb import cli; cli(port=5555)"

# Позволяет запустить плагин отдельно - без запуска Calibre.
run:
	cd ../.. && calibre-debug ./calibre_plugins/paragraphs_plugin/__init__.py
