import math

from PyQt5 import QtGui, QtWidgets

def black_print(text):
    print('\033[30m{}\033[0m'.format(text))

def red_print(text):
    print('\033[31m{}\033[0m'.format(text))

def green_print(text):
    print('\033[32m{}\033[0m'.format(text))

def yellow_print(text):
    print('\033[33m{}\033[0m'.format(text))

def blue_print(text):
    print('\033[34m{}\033[0m'.format(text))

def magenta_print(text):
    print('\033[35m{}\033[0m'.format(text))

def cyan_print(text):
    print('\033[36m{}\033[0m'.format(text))

def gray_print(text):
    print('\033[90m{}\033[0m'.format(text))
    

class FloatNotEmptyValidator(QtGui.QValidator):
    def validate(self, text, pos):
        state = QtGui.QIntValidator.Acceptable if float(text) else QtGui.QIntValidator.Invalid
        return state, text, pos

def calculate_efffective_lr(initial_lr, operator, operand):
	if operator == '*':
		assert operand!=None and operand>0,'operand cannot be negative or None'
		return initial_lr*operand
	elif operator == '/':
		assert operand!=None and operand>0,'operand cannot be negative or None'
		return initial_lr/operand
	elif operator == '+':
		assert operand!=None and operand>0,'operand cannot be negative or None'
		return initial_lr+operand
	elif operator == '-':
		assert operand!=None and operand>0,'operand cannot be negative or None'
		assert (initial_lr>operand),'operand({}) cannot be greater than learning_rate({})'.format(operand,initial_lr)
		return initial_lr-operand 
	else:
		if operator != 'f(x)':
			return operand
		else:
			print('unsupported operand {}, retrning f(x)=x'.format(operator))
			return initial_lr
