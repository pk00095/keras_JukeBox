import math

def calculate_efffective_lr(initial_lr, operator, operand=None):
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
			print('unsupported operand {}, retrning f(x)=x'.format(operator))
		return initial_lr