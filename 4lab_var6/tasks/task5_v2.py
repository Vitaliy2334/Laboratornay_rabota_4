import sys
import threading
import time
import numpy as np
import matplotlib.pyplot as plt

import requests
from PyQt5 import QtCore, QtWidgets
from task5_ui import Ui_MainWindow


class newWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.startButton.clicked.connect(self.start)
        self.urls = []
        self.results = []

        self.ui.progressBar1.setValue(0)
        self.ui.progressBar2.setValue(0)
        self.ui.progressBar3.setValue(0)

        # for test
        self.ui.file1UrlInput.setText('https://download.microsoft.com/download/5/D/8/5D8C65CB-C849-4025-8E95-C3966CAFD8AE/vcredist_x86.exe')
        self.ui.file2UrlInput.setText('https://download.microsoft.com/download/1/6/B/16B06F60-3B20-4FF2-B699-5E9B7962F9AE/VSU_4/vcredist_x64.exe')
        self.ui.file3UrlInput.setText('https://aka.ms/vs/17/release/vc_redist.arm64.exe')

    def sizeof_fmt(self, num, suffix='B'):
        for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti']:
            if abs(num) < 1024.0:
                return f"{num:.2f} {unit}{suffix}"
            num /= 1024.0
        return f"{num:.2f} Pi{suffix}"

    def start(self):
        if self.ui.file1UrlInput.text() and self.ui.file1UrlInput.text().__contains__('http'):
            self.urls.append({'url': self.ui.file1UrlInput.text(), 'progressBar': self.ui.progressBar1})
        if self.ui.file2UrlInput.text() and self.ui.file2UrlInput.text().__contains__('http'):
            self.urls.append({'url': self.ui.file2UrlInput.text(), 'progressBar': self.ui.progressBar2})
        if self.ui.file3UrlInput.text() and self.ui.file3UrlInput.text().__contains__('http'):
            self.urls.append({'url': self.ui.file3UrlInput.text(), 'progressBar': self.ui.progressBar3})

        threads = []
        for url in self.urls:
            t = threading.Thread(target=self.download, args=(url['url'], url['progressBar']))
            threads.append(t)
            t.start()

        for thread in threads:
            thread.join()

        self.show_results()

    def download(self, url, progressBar):
        start_time = time.time()

        response = requests.get(url, stream=True)
        if response.status_code == 200:
            total_len = int(response.headers.get('content-length'))
            progressBar.setMaximum(total_len)
            bytes_read = 0
            with open(url.split('/')[-1], 'wb') as f:
                for chunk in response.iter_content(chunk_size=4096):
                    f.write(chunk)
                    bytes_read += len(chunk)
                    progressBar.setValue(bytes_read)

        download_time = (time.time() - start_time)
        result = (url.split('/')[-1], total_len, download_time)

        self.results.append(result)

    def show_results(self):
        for res in self.results:
            print(res)

        download_times = []
        download_times_out = []
        file_sizes = []
        file_names = []
        for res in self.results:
            file_names.append(res[0])
            file_sizes.append(res[1])
            download_times.append(res[2])
            download_times_out.append(f"{int(res[2])}s {int((res[2]-int(res[2]))*1000)}ms")



        #создание областей для рисования
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15,10))

        # гистограмма
        x_pos = np.arange(len(file_names))
        ax1.bar(x_pos, download_times, align='center', alpha=0.5)
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(file_names)
        ax1.set_ylabel('Time (s)')
        ax1.set_xlabel('File names')
        ax1.set_title('Download time')

        for i, v in enumerate(download_times_out):
            ax1.text(i, download_times[i]-0.2, v, ha='center')

        # круговая
        labels = [f"{file_names[i]} \n[{self.sizeof_fmt(file_sizes[i])}]" for i in range(len(file_names))]
        ax2.pie(file_sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax2.set_title("File sizes")

        plt.show()


def task5():
    app = QtCore.QCoreApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    window = newWindow()
    window.show()
    sys.exit(app.exec_())