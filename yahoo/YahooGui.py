import datetime
import pandas as pd
import PyQt5

import  yahoo.YahooFinance as yp
import sys
import traceback
import time
import os
# require pip install PyQtWebEngine
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
#from PyQt5.QtWebKit import *
from PyQt5.QtWebEngineWidgets   import *
from PyQt5 import *
timeout = pd.Timedelta("5 seconds")
open_time = "9:30"
close_time = "16:00"

class WorkerSignals(QObject):
    finished = PyQt5.QtCore.pyqtSignal(object)
    error = PyQt5.QtCore.pyqtSignal(tuple)
    result = PyQt5.QtCore.pyqtSignal(object, object)

class Worker(QRunnable):
    def __init__(self, symbol, parent, proxies):
        super(Worker, self).__init__()
        self.symbol = symbol
        self.parent = parent
        self.proxies = proxies

        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            if self.symbol not in self.parent.yp_cache:
                #print("Checking cache ... ")
                self.parent.yp_cache[self.symbol] = yp.YahooFinance(proxies=self.proxies, verify=False)
            yahoo = self.parent.yp_cache [self.symbol]
            yahoo.get_details(self.symbol, timedelta=timeout)

            bid = yahoo.get_bid( self.symbol)
            ask = yahoo.get_ask( self.symbol)
            last = yahoo.get_last_price(self.symbol)
            qtime = yahoo.get_query_time()


            open = yahoo.get_open_price(self.symbol)
            prev_close = yahoo.get_prev_close(self.symbol)
            close_status  = yahoo.get_close_status(self.symbol)
            change = (last - prev_close)/prev_close
            change = str(int(change * 10000)/100) + "%"
            result = { 'bid': bid, 'ask': ask, 'last': last, 'open': open, 'close': prev_close, 'change': change, 'close_status': close_status, 'time': qtime}
            self.signals.result.emit (self.symbol, result)
        except:

            print("error for ", self.symbol)
            traceback.print_exc()
            exectype, value = sys.exc_info()[:2]
            self.signals.error.emit( (exectype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit (self.symbol)


class Second(QDialog):#QMainWindow QDialog
    def __init__(self, parent=None):
        super(Second, self).__init__(parent)
        layout = QVBoxLayout(self)
        layout.setSizeConstraint(QLayout.SetNoConstraint)

        web = QWebEngineView(self)
        self.webSettings = web.settings()
        self.webSettings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.webSettings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        layout.addWidget(web)
        #layout.setRowStretch(2, 2)
        layout.setSizeConstraint(QLayout.SetNoConstraint)
        web.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.resize(1024, 750);

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        web.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.webSettings.setAttribute(QWebEngineSettings.ShowScrollBars, True)
        #web.page().mainFrame().setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAsNeeded)
        #web.setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAsNeeded)
        #web.addUrl("http://google.com")
        #self.addWidget(web)
        #layout.setContentsMargins(0,0,0,0)

        self.setLayout(layout)
        web.load(QUrl("http://google.com"))


#self.ui.lineEdit.setText("")
class App(QWidget):
    def __init__(self, config_file, proxies=None):
        super(App, self).__init__()
        config_dir = os.path.dirname(config_file)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)


        self.config_file = config_file
        self.df_config = self.read_config()

        self.proxies = proxies
        self.title = "Yahoo Maket Prices " + time.ctime(os.path.getmtime(__file__))
        self.left = 100
        self.top = 200
        self.width = 400
        self.height = 150
        self.yp_cache = {}
        self.threadpool = QThreadPool()
        self.pending_req = {}
        self.header_map = {}


        self.initUI()
        self.setMinimumSize(1000, 300)
        #// setWindowIcon(QIcon("png"))
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()



    def read_config(self):
        self.symbols = []
        if os.path.exists(self.config_file):
            df =  pd.read_csv(self.config_file, index_col=['name'])
            if 'symbols' in df.index:
                self.symbols = df.loc["symbols"].value.split(",")
            return df
        df = pd.DataFrame(columns=['name', "value"]).set_index("name")
        return df
    def save_config(self):
        print("Saving config\n", self.df_config)
        print("Saving config\n", self.symbols)
        self.df_config.loc["symbols", "value"] = ",".join(self.symbols)
        self.df_config.to_csv(self.config_file, index=True)

    def is_regular_trading_hours(self):
        now = pd.to_datetime(datetime.datetime.now())
        ot = pd.to_datetime(open_time)
        ct = pd.to_datetime(close_time)
        if pd.to_datetime(now).date() in df_holiday.index:
            return False

        weekday =  now.date().weekday()
        if weekday in [ 5, 6]:
            #print("week end")
            return False
        if now >= ot and now <= ct:
            return True

        return False

    def get_sleep_time(self):
        if self.is_regular_trading_hours():
            return  pd.Timedelta("5 seconds")

        now = pd.to_datetime(datetime.datetime.now())
        ot = pd.to_datetime(open_time)
        delta = ot - now
        if delta >=pd.Timedelta("0 seconds") and delta < pd.Timedelta("15 minutes"):
            return delta
        return pd.Timedelta("15 minutes")

    def recurring_timer(self):
        global timeout
        try:
            timeout = self.get_sleep_time()
            self.check_for_expired()
        except:
            traceback.print_exc()


    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.layout = QVBoxLayout(self)

        self.setLayout(self.layout)
        self.symbol_edit = QLineEdit("", self)
        hlayout= QHBoxLayout(self)
        hlayout.stretch(True)
        hlayout.addWidget(self.symbol_edit)
        self.add_symbol_button = QPushButton("Add Symbol", self)
        self.add_symbol_button.clicked.connect(self.on_add_symbol)
        hlayout.addWidget(self.add_symbol_button)
        self.layout.addLayout(hlayout)

        model = QStandardItemModel()
        self.headers = ["Source", "Symbol", "Prev Close", "OPEN", "BidQty", "Bid", "SynP", "Ask", "AskQty", "change", "Status", "timestamp", "age"]
        model.setHorizontalHeaderLabels(self.headers)
        table = QTableView()
        table.setModel(model)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)

        table.doubleClicked.connect(self.on_table_double_clcked)
        #table.clicked()
        table.pressed.connect(self.on_contextMenuEvent)
        self.table = table
        model.setColumnCount(len(self.headers))
        self.layout.addWidget(table)
        self.model= model


        print(self.df_config)

        if len(self.symbols) == 0:
            model.appendRow(self.get_details("OEF"))
        else:

            for s in self.symbols:
                model.appendRow(self.get_details(s))

       # table.verticalHeader().setDefaultSelectionSize(20)
        table.verticalHeader().setVisible(False)
        [table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch) for i in range(0, len(self.headers))]

        #self.browser = QWebEngineView(self)
        #self.browser.resize(2000, 800)
        #self.layout.addWidget(self.browser)
        #self.browser.load(QUrl("http://google.com"))
        self.refresh_button = QPushButton("Refresh", self)
        self.refresh_button.setToolTip("Refresh Market data")
        self.layout.addWidget(self.refresh_button)
        self.refresh_button.clicked.connect(self.on_click_refresh)


        self.show()

    def mousePressEvent(self, event):
        super.mousePressedEvent(event)
        print("here")
    def on_contextMenuEvent(self, index, **kwargs):
        self.menu = QMenu(self)
        print(kwargs)
        removeEntry = QAction('Delete', self)
        upEntry = QAction('Up', self)
        downEntry = QAction('Down', self)
        #index  = self.table.selectedIndexes()
        #if event.button() == Qt.RightButton:
        removeEntry.triggered.connect(lambda event: self.remove_row(event, index))
        upEntry.triggered.connect(lambda event: self.move_row_up(event, index))
        downEntry.triggered.connect(lambda event: self.move_row_down(event, index))
        self.menu.addAction(removeEntry)
        self.menu.addAction(upEntry)
        self.menu.addAction(downEntry)
        # add other required actions
        self.menu.popup(QCursor.pos())
        self.table.clearSelection()

    def remove_row(self, event, index):
        print("here", event, index.row())
        try:
            idx = int(index.row())
            del self.symbols[idx:idx+1]
            self.save_config()
        except:
            traceback.print_exc()

        try:
            #if event.button() == Qt.RightButton:
            print(self.model.removeRow(index.row()))
            self.table.clearSelection()
        except:
            traceback.print_exc()

    def move_row_up(self, event, index):
        print("here", event, index.row())
        try:
            idx = int(index.row())
            if idx == 0:
                return
        except:
            traceback.print_exc()
            return

        try:
            #if event.button() == Qt.RightButton:
            idx_from = self.model.index(idx, 0)
            idx_to = self.model.index(idx-1, 0)
            #self.model.moveRow(idx_from, idx_from.row(), idx_to, 1)
            row = self.model.takeRow(idx_from.row())
            #idx_to.parent.appendRow(row)
            self.model.insertRow(int(idx_to.row()), row)
            #print(self.model.removeRow(index.row()))
            #self.table.clearSelection()
            tmp = self.symbols[idx_from.row()]
            self.symbols[idx_from.row()] = self.symbols[idx_to.row()]
            self.symbols[idx_to.row()] = tmp
            self.save_config()
        except:
            traceback.print_exc()

    def move_row_down(self, event, index):
        print("here", event, index.row())
        try:
            idx = int(index.row())
            if idx == len(self.symbols)-1:
                return
        except:
            traceback.print_exc()
            return

        try:
            #if event.button() == Qt.RightButton:
            idx_from = self.model.index(idx, 0)
            idx_to = self.model.index(idx+1, 0)


            #self.model.moveRow(idx_from, idx_from.row(), idx_to, 1)
            row = self.model.takeRow(idx_to.row())
            #idx_to.parent.appendRow(row)
            self.model.insertRow(int(idx_from.row()), row)
            #print(self.model.removeRow(index.row()))
            #self.table.clearSelection()

            tmp = self.symbols[idx_from.row()]
            self.symbols[idx_from.row()] = self.symbols[idx_to.row()]
            self.symbols[idx_to.row()] = tmp
            self.save_config()
        except:
            traceback.print_exc()

    def check_for_expired(self):
        #print("check for expired ", self.model.rowCount())
        if self.isMinimized():
            print("not visible")
            return
        if not self.isVisible() or self.isHidden():
            print("not visible -- hidden", self.isVisible(), self.isHidden())
            return

        #else:
        #    print("huh visible")

        for x in range(0, self.model.rowCount()):
            index = self.model.index(x, self.get_row_index("Symbol"))
            symbol = index.data()
            #print("checking for ", symbol)
            timestamp = pd.to_datetime(self.model.index(x, self.get_row_index("timestamp")).data())
            now = pd.to_datetime(datetime.datetime.now())
            if timestamp is not None:
                delta  = (now - timestamp)
                if delta < timeout:
                    #print("too young", self.delta_to_minutes(delta), symbol)
                    index = self.model.index(x, self.get_row_index("age"))
                    self.model.setData(index, self.delta_to_minutes(delta))
                    continue
            if symbol in self.pending_req:
                continue

            index = self.model.index(x, self.get_row_index("Source"))
            self.model.setData(index, QBrush(Qt.gray), Qt.BackgroundRole)
            self.pending_req[symbol] = symbol
            if self.table.isRowHidden(x):
                print("row ", x, "hidden")
                continue

            try:
                worker = Worker(symbol, self, self.proxies)
                worker.signals.result.connect(self.on_result)
                worker.signals.finished.connect(self.on_complete)

                self.threadpool.start(worker)
            except:
                traceback.print_exc()
                del self.pending_req[symbol]


    def on_mouse_pressed(self, **kwargs):
        try :
            print("on_mouse_pressed", kwargs)
        except:
            traceback.print_exc()

    def on_table_double_clcked(self, index):
        #print("double clicked", index.row(), index.column())
        try :
            browser = Second(self)
            #browser = QWebEngineView(self)
            #self.browser.load(QUrl("http://google.com"))
            browser.show()
            print("double clicked", index.row(), index.column())
        except:
            traceback.print_exc()

    @pyqtSlot()
    def on_click_refresh(self):
        pass

    @pyqtSlot()
    def on_add_symbol(self):
        tokens = self.symbol_edit.text().split(",")
        try:


            for value in tokens:
                value = value.strip()
                if len(value)==0:
                    continue
                found = False
                for x in range(0, self.model.rowCount()):
                    index = self.model.index(x, 1)
                    symbol = index.data()
                    if symbol ==value:
                        print(value, "already in the list")
                        found = True
                        break
                if not found:
                    self.model.appendRow(self.get_details(value))
                    self.symbols.append(value)

            self.save_config()

        except:
            traceback.print_exc()

    def delta_to_minutes(self, delta):
        min = delta.total_seconds()/60
        min = int(min*100)/100  # round out
        if min <= 0:
            return ""
        return str(min) + " minutes"


    def get_row_index(self, fieldname):
        headers = [self.model.headerData(x, Qt.Horizontal) for x in range(0, self.model.columnCount())]
        if fieldname not in self.header_map:
            i = 0
            for x in headers:
                self.header_map[x] = i
                i = i +1
            if fieldname not in self.header_map:
                return -1
        return self.header_map[fieldname]

    def set_color(self, index, color):
        self.model.setData(index, QBrush(color), Qt.BackgroundRole)
    def on_result(self, symbol, result):
        try:
            #print("on_result", symbol)
            headers = [self.model.headerData(x, Qt.Horizontal) for x in range(0, self.model.columnCount())]
            now = pd.to_datetime(datetime.datetime.now())
            mapping = {
                "Status": lambda x:"OPEN" if not x['close_status'] else "CLOSED",
                "Source": lambda x: "YAHOO-THD",
                'Prev Close': lambda  x:x['close'],
                "Symbol": lambda  x: symbol,
                "age": lambda  x: self.delta_to_minutes(now - pd.to_datetime(x['time'])),
                'OPEN': lambda x: x['open'],
                'BidQty': lambda x: x['bid'][1],
                'Bid': lambda x: x['bid'][0],
                'SynP': lambda x: x['last'],
                'AskQty': lambda x: x['ask'][1],
                'Ask': lambda x: x['ask'][0],
                'change': lambda x: x['change'],
                'timestamp': lambda x: x['time'],
            }
            data =  [ mapping[x](result) if x in mapping else "" for x in headers]
            details = [ QStandardItem(str(x)) for x in data]
            [d.setTextAlignment(Qt.AlignCenter) for d in details]

            src_index = self.get_row_index("Source")
            status_index = self.get_row_index("Status")
            change_index = self.get_row_index("change")
            synp_index = self.get_row_index("SynP")
            bid_index = self.get_row_index("Bid")
            ask_index = self.get_row_index("Ask")
            for x in range(0, self.model.rowCount()):
                index = self.model.index(x, 1)
                table_symbol = index.data()
                if table_symbol != symbol:
                    continue
                for y in range(0, len(details)):
                    index = self.model.index(x, y)
                    self.model.setData(index, details[y].text())
                    if y == src_index:
                        tm = mapping['timestamp'](result)
                        delta = now - pd.to_datetime(tm)
                        self.set_color(index, Qt.green if delta < (timeout + pd.Timedelta("10 seconds")) else Qt.gray)



                status = self.model.index(x, status_index)
                self.set_color(status, Qt.green if "OPEN" in status.data().upper() else Qt.red)

                change_idx = self.model.index(x, change_index)
                self.set_color(change_idx, Qt.red if "-" in change_idx.data().upper() else Qt.green)


                # color relative to close price
                self.set_color(self.model.index(x, synp_index), Qt.red if "-" in change_idx.data().upper() else Qt.green)
                self.set_color(self.model.index(x, bid_index), Qt.red if "-" in change_idx.data().upper() else Qt.green)
                self.set_color(self.model.index(x, ask_index), Qt.red if "-" in change_idx.data().upper() else Qt.green)

        except:
            traceback.print_exc()

    def on_complete(self, symbol):
        #print("thread complete", symbol)
        del self.pending_req[symbol]

    def get_details(self, symbol):
        data = [ QStandardItem("YAHOO"), QStandardItem(symbol)]

        while (len(data) < len(self.headers)):
            data.append(QStandardItem(""))
        #data[0].setData(QBrush(Qt.gray), Qt.BackgroundRole)
        [d.setTextAlignment(Qt.AlignCenter) for d in data]
        return data



if __name__ == "__main__":
    df_holiday = pd.read_csv("holiday.csv", index_col=["date"])
    home_dir = os.path.expanduser("~")
    config_file = os.path.join(home_dir, ".yahoo_gui/config.csv")


    print(df_holiday.index)
    print(open_time, close_time)

    qapp = QApplication(sys.argv)
    app = App(config_file)
    sys.exit(qapp.exec_())