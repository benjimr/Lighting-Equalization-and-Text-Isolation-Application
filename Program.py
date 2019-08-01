# Ben Ryan
#The program will crop, reduce noise, sharpen and equalize lighting in an image with text.

import cv2
import numpy as np
import easygui

#used to store whether the user wants to see step by step or just final image
stepByStep = False
	
#used to crop the text from the image
def isolateBlock(imgOrig):
	img = imgOrig.copy()
	
	#getting image parameters for use later
	h, w, c = np.shape(img)
	
	#convert to YUV color space so we can extract the luminance channel for equalizing
	yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
	lum, _, _ = cv2.split(yuv)
		
	#blur the luminance channel
	k = (int(h*0.01), int(w*0.01))
	blurred = cv2.blur(lum, k)
	
	#creating a contrast limited adaptive histogram equalization object
	k = (int(h*0.03), int(w*0.03))
	clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=k)

	#use the clahe object on the blurred image to equalize the light
	#this whill help when thresholding
	blurEqualized = clahe.apply(blurred)
	
	#use a structuring element to open the image
	k = (int(h*0.01), int(w*0.01))
	structEl = cv2.getStructuringElement(cv2.MORPH_RECT, k)
	opened = cv2.morphologyEx(blurEqualized, cv2.MORPH_OPEN, structEl)
	
	#use adaptive binary inverse thresholding with gaussian
	thresholded = cv2.adaptiveThreshold(opened,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV, 15, 5)

	#erode the image to remove small contours
	k = (int(h*0.03), int(w*0.03))
	eroded = cv2.erode(thresholded, k, k[0])

	#use a new structuring element with same k size as eroded with to close the image
	structEl = cv2.getStructuringElement(cv2.MORPH_RECT, k)
	closed = cv2.morphologyEx(eroded, cv2.MORPH_CLOSE, structEl)
	
	#find the outer contours in the image with simple return, we don't need to consider the
	#hierachry here
	contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	#basing the following variables off the width and height of the image so they scale well
	imgArea = w*h
	minArea = imgArea * 0.001 #min area contour must be to be considered
	lineWidth = int(imgArea * 0.000001) #what line width should the box be drawn with so its visible when the image is displayed
	
	#how much to expand the ROI by either side, 
	expandDistX = int(w*0.02)
	expandDistY = int(h*0.02)
	
	#used to find the outer paramters of the contours
	xMin = w
	xMax = 0
	
	yMin = h
	yMax = 0
	
	#loop through all the contours found
	for contour in contours:
		#get contour area
		conArea = cv2.contourArea(contour)	

		#get rectangle parameters that surround it
		x,y,wC,hC = cv2.boundingRect(contour)
		
		#calc the bottom right corner points
		x2 = x+wC
		y2 = y+hC
		
		#at this point only significant parts of the image should be larger than minArea
		#so anything smaller should be ignored
		if  conArea > minArea:
			#draw green rectangle around significant contours
			cv2.rectangle(img,(x,y),(x2, y2),(0,255,0), lineWidth)
			
			#check if this contour is the furthest out in any direction and update values accordingly
			if x < xMin:
				xMin = x
				
			if x2 > xMax:
				xMax = x2
				
			if y < yMin:
				yMin = y
				
			if y2 > yMax:
				yMax = y2
		else:
			#draw red rectangle to show the contours not being considered
			cv2.rectangle(img,(x,y),(x2, y2),(0,0,255),lineWidth)
		
	#using above calculated expand distances, increase or decrease the min/max values
	#up to the expandDist but ensuring they don't go over the edge
	for x in range(0, expandDistX):
		if xMin > 0:
			xMin -= 1
			
		if xMax < w:
			xMax += 1
		
	for y in range(0, expandDistY):
		if yMin > 0:
			yMin -= 1
			
		if yMax < h:
			yMax += 1
			
	#sometimes the min, max values get swapped depending on the specific contours,  if this happens swap back
	if yMin > yMax:
		yMin, yMax = yMax, yMin
	
	if xMin > xMax:
		xMin, xMax = xMax, xMin
		
	#draw the blue outer rectangle which should encompass all significant contours
	cv2.rectangle(img,(xMin,yMin),(xMax,yMax),(255,0,0),lineWidth)

	#crop the original unedited image using the outer rectangle paramaters
	cropped = imgOrig[yMin:yMax, xMin:xMax]
	
	#draw contours on the original image to show how it found what it cropped
	cv2.drawContours(img, contours,-1,(0,255,255),1)
	
	#show the image at each step if that has been requested by the user.
	if stepByStep == True:
		print("Press any key to go to next step")
		showImage("Original", imgOrig, 1)
		showImage("YUV", yuv, 1)
		showImage("Y channel", lum, 1)
		showImage("blurred", blurred, 1)
		showImage("blurEqualized", blurEqualized , 1)
		showImage("opened", opened, 1)
		showImage("thresholded", thresholded, 1)
		showImage("eroded", eroded, 1)
		showImage("closed", closed, 1)
		showImage("contours", img, 1)
		showImage("cropped", cropped, 1)

	#return the cropped original, and the contours drawn on the original
	return cropped, img


