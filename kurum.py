import sys
import math
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QVBoxLayout, QLineEdit
from PySide6.QtSql import QSqlDatabase, QSqlRecord, QSqlTableModel
from PySide6.QtUiTools import QUiLoader

app = QApplication()
#apply_stylesheet(app, theme = 'light_blue.xml')

loader = QUiLoader()

main = loader.load("main.ui", None)
form = loader.load("form.ui", None)
table = loader.load("table.ui", None)

class Window:

    def __init__(self, w):

        centralLayout = QVBoxLayout()

        centralLayout.addWidget(table)
        centralLayout.addWidget(form)

        w.centralwidget.setLayout(centralLayout)

        form.calculateButton.clicked.connect(self.calculate)
        table.newCalculationButton.clicked.connect(self.clearForm)
        table.deleteCalculationButton.setVisible(False)

        conn = QSqlDatabase.addDatabase("QSQLITE")
        conn.setDatabaseName("kurum.db")
        conn.open()

        columns = [
            "ID",
            "Снежный покров",
            "Длительность \n летнего \n периода (месяцы)",
            "Средняя \n летняя \n температура \n воздуха (°C)",
            "Средняя \n зимняя \n температура \n воздуха (°C)",
            "Плотность \n горных \n пород (kg/m³)",
            "Удельная \n теплоемкость \n мерзлых \n пород (J/kgK)",
            "Коэффициент \n теплопроводности \n мерзлых \n пород (W/mK)",
            "Эффективная \n теплопроводность \n слоя \n курума (W/mK)",
            "Ествественная \n температура \n грунтового \n основания (°C)",
            "Высота курума (m)"
        ]

        self.model = QSqlTableModel(None, conn)
        self.model.setTable("Results")
        self.model.setQuery("SELECT * FROM Results")

        for i, title in enumerate(columns):
            self.model.setHeaderData(i, Qt.Horizontal, title)

        table.tableView.setModel(self.model)
        table.tableView.hideColumn(0)
        table.tableView.resizeColumnsToContents()

        table.tableView.selectionModel().selectionChanged.connect(self.enableDelete)
        table.deleteCalculationButton.clicked.connect(self.deleteRow)

        table.tableView.show()

    def calculate(self):

        sn = form.snowCover.value()
        tl = float(form.avgSummerAirTemp.text())
        tz = float(form.avgWinterAirTemp.text())
        r = float(form.rocksDensity.text())
        c = float(form.frozenRocksHeatCapacity.text())
        l = float(form.frozenRocksHeatTransferCoeff.text())
        n = float(form.summerPeriodDuration.text())
        lk = float(form.kurumHeatTransferCoeff.text())
        te = float(form.soilNaturalTemp.text())

        p1 = (4.8 * 1000 * lk * tl * math.sqrt(3 * n))
        p2 = -(math.sqrt(r * c * l)) * (2 * te + tz / sn)

        h = round(p1 / p2, 2)

        record = self.model.record()
        record.setValue("ID", 0)
        record.setValue("snowCover", sn)
        record.setValue("avgSummerAirTemp", tl)
        record.setValue("avgWinterAirTemp", tz)
        record.setValue("rocksDensity", r)
        record.setValue("frozenRocksHeatCapacity", c)
        record.setValue("frozenRocksHeatTransferCoeff", l)
        record.setValue("summerPeriodDuration", n)
        record.setValue("kurumHeatTransferCoeff", lk)
        record.setValue("soilNaturalTemp", te)
        record.setValue("kurumHeight", h)

        res = self.model.insertRecord(-1, record)

        self.clearForm()
        
    def clearForm(self):
        inputs = form.findChildren(QLineEdit)
        for input in inputs:
            input.clear()
            form.snowCover.setValue(1.0)
            form.snowCover.setSpecialValueText("Нет покрова")

        table.tableView.clearSelection()
        table.deleteCalculationButton.setVisible(False)

    def enableDelete(self):
        table.deleteCalculationButton.setVisible(True)

    def deleteRow(self):
        rowIndex = table.tableView.currentIndex().row()
        self.model.removeRow(rowIndex)
        self.model.submitAll()
        self.model.select()
    

w = Window(main)

main.show()

sys.exit(app.exec())

