import pickle
import cv2
import numpy as np

#########################
# Camera settings
cam_id = 1  # Change this to your desired camera ID, try 0 for default webcam
width, height = 1920, 1080  # Change this to desired image resolution
#########################

# Initialize variables
cap = cv2.VideoCapture(cam_id)  # For Webcam
cap.set(3, width)  # Set width
cap.set(4, height)  # Set height
points = np.zeros((4, 2), int)  # Array to store clicked points
counter = 0  # Counter to track the number of clicked points

def mousePoints(event, x, y, flags, params):
    """
    Callback function for mouse clicks.

    Args:
        event: OpenCV event type (e.g., cv2.EVENT_LBUTTONDOWN)
        x: X-coordinate of the mouse click
        y: Y-coordinate of the mouse click
        flags: Additional flags associated with the event
        params: User-defined parameters passed to the callback function

    Returns:
        None
    """
    global counter
    if event == cv2.EVENT_LBUTTONDOWN:
        points[counter] = x, y  # Store the clicked point
        counter += 1  # Increment counter
        print(f"Clicked points: {points}")

def warp_image(img, points, size=[1920, 1080]):
    """
    Warps an image based on the selected points.

    Args:
        img: The image to be warped
        points: Array containing four clicked points
        size: Desired size of the warped image

    Returns:
        imgOutput: The warped image
        matrix: The perspective transformation matrix
    """
    pts1 = np.float32(points)  # Convert points to float32
    pts2 = np.float32([[0, 0], [size[0], 0], [0, size[1]], [size[0], size[1]]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)  # Calculate perspective transformation matrix
    imgOutput = cv2.warpPerspective(img, matrix, (size[0], size[1]))  # Warp the image
    return imgOutput, matrix

while True:
    success, img = cap.read()

    if counter == 4:
        # Save selected points to file
        with open("map.p", "wb") as fileObj:
            pickle.dump(points, fileObj)
        print("Points saved to file: map.p")
        # Warp the image
        imgOutput, matrix = warp_image(img, points)
        # Display warped image
        cv2.imshow("Output Image", imgOutput)

    # Draw circles at clicked points
    for x in range(0, 4):
        cv2.circle(img, (points[x][0], points[x][1]), 3, (0, 255, 0), cv2.FILLED)

    if not success:
        print("Failed to capture image")
        break

    cv2.imshow("Original Image", img)
    cv2.setMouseCallback("Original Image", mousePoints)

    # Wait for a key press for 1 ms
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
