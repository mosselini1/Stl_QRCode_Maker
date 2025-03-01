
"""

Stl_QRCode_Maker

Original Author: Ainoretho (https://www.printables.com/@Ainoretho_411097)
Modifying Author: mosselini1 (https://www.printables.com/@mosselini1_1346202 & https://makerworld.com/en/@mosselini1)
Date: 01/03/25
"""

import qrcode

import numpy as np
import cadquery as cq

def make_qrcode(url):
	"""Url to numpy matrix"""
	
	qr = qrcode.QRCode()
	qr.add_data(url)
	qr.make()
	
	nb_lines = len(qr.modules)
	nb_cols = len(qr.modules[0])
	
	res = np.zeros((nb_lines,nb_cols),dtype=bool)
	
	for i in range(nb_lines):
		for j in range(nb_cols):
			res[i,j] = qr.modules[i][j]
			
	return res
	
def make_3dmodel_smart(np_mat,whished_dims,border,backplate_thickness,data_thickness,pixel_precision=1):
	"""
	Numpy matrix to cadquery object
	Based upon whished dimensions of the backplate and the (minimal) border it will determine the biggest pixel_size possible
	"""
		
	nb_lines,nb_cols = np_mat.shape
	
	whished_width,whished_height = whished_dims
	
	data_full_posib_size = min((whished_width-2*border)*(10**pixel_precision)//nb_cols,(whished_height-2*border)*(10**pixel_precision)//nb_lines)
	
	pixel_size = data_full_posib_size/(10**pixel_precision)
	print("chosen pixel size :", pixel_size)

	return make_3dmodel(np_mat,pixel_size,data_thickness,whished_dims,backplate_thickness)

def make_3dmodel_by_border(np_mat,pixel_size,backplate_thickness,data_thickness,border):
	"""
	Numpy matrix to cadquery object
	The backplate dimensions are determined by the pixel size and the border distance
	"""
	
	nb_lines,nb_cols = np_mat.shape
	
	data_width = pixel_size * nb_lines
	data_length = pixel_size * nb_cols
	
	full_width = data_width + border * 2
	full_length = data_length + border * 2
	return make_3dmodel(np_mat,pixel_size,data_thickness,(full_width,full_length),backplate_thickness)

def make_3dmodel(np_mat,pixel_size,data_thickness,backplate_size,backplate_thickness):
	"""
	Numpy matrix to cadquery object
	Specify manually the pixel_size and the backplate_size to define the overal object dimensions
	"""
	
	full_width,full_length = backplate_size
	
	nb_lines,nb_cols = np_mat.shape

	backplate = cq.Workplane('XY').rect(full_width, full_length).extrude(-backplate_thickness)
	
	data_blocks = []
	for x in range(nb_lines):
		for y in range(nb_cols):
			if np_mat[x,y]:
				x_pos = (x - nb_lines//2) * pixel_size + (pixel_size/2)*(nb_lines%2 == 0)
				y_pos = (y - nb_cols//2) * pixel_size + (pixel_size/2)*(nb_cols%2 == 0)
				
				data_block = cq.Workplane('XY').center(x_pos, y_pos).box(pixel_size, pixel_size, data_thickness,(True,True,False))
				data_blocks.append(data_block.val())

	return cq.Compound.makeCompound([backplate.val()]+data_blocks) # a coumpound is a collection of loose objects, in a 3d slicer will alow easy multicolor

def main():
	"""
	The main function of the program
	"""
	
	link = "https://github.com/mosselini1/Stl_QRCode_Maker" # input
	
	qrcode_mat = make_qrcode(link)
	
	tol = 0.15
	border = 2
	backplate_thickness = 3-tol/2
	data_thickness = 1 # height of the pixel layer
	backplate_size = (60-tol,60-tol)
	pixel_precision = 1 # amount of decimals for the pixel size
	
	model = make_3dmodel_smart(qrcode_mat,backplate_size,border,backplate_thickness,data_thickness,1)
	model.exportStl(f"qrcode_model.stl") # output
	
	"""
	model = make_3dmodel_by_border(qrcode_mat,1.5,backplate_thickness,data_thickness,border)
	model.exportStl(f"qrcode_model.stl")
	"""

if __name__ == '__main__': main()
