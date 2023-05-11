import sys
import threading
import time
import numpy as np
import matplotlib.pyplot as plt

import requests
from PyQt5 import QtCore, QtWidgets
from ex5_ui import Ui_MainWindow

class FileDownloader(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.startButton.clicked.connect(self.download)
        self.urls = []
        self.results = []

        self.ui.progressBar1.setValue(0)
        self.ui.progressBar2.setValue(0)
        self.ui.progressBar3.setValue(0)

    def sizeof_format(self, num=None):
        for unit in ['', 'K', 'M', 'G']:
            if abs(num) < 1024.0:
                return f'{num:.2f} {unit}B'
            num /= 1024.0
        return f'{num:.2f} TB'

    def download(self):
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


def ex5():
    window = QtCore.QCoreApplication.instance()
    if window is None:
        window = QtWidgets.QApplication(sys.argv)
    app = FileDownloader()
    app.show()
    sys.exit(window.exec_())

if __name__ == '__main__':
    ex5()
