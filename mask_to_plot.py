import cv2 as cv
import numpy as np

def translate(i,mn,mx,newmn,newmx):
	return newmn+((i-mn)/(mx-mn))*(newmx-newmn)


def visualize_mask(mask):
	st=np.unique(mask)
	sorted(st)
	mp={}
	for (i,val) in enumerate(st):
		mp[val]=translate(i,0,len(st)-1,0,255)
	newmask=mask.copy();
	for i in range(len(mask)):
		for j in range(len(mask[i])):
			newmask[i][j]=mp[mask[i][j]]
	cv.imshow('mask',newmask)
	cv.waitKey()
	cv.destroyAllWindows()


def give_contours(img,mask,min_area=100):
	mask=cv.cvtColor(mask,cv.COLOR_BGR2GRAY)
	st=np.unique(mask)
	contours=[]
	for i in st:
		if i==0:
			continue;
		newmask=(mask==i).astype(np.uint8)*255;
		curr,hei=cv.findContours(newmask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE)
		for c in curr:
			if cv.contourArea(c)>min_area:
				contours.append(c)
	return contours


def contours_overlay(contours,img):
	overlay_img=img.copy()
	cv.drawContours(overlay_img,contours,-1,(0,0,255),2)
	return overlay_img
