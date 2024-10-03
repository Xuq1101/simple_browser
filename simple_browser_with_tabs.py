import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QTabWidget, QWidget, QVBoxLayout, QLabel, QListWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

# Изменение платформы на "windows"
os.environ["QT_QPA_PLATFORM"] = "windows"  

class Browser(QMainWindow):
	def __init__(self):
		super().__init__()
		self.browser = QTabWidget()
		self.browser.setTabsClosable(True)
		self.browser.tabCloseRequested.connect(self.close_tab)
		self.setCentralWidget(self.browser)

		# Стиль для интерфейса
		self.setStyleSheet("""
			QMainWindow {
				background-color: #f2f2f2;
			}
			QToolBar {
				background-color: #ffffff;
				border-bottom: 1px solid #dcdcdc;
			}
			QTabWidget::pane {
				border-top: 2px solid #dcdcdc;
			}
			QTabBar::tab {
				background: #ffffff;
				border: 1px solid #dcdcdc;
				padding: 10px;
			}
			QTabBar::tab:selected {
				background: #f2f2f2;
				border-bottom: 2px solid #ffcc00;
			}
			QLineEdit {
				border: 1px solid #dcdcdc;
				padding: 5px;
				border-radius: 5px;
			}
		""")

		# Меню
		menubar = self.menuBar()
		file_menu = menubar.addMenu('Файл')
		bookmarks_menu = menubar.addMenu('Закладки')
		downloads_menu = menubar.addMenu('Загрузки')

		save_tab_action = QAction('Сохранить вкладку', self)
		save_tab_action.triggered.connect(self.save_tab)
		file_menu.addAction(save_tab_action)

		add_bookmark_action = QAction('Добавить закладку', self)
		add_bookmark_action.triggered.connect(self.add_bookmark)
		bookmarks_menu.addAction(add_bookmark_action)

		view_bookmarks_action = QAction('Просмотреть закладки', self)
		view_bookmarks_action.triggered.connect(self.view_bookmarks)
		bookmarks_menu.addAction(view_bookmarks_action)

		view_downloads_action = QAction('Просмотреть загрузки', self)
		view_downloads_action.triggered.connect(self.view_downloads)
		downloads_menu.addAction(view_downloads_action)

		self.bookmarks = []
		self.downloads = []

		# Панель инструментов
		navbar = QToolBar()
		self.addToolBar(navbar)

		back_btn = QAction('Назад', self)
		back_btn.triggered.connect(self.navigate_back)
		navbar.addAction(back_btn)

		forward_btn = QAction('Вперед', self)
		forward_btn.triggered.connect(self.navigate_forward)
		navbar.addAction(forward_btn)

		reload_btn = QAction('Обновить', self)
		reload_btn.triggered.connect(self.reload_page)
		navbar.addAction(reload_btn)

		home_btn = QAction('Домой', self)
		home_btn.triggered.connect(self.navigate_home)
		navbar.addAction(home_btn)

		new_tab_btn = QAction('+', self)
		new_tab_btn.triggered.connect(lambda: self.add_new_tab(QUrl("https://www.google.com/"), "+"))
		navbar.addAction(new_tab_btn)

		self.url_bar = QLineEdit()
		self.url_bar.returnPressed.connect(self.navigate_to_url)
		navbar.addWidget(self.url_bar)
		self.add_new_tab(QUrl("https://www.google.com/"), "Home")
	def save_tab(self):
		current_browser = self.browser.currentWidget()
		if current_browser:
			url = current_browser.url().toString()
			with open('saved_tabs.txt', 'a') as f:
				f.write(url + '\n')
			print(f"Вкладка сохранена: {url}")

	def add_new_tab(self, qurl=None, label="Blank"):
		if qurl is None:
			qurl = QUrl("https://www.google.com/")

		browser = QWebEngineView()
		browser.setUrl(qurl)
		i = self.browser.addTab(browser, label)
		self.browser.setCurrentIndex(i)

		browser.urlChanged.connect(lambda qurl, browser=browser: self.update_url(qurl, browser))
		browser.loadFinished.connect(lambda _, i=i, browser=browser: self.browser.setTabText(i, browser.page().title()))

	def close_tab(self, i):
		if self.browser.count() < 2:
			return
		self.browser.removeTab(i)

	def navigate_home(self):
		self.load_home_page()

	def load_home_page(self):
		home_html = '''
		<html>
		<head>
			<title>Домой</title>
			<style>
				body { font-family: Arial, sans-serif; }
				h1 { text-align: center; }
				ul { list-style-type: none; padding: 0; }
				li { margin: 10px 0; }
				a { text-decoration: none; color: #1a0dab; }
				a:hover { text-decoration: underline; }
			</style>
		</head>
		<body>
			<h1>Сохраненные Вкладки</h1>
			<ul>
		'''
		try:
			with open('saved_tabs.txt', 'r') as f:
				for line in f:
					url = line.strip()
					home_html += f'<li><a href="{url}" onclick="window.location.href=\'{url}\'">{url}</a></li>'
		except FileNotFoundError:
			home_html += "<li>Нет сохраненных вкладок</li>"
		home_html += "</ul></body></html>"

		home_page = QWebEngineView()
		home_page.setHtml(home_html)
		i = self.browser.addTab(home_page, "Домой")
		self.browser.setCurrentIndex(i)

	def navigate_to_url(self):
		url = self.url_bar.text()
		self.browser.currentWidget().setUrl(QUrl(url))

	def update_url(self, q, browser=None):
		if browser != self.browser.currentWidget():
			return
		self.url_bar.setText(q.toString())

	def navigate_back(self):
		self.browser.currentWidget().back()

	def navigate_forward(self):
		self.browser.currentWidget().forward()

	def reload_page(self):
		self.browser.currentWidget().reload()

	def view_bookmarks(self):
		bookmarks_window = BookmarksWindow(self)
		bookmarks_window.show()

	def add_bookmark(self):
		current_browser = self.browser.currentWidget()
		if current_browser:
			url = current_browser.url().toString()
			self.bookmarks.append(url)
			print(f"Закладка добавлена: {url}")

	def view_downloads(self):
		print("Просмотреть загрузки")  # Заполнитель для функции view_downloads
		# ... (реализуйте функциональность для просмотра загрузок)

class BookmarksWindow(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("Закладки")

		layout = QVBoxLayout()
		label = QLabel("Ваши Закладки:")
		layout.addWidget(label)

		# Добавьте QListWidget или другой элемент UI для отображения закладок
		# Пример с использованием метки (label) пока что:
		self.bookmarks_list = QListWidget()
		for bookmark in parent.bookmarks:
			self.bookmarks_list.addItem(bookmark)
		layout.addWidget(self.bookmarks_list)

		self.setLayout(layout)

app = QApplication(sys.argv)
QApplication.setApplicationName("Браузер с вкладками")
window = Browser()
app.exec_()