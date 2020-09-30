import sys
import re

from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QVBoxLayout, QWidget, QPushButton, QLineEdit 
from PyQt5.QtCore import Qt
from functools import partial


ERROR_MSG = "ERROR"
BUTTONS = {"AC": (0, 0),
           "+/-": (0, 1),
           "^": (0, 2),
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
           "0": (4, 0, 1, 3),
           "=": (4, 3),
           }


class Calculator(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("Helena's Calculator")
    self.general_layout = QVBoxLayout()
    self._central_widget = QWidget(self)
    self.setCentralWidget(self._central_widget)
    self._central_widget.setLayout(self.general_layout)
    self._create_display()
    self._createButtons()

  def _create_display(self):
    """Creates a textbox to display expressions."""
    self.display = QLineEdit()
    self.display.setFixedHeight(35)
    self.display.setAlignment(Qt.AlignRight)
    self.general_layout.addWidget(self.display)

  def _createButtons(self):
    """Creates buttons for every button in BUTTONS at their defined positions."""
    self.buttons = {}
    buttons_layout = QGridLayout()
    for button_text, pos in BUTTONS.items():
      self.buttons[button_text] = QPushButton(button_text)
      if (button_text == "0"):
        self.buttons[button_text].setFixedSize(210, 35)
        buttons_layout.addWidget(self.buttons[button_text], pos[0], pos[1], pos[2], pos[3])
      else:
        self.buttons[button_text].setFixedSize(70, 35)
        buttons_layout.addWidget(self.buttons[button_text], pos[0], pos[1])
    self.general_layout.addLayout(buttons_layout)

  def set_display_text(self, text):
    """Update the expression in display with the given text parameter.
    
    Keyword Arguments:
    text -- the text to update the display view
    """
    self.display.setText(text)
    self.display.setFocus()
  
  def display_text(self):
    """Return the expression shown."""
    return self.display.text()

  def clear_display(self):
    """Reset expression to empty string."""
    self.set_display_text('')


class Control():
  def __init__(self, model, view):
    self._evaluate = model
    self._view = view
    self._connect_signals()
  
  def _calculate_result(self):
    result = self._evaluate(expression=self._view.display_text())
    self._view.set_display_text(result)

  def _build_expression(self, button_pressed_text):
    """Append expression with text from the clicked button.

    Keyword arguments:
    button_pressed_text -- the button's text to append to the end of the expression before updating display_text
    """
    if self._view.display_text() == ERROR_MSG:
      self._view.clear_display()
    expression = self._view.display_text() + button_pressed_text
    self._view.set_display_text(expression)

  def switch_sign(self):
    """Switch the integer displayed to have the opposite sign."""
    if self._view.display_text() == ERROR_MSG:
      self._view.clear_display()
    try:
      number = str(-1 * int(self._view.display_text()))
    except ValueError:
      number = self._view.display_text()
    self._view.set_display_text(number)
  
  def _connect_signals(self):
    """Connect the functions of buttons to the corresponding buttons on the calculator GUI."""
    for button_text, button in self._view.buttons.items():
      if button_text not in {"=", "AC", "+/-", "%"}:
        button.clicked.connect(partial(self._build_expression, button_text))
    self._view.buttons["+/-"].clicked.connect(self.switch_sign)
    self._view.buttons["="].clicked.connect(self._calculate_result)
    self._view.display.returnPressed.connect(self._calculate_result)
    self._view.buttons["AC"].clicked.connect(self._view.clear_display)


def main():
  calc = QApplication(sys.argv)
  view = Calculator()
  view.show()
  model = evaluate_expression
  Control(model=model, view=view)
  sys.exit(calc.exec())


"""
Some edges:
- *** => 0      | ERROR
- alpha => 0    | ERROR

Extended Features:
- exponent, square roots, square
- ()
- decimal math
- why do you have %
  # decimal_place = 1
  # 0.98
  # endr = 0
  # !!! hit decimal !!!
  # endr + (current_char / (10 ** decimal_place)) ; decimal_place += 1 ==> 0 + (9 / 10) ==> 0 + 0.9. ==> 0.9
  # 0.9 + (8 / (10 ** 2)) ==> 0.9 + 0.08 ==> 0.98
"""
def my_eval(expression):
  """Return the value of the evaluated expression.
  
  Keyword Arguments:
  expression -- the expression to evaluate

  result -- holds result of subexpression evaluated so far; helpful if () included
  intermediate_endr -- the larger, accumulated addend, subtrahend, multiplier, or divisor to calculate with the current result; i.e. results of parenthesized expressions
  endr -- to describe addend, subtrahend, multiplier, and divisors
  sign -- sign of the endr
  """
  result = 0
  intermediate_endr = 0
  endr = 0
  sign = 1
  current_operator = "+"
  for index,current_char in enumerate(expression + "+"):
    if (index > 0 and is_op(expression[index - 1]) and current_char == "-"):
      sign = -1
      continue
    elif is_op(current_char):
      if current_operator == "+":
        result += intermediate_endr
        intermediate_endr = endr
      elif current_operator == "-":
        result += intermediate_endr
        intermediate_endr = -1 * endr
      elif current_operator == "*":
        intermediate_endr *= endr
      elif current_operator == "/":
        intermediate_endr = int(intermediate_endr / endr)
      elif current_operator == "^":
        intermediate_endr = int(intermediate_endr ** endr)
      current_operator = current_char
      endr = 0
    elif current_char.isdigit():
      endr = (endr * 10) + (sign * int(current_char))
      sign = 1
  return int(sign * (result + intermediate_endr))
  

def is_op(c):
  """Returns if a char is one of four arithmetic operations.
  
  Keyword Arguments:
  c -- character to check if "+", "-", "*", or "/"
  """
  return c in {"+", "-", "*", "/", "^"}


def evaluate_expression(expression):
  """Return ERROR_MSG or value of the evaluated expression.

  Keyword Arguments:
  expression -- expression to be evaluated
  """
  try:
    result = str(my_eval(expression))
  except Exception as e:
    print(e)
    result = ERROR_MSG
  return result


if __name__ == "__main__":
  main()
  