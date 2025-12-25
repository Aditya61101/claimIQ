import cv2

def preprocess_image_for_ocr(image):
    """
    image: numpy array
    return: processed image
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    height, width = gray.shape
    gray = cv2.resize(gray, (width*2, height*2), interpolation=cv2.INTER_CUBIC)

    # noise removal
    gray = cv2.GaussianBlur(gray, (5,5), 0)

    # adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )

    return thresh
