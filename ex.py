"""
このモジュールはサンプルです。
"""

def hello():
	"""この関数は挨拶をします"""
	print("hello")

def calc_int(a: int, b: int) -> int:
	"""
	この関数は整数を足し算します。
	
	Args:
		a (int): 足し算の左辺の整数
		b (int): 足し算の右辺の整数
	Returns:
		int: aとbの計算結果。
	
	Examples:
		>>> calc_int(1, 2)
		3
	"""
	return a + b

if __name__ == "__main__":
	import doctest
	doctest.testmod()
