The goal of this program is to crop, reduce noise, sharpen and equalize lighting in an image with text.

## How to use
First the user must choose whether they want the output to be shown step by step using command line text input
Next they will select the image for the program to use using easygui
If they have chosen to go step by step, they can press any key to move on to the next step.

## Scalability
I have based as many of my parameters as possible off the image, such as deciding
kernel size and minimum contour area based on image width and height

## Optimization
Mainly due to the process() function and the filering, on very large images it can take a while.
Never more than 15 seconds in my experience but may vary from computer to computer.
'text.jpg' is quite low resolution so it is very quick

## Sample Images and Results
### Sample 1 - Main Task
<table style="text-align:center; float:center;">
<tr>
<td style="width:300px; text-align:center;">
    <img src="https://i.imgur.com/blI49aZ.jpg" alt="Original" width="300"/><br>Original
</td>

<td style="width:300px; text-align:center;">
    <img src="https://i.imgur.com/qxKnaTC.jpg" alt="Contoured" width="300"/><br>Contoured
</td>
</tr>

<tr>
<td style="width:300px; text-align:center;">
<img src="https://i.imgur.com/IXaA8jn.jpg" alt="Processed 1" width="300"/><br>Processed Option 1
</td>

<td style="width:300px; text-align:center;">
<img src="https://i.imgur.com/YTnhluH.jpg" alt="Processed 2" width="300"/><br>Processed Option 2
</td>
</tr>
</table>


### Sample 2 - Difficult Extra Sample
<table style="text-align:center; float:center;">
<tr>
<td style="width:300px; text-align:center;">
<img src="https://i.imgur.com/cNADitA.jpg" alt="Original" width="300"/><br>Original
</td>

<td style="width:300px; text-align:center;">
<img src="https://i.imgur.com/434t9Ch.jpg" alt="Contoured" width="300"/><br>Contoured
</td>
</tr>

<tr>
<td style="width:300px; text-align:center;">
<img src="https://i.imgur.com/yPojSku.jpg" alt="Processed 1" width="300"/><br>Processed Option 1
</td>

<td style="width:300px; text-align:center;">
<img src="https://i.imgur.com/sg5fZVz.jpg" alt="Processed 2" width="300"/><br>Processed Option 2
</td>
</tr>
</table>


### Armistice Image - Secondary Objective
The armistice image is a photo of a message notifying WWI soldiers of the armistice. This project was developed close to the centenary of armistice day, and so the restoration of this image was thrown in as a secondary objective.
It works to a certain extent on this image, in terms of cropping and light equalization, however the faded text is still quite unreadable.

<table style="text-align:center; float:center;">
<tr>
<td style="width:300px; text-align:center;">
<img src="https://i.imgur.com/RvmcHpF.jpg" alt="Original" width="300"/><br>Original
</td>

<td style="width:300px; text-align:center;">
<img src="https://i.imgur.com/AlsY1gp.jpg" alt="Contoured" width="300"/><br>Contoured
</td>
</tr>

<tr>
<td style="width:300px; text-align:center;">
<img src="https://i.imgur.com/wikl8pB.jpg" alt="Processed 1" width="300"/><br>Processed Option 1
</td>

<td style="width:300px; text-align:center;">
<img src="https://i.imgur.com/uYg7VLK.jpg" alt="Processed 2" width="300"/><br>Processed Option 2
</td>
</tr>
</table>

## Summary of Functions
isolateBlock() : used for cropping sections of the image
process() : used for reducing noise, increasing contrast, sharpening, and lighting equalization
showImage() : used for display images and holding the program more easily
combine(): used for combining some of the outputs for easier comparison in the step by step display
getAns() : used to check if user wants step by step output
main(): used to control the flow of the program


## Isolation Steps

isolateBlock() is used to crop the text from the image
Steps:

1. Convert to YUV color space and extract the Y channel
		Using this color space so we can access the luminance channel

2. Blur the Y channel
		Do this to remove as much noise as possible without losing too much data
		Here we aren't worrying about text quality, just text location, so blurring 
		may make it unreadable at this point.

3. Use Contrast Limited Adaptive Histogram Equalization
		This equalizes the lighting making the text areas more visible against the background

4. Open the image using morphologyEx
		This is done to merge as much of the black text blobs together so thresholding is easier

5. Use adaptive inverse binary thresholding
		This will clearly show most of the blobs of text as white and the background as black

6. Erode the image
		This will remove most of the small contours that are not part of the text

7. Close the image using morphologyEx
		This will combine the remaining contours in to much larger contours
		This works on the idea that most of the time, text is grouped together
		So at this point the contours that are from text, should join together

8. Find the outer contours
		Gives us all the remaining outermost contours, should just be the text at this point

9. Draw contours and bounding boxes for step by step
		Draw all contours in yellow
		Draw bounding boxes around contours with significant enough area in green
		Draw bounding boxes around contours with not enough area in red
		This is just done to show the user what it found, if showing step by step

10. Crop the calculated outer bounding box
		Taking the outermost paramaters from the significant contours
		Use this as the box to be cropped
		Expand this box out a certain amount in all directions
		this can help correct some potential over erosion of important areas
		instead of using dilation which would potentially enlarge unimportant areas.



## Lighting Equalization

process() is used to process an image to reduce noise, increase contrast, increase sharpness and light equalization
This section can be quite slow on very large images. 'Text.jpg' is not very big so it is quick.

Steps:
1. Convert to YUV color space and extract the Y channel
		Using this color space so we can access the luminance channel, as above

2. Use Contrast Limited Adaptive Histogram Equalization
		This equalizes the lighting making the text more visible against the background, as above

3. Merge the equalized channel back with u, v
		This gives us back a 3D image with the luminance equalized

4. Convert to BGR and apply Gaussian Blur and Bilateral Filter seperately
		The gaussian blur will reduce noise
		The Bilateral filter reduces noise but helps keep the edges of the letters clear

5. Use weighted subtraction to subtract the Gaussian Blur from the Bilateral Filter
		Bilateral filtering involves blurring.
		We don't want it blurred so we subtract the gaussian blur from the bilateral filter
		This leaves just the clearer edges from the bilateral filter

6. Convert to grayscale and apply Laplacian operator
		The Laplacian operator shows edges in an image
		At this point the text should be the only edges left
		So the text should be clearly shown 

7. Subtract the laplacian from the grayscale
		When we subtract the laplacian from the grayscale image we are left with
		just the text on a mostly white/gray, evenly lit background.
		This is our final output

Note: Both steps 5 and 7 have output that could be desirable final products in different conditions, 5 gives closer to true colour output, while 7 give the appearance of a black and white scan.
