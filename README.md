# LensReader

## Video Demo: https://youtu.be/V1mqvwGvnvg

## Description:

### Background

I developed the LensReader app with the primary goal of providing users with a seamless experience in converting images to text. This project allowed me to explore the realms of Optical Character Recognition (OCR) technology and create a user-friendly interface for efficient image-to-text conversion. The journey involved delving into image processing, text recognition algorithms, and enhancing the overall user experience.

I used python as the primary language for the app. The main libraries mainly used on the app are PyQt6, pytesseract, and Pillow. The app is inpsired from a web extension named blackbox as this extension made a lot of people's experience much easier and convenient especially when they want to copy a text from a video or any images. As someone who have appreciated this feature, I was inspired to make an app from this which everyone can make use of and make each and everyone's life easier and convenient.

### LensReader

LensReader is an application designed to convert images into editable text. With this user-friendly tool, users can extract text content from images effortlessly. The app is built to handle various image formats and provides accurate and reliable text conversion, making it a versatile solution for a wide range of users.

## Technicalities

In my project, I leveraged the powerful capabilities of the pytesseract module for seamless image-to-text conversion. This module, well-versed in handling such scenarios, offered a set of convenient methods that facilitated the transformation of images or snippets into editable text, streamlining the entire process with ease. The advantage of pytesseract's pre-trained models added an extra layer of accuracy to the optical character recognition (OCR) tasks, ensuring reliable results.

For the graphical user interface (GUI) of the application, I opted for PyQt6, a robust framework known for its flexibility and ease of use in creating interactive and visually appealing interfaces. PyQt6 provided a solid foundation for designing an intuitive user experience, enhancing the overall accessibility of the image-to-text conversion application.

To package the project into a standalone executable file, I turned to PyInstaller. This utility efficiently bundled all the necessary components, including the Python interpreter, libraries, and dependencies, into a single executable file. This not only simplified the deployment process but also made the application more user-friendly by eliminating the need for users to install additional dependencies manually.

In addition to these key components, I integrated Pillow and PyQt6.QtGui into the workflow to handle image processing tasks. These powerful libraries allowed me to implement image pre-processing techniques, such as noise reduction, rescaling, and grayscaling. These techniques played a crucial role in enhancing the quality of the input images, ultimately improving the accuracy of the OCR process. The combination of Pillow's versatile image processing capabilities and pytesseract's OCR prowess resulted in a robust and efficient solution for converting images to text within the application.

### Key Components

- **Image to text**: pytesseract have a lot of methods and features that allows programmers to perform Natural Language Processing and other processes.
- **User Interface**: The app features an intuitive user interface for a seamless experience.
- **Image Processing**: the app used image pre-processing techniques such as conversion to grayscale, noise reduction, and resizing or rescaling of an image

### How to Properly Run

To run the LensReader, we can do it in 2 ways:

First, 
1. python project.py

Second,
1. pyinstaller project.py
2. run the executable on the dist directory

## References

For the screenshot clipping tool, I got it from a github repository from god233012yamil (https://github.com/god233012yamil/pyqt_screen_capture)

**Thank you for using LensReader!**
We hope this tool enhances your workflow and proves to be a valuable asset. Feel free to explore and contribute to make it even better.