#used to process an image to reduce noise, increase contrast, increase sharpness and equalize lighting
def process(imgOrig):
	img = imgOrig.copy()
	
	#getting image parameters for use later
	h, w, c = np.shape(img)
	
	#convert to YUV color space so we can extract the luminance channel for equalizing
	yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
	lum, u, v = cv2.split(yuv)

	#creating a contrast limited adaptive histogram equalization object
	k = (int(h*0.03), int(w*0.03))
	clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=k)
	
	#apply clahe to luminance channel
	lumEqualized = clahe.apply(lum)
	
	#merge the equalized channel back with the rest
	merged = cv2.merge((lumEqualized, u, v))
	
	#convert it back to bgr
	bgr = cv2.cvtColor(merged, cv2.COLOR_YUV2BGR)

	#getting k size
	k = [int(h*0.02), int(w*0.02)]
	
	#error prevention, ensuring acceptable input for gaussian
	if k[0] % 2 != 1:
		k[0] += 1
		
	if k[1] % 2 != 1:
		k[1] += 1
		
	k = (k[0], k[1])
		
	#apply gaussain blur
	gaussian = cv2.GaussianBlur(bgr, k, 0)
	
	#apply bilateral filter, this won't scale well, need to find way to dynamically choose the parameters
	#I tried to base them on width, height and averages but couldn't find the right balance, needs more testing.
	biLat = cv2.bilateralFilter(bgr, 30, 30, 30)
	
	#bilateral filter leaves slightly too much blur, so take away a gaussian blur to sharpen slightly
	bgrSub = cv2.addWeighted(biLat, 1.5, gaussian, -0.5, 0)
	gray = cv2.cvtColor(bgrSub, cv2.COLOR_BGR2GRAY)
	
	#use Laplacian operator to bring out the edges
	grayLap = cv2.Laplacian(gray, cv2.CV_8U)
	
	#subtract the laplacian from the grayscale to clean up the image
	graySub = cv2.addWeighted(gray, 1.5, grayLap, -0.3, 0)
	
	#show images at each step if user requested it
	if stepByStep == True:
		showImage("Luminance Channel Equalized", lumEqualized, 1)
		showImage("Merged back with U and V", merged, 1)
		showImage("Converted back to BGR", bgr, 1)
		showImage("Gaussian blurred", gaussian, 1)
		showImage("Bilateral Filters", biLat, 1)
		showImage("Gaussian Blur(-0.3) subtracted from Bilater filter(1.5)", bgrSub, 1)
		showImage("Converted to grayscale", gray, 1)
		showImage("Laplacian Operator used on gray", grayLap, 1)
		showImage("Laplacian subtracted from grayscale", graySub, 1)

	return graySub

#shows image and hold window open
def showImage(title, image, hold):
	shp = np.shape(image)
	while shp[0] > 1000 or shp[1] > 1800:
		shp = (int(shp[1]*.9), int(shp[0]*.9))
	
	cv2.namedWindow(title, cv2.WINDOW_KEEPRATIO)
	cv2.resizeWindow(title, shp[1], shp[0])
	cv2.imshow(title, image)
	
	if hold == 1:
		cv2.waitKey(0)
	else:
		return

#combines the original, the cropped, the contours drawn and the final output in to one image side by side
#just used for easy comparison
def combine(zipped, params, images):
	#unzip the parameters
	img1Params, img2Params, img3Params, img4Params = params
	
	#height of new image will be the highest of the images to be combined
	height = max(zipped[0])
	
	#width of new image will be the sum of the images to be combined
	width = sum(zipped[1])
	
	#create new image
	combined = np.zeros((height, width, 3), np.uint8)
	
	#calculate the starting positions
	pos1 = img1Params[1]+img2Params[1]
	pos2 = img1Params[1]+img2Params[1]+img3Params[1]
	
	#set the correct locations equal to the images
	combined[0:img1Params[0], 0:img1Params[1]] = images[0]
	combined[0:img2Params[0], img1Params[1]:pos1] = images[1]
	combined[0:img3Params[0], pos1:pos2] = images[2]
	combined[0:img4Params[0], pos2:width] = cv2.cvtColor(images[3], cv2.COLOR_GRAY2BGR)
	
	return combined

#used to check whether the user wants to see the output at each step, or just the final output
def getAns():
	ans = input('Show image step by step?(y/n)')

	if ans == 'y' or ans == 'Y':
		return True
	else:
		return False
	
def main():			
	#check if user wants step by step display
	global stepByStep
	stepByStep = getAns()

	#get file specified by the users
	file = easygui.fileopenbox()
	orig = cv2.imread(file)
	
	#error checking
	if orig is None:
		print("Error retrieving file. Please try again.")
		return
	
	print("May take more the 10 seconds on large images")
	print("Processing...")

	#isolate the text
	cropped, conDraw = isolateBlock(orig)
	
	#process to make it clearer and cleaner
	processed = process(cropped)
	
	#display combined image if step by step was requested
	if stepByStep == True or True:
		zipped = list(zip(np.shape(orig), np.shape(conDraw), np.shape(cropped), np.shape(processed)))
		params = (np.shape(orig), np.shape(conDraw), np.shape(cropped), np.shape(processed))
		images = [orig, conDraw, cropped, processed]
		
		combined = combine(zipped, params, images)
		showImage("combined", combined, 0)
	
	#display final output
	showImage("Final Output", processed, 1)
	
if __name__ == "__main__":
	main()
