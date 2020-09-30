import sys
import re

from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QVBoxLayout, QWidget, QPushButton, QLineEdit 
from PyQt5.QtCore import Qt
from functools import partial


ERROR_MSG = "ERROR"
BUTTONS = {"AC": (0, 0),
           "+/-": (0, 1),
           "%": (0, 2),
           "/": (0, 3),
           "7": (1, 0),
           "8": (1, 1),
           "9": (1, 2),
           "*": (1, 3),
           "4": (2, 0),
           "5": (2, 1),
           "6": (2, 2),
           "-": (2, 3),
           "1": (3, 0),
           "2": (3, 1),
           "3": (3, 2),
           "+": (3, 3),
           "0": (4, 0),
          #  "(": (4, 1),
          #  ")": (4, 2),
           "=": (4, 3),
           }


class Calculator(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("Helena's Calculator")
    self.generalLayout = QVBoxLayout()
    self._centralWidget = QWidget(self)
    self.setCentralWidget(self._centralWidget)
    self._centralWidget.setLayout(self.generalLayout)
    self._createDisplay()
    self._createButtons()
  
  def _createDisplay(self):
    self.display = QLineEdit()
    self.display.setFixedHeight(35)
    self.display.setAlignment(Qt.AlignRight)
    self.generalLayout.addWidget(self.display)

  def _createButtons(self):
    self.buttons = {}
    buttonsLayout = QGridLayout()
    for buttonText, pos in BUTTONS.items():
      self.buttons[buttonText] = QPushButton(buttonText)
      self.buttons[buttonText].setFixedSize(70, 35)
      buttonsLayout.addWidget(self.buttons[buttonText], pos[0], pos[1])
    self.generalLayout.addLayout(buttonsLayout)

  def setDisplayText(self, text):
    self.display.setText(text)
    self.display.setFocus()
  
  def displayText(self):
    return self.display.text()

  def clearDisplay(self):
    self.setDisplayText('')


class Control():
  def __init__(self, model, view):
    self._evaluate = model
    self._view = view
    self._connectSignals()
  
  def _calculateResult(self):
    result = self._evaluate(expression=self._view.displayText())
    self._view.setDisplayText(result)

  def _buildExpression(self, buttonPressedText):
    if self._view.displayText() == ERROR_MSG:
      self._view.clearDisplay()
    expression = self._view.displayText() + buttonPressedText
    self._view.setDisplayText(expression)

  def switchSign(self):
    if self._view.displayText() == ERROR_MSG:
      self._view.clearDisplay()
    try:
      number = str(-1 * int(self._view.displayText()))
    except ValueError:
      number = self._view.displayText()
    self._view.setDisplayText(number)

  def asPercent(self):
    if self._view.displayText() == ERROR_MSG:
      self._view.clearDisplay()
    try:
      number = str(0.01 * float(self._view.displayText()))
    except ValueError:
      number = self._view.displayText()
    self._view.setDisplayText(number)
  
  def _connectSignals(self):
    for buttonText, button in self._view.buttons.items():
      if buttonText not in {"=", "AC", "+/-", "%"}:
        button.clicked.connect(partial(self._buildExpression, buttonText))
    self._view.buttons["+/-"].clicked.connect(self.switchSign)
    self._view.buttons["%"].clicked.connect(self.asPercent)
    self._view.buttons["="].clicked.connect(self._calculateResult)
    self._view.display.returnPressed.connect(self._calculateResult)
    self._view.buttons["AC"].clicked.connect(self._view.clearDisplay)


def main():
  calc = QApplication(sys.argv)
  view = Calculator()
  view.show()
  model = evaluateExpression
  Control(model=model, view=view)
  sys.exit(calc.exec())

def myEval(expression):
  # print(expression, " is type: ", type(expression))
  integers = parseExpression(expression)[0]
  operations = parseExpression(expression)[1]
  result = int(integers[0])
  for i,oval in enumerate(operations):
    other = int(integers[i+1])
    if oval == "+":
      result += other
    elif oval == "-":
      result -= other
    elif oval == "*":
      result = result * other
    elif oval == "/":
      result = result / other
  return result

def parseExpression(expression):
  integers = [ival for ival in re.split('\+|-|\*|/', expression) if ival.isdigit()]
  operations = [oval for oval in re.split('0|1|2|3|4|5|6|7|8|9|', expression) if oval in {"+", "-", "*", "/"}]
  return (integers, operations[:len(integers)])

def evaluateExpression(expression):
  try:
    result = str(myEval(expression))
  except Exception:
    result = ERROR_MSG
  return result


if __name__ == "__main__":
  main()
  # test = '97- 8+ 6*23/9182'
  # print(re.split('0|1|2|3|4|5|6|7|8|9|', test))
  