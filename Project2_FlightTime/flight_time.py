"""
Interactive Map - Flight Time

Functionality:
- This script creates an interactive map application that allows users to interact with a digital map using hand gestures.
- It processes live video feed from a webcam to detect hand positions and movements.
- The script warps the webcam feed to align with a digital map and allows users to select and interact with different regions on the map.
- It displays flight times between selected countries based on hand gestures.

Usage:
- The script is executed in a Python environment with the necessary libraries installed.
- It requires a webcam to capture live video feed for hand tracking.
- Users can interact with the map by moving their hands in front of the webcam. The application responds to these movements and displays relevant information on the screen.

Libraries:
- pickle: Used for loading serialized Python objects, specifically map points and country polygons.
- cv2 (OpenCV): Utilized for image processing and computer vision tasks.
- cvzone: A library built on top of OpenCV to simplify certain tasks, including hand tracking.
- numpy (NumPy): Essential for numerical operations, particularly in handling arrays and image data.
- HandDetector from cvzone: A pre-built class for detecting and tracking hand movements in real-time.

Note:
- The script assumes the presence of pre-processed data files for map points and country polygons.
- It is designed to be run in a Python environment where the aforementioned libraries are installed.

**Author:** Murtaza Hassan
**Website:** www.computervision.zone

"""

# Import necessary libraries
import pickle  # Pickle library for serializing Python objects
import cv2  # OpenCV library for computer vision tasks
import cvzone
import numpy as np  # NumPy library for numerical operations
from cvzone.HandTrackingModule import HandDetector

######################################
cam_id = 1
width, height = 1920, 1080
map_file_path = "../Step1-GetCornerPoints/map.p"
countries_file_path = "../Step2_Get_Country_Polygons/countries.p"
######################################

file_obj = open(map_file_path, 'rb')
map_points = pickle.load(file_obj)
file_obj.close()
print(f"Loaded map coordinates.")

# Load previously defined Regions of Interest (ROIs) polygons from a file
if countries_file_path:
    file_obj = open(countries_file_path, 'rb')
    polygons = pickle.load(file_obj)
    file_obj.close()
    print(f"Loaded {len(polygons)} countries.")
else:
    polygons = []

# Open a connection to the webcam
cap = cv2.VideoCapture(cam_id)  # For Webcam
# Set the width and height of the webcam frame
cap.set(3, width)
cap.set(4, height)
# Counter to keep track of how many polygons have been created
counter = 0
# Initialize the HandDetector class with the given parameters
detector = HandDetector(staticMode=False,
                        maxHands=2,
                        modelComplexity=1,
                        detectionCon=0.5,
                        minTrackCon=0.5)

flight_time_list = [["USA", "India", "14 hours"],
                    ["USA", "China", "15 hours"],
                    ["Russia", "India", "6 hours"],
                    ["Canada", "India", "17 hours"],
                    ["Saudi Arabia", "USA", "14 hours"],
                    ]


def warp_image(img, points, size=[1920, 1080]):
    """
    Warp the input image based on the provided points to create a top-down view.

    Parameters:
    - img: Input image.
    - points: List of four points representing the region to be warped.
    - size: Size of the output image.

    Returns:
    - imgOutput: Warped image.
    - matrix: Transformation matrix.
    """
    pts1 = np.float32([points[0], points[1], points[2], points[3]])
    pts2 = np.float32([[0, 0], [size[0], 0], [0, size[1]], [size[0], size[1]]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgOutput = cv2.warpPerspective(img, matrix, (size[0], size[1]))
    return imgOutput, matrix


def warp_single_point(point, matrix):
    """
    Warp a single point using the provided perspective transformation matrix.

    Parameters:
    - point: Coordinates of the point to be warped.
    - matrix: Perspective transformation matrix.

    Returns:
    - point_warped: Warped coordinates of the point.
    """
    # Convert the point to homogeneous coordinates
    point_homogeneous = np.array([[point[0], point[1], 1]], dtype=np.float32)

    # Apply the perspective transformation to the point
    point_homogeneous_transformed = np.dot(matrix, point_homogeneous.T).T

    # Convert back to non-homogeneous coordinates
    point_warped = point_homogeneous_transformed[0, :2] / point_homogeneous_transformed[0, 2]
    point_warped = int(point_warped[0]), int(point_warped[1])

    return point_warped


def inverse_warp_image(img, imgOverlay, map_points):
    """
    Inverse warp an overlay image onto the original image using provided map points.

    Parameters:
    - img: Original image.
    - imgOverlay: Overlay image to be warped.
    - map_points: List of four points representing the region on the map.

    Returns:
    - result: Combined image with the overlay applied.
    """
    # Convert map_points to NumPy array
    map_points = np.array(map_points, dtype=np.float32)

    # Define the destination points for the overlay image
    destination_points = np.array([[0, 0], [imgOverlay.shape[1] - 1, 0], [0, imgOverlay.shape[0] - 1],
                                   [imgOverlay.shape[1] - 1, imgOverlay.shape[0] - 1]], dtype=np.float32)

    # Calculate the perspective transform matrix
    M = cv2.getPerspectiveTransform(destination_points, map_points)

    # Warp the overlay image to fit the perspective of the original image
    warped_overlay = cv2.warpPerspective(imgOverlay, M, (img.shape[1], img.shape[0]))

    # Combine the original image with the warped overlay
    result = cv2.addWeighted(img, 1, warped_overlay, 0.65, 0, warped_overlay)

    return result


def get_finger_location(img, imgWarped):
    """
    Get the location of the index finger tip in the warped image.

    Parameters:
    - img: Original

 image.

    Returns:
    - warped_point: Coordinates of the index finger tip in the warped image.
    """
    # Find hands in the current frame
    hands, img = detector.findHands(img, draw=False, flipType=True)
    # Check if any hands are detected
    if hands:
        # Information for the first hand detected
        hand1 = hands[0]  # Get the first hand detected
        indexFinger = hand1["lmList"][8][0:2]  # List of 21 landmarks for the first hand
        # cv2.circle(img,indexFinger,5,(255,0,255),cv2.FILLED)
        warped_point = warp_single_point(indexFinger, matrix)
        warped_point = int(warped_point[0]), int(warped_point[1])
        print(indexFinger, warped_point)
        cv2.circle(imgWarped, warped_point, 5, (255, 0, 0), cv2.FILLED)
        if len(hands) == 2:
            hand2 = hands[1]
            indexFinger2 = hand2["lmList"][8][0:2]  # List of 21 landmarks for the first hand
            warped_point2 = warp_single_point(indexFinger2, matrix)
            cv2.circle(imgWarped, warped_point2, 5, (255, 0, 255), cv2.FILLED)
            warped_point = [warped_point, warped_point2]

    else:
        warped_point = None

    return warped_point


def create_overlay_image(polygons, warped_point, imgOverlay):
    """
    Create an overlay image with marked polygons based on the warped finger location.

    Parameters:
    - polygons: List of polygons representing countries.
    - warped_point: Coordinates of the index finger tip in the warped image.
    - imgOverlay: Overlay image to be marked.

    Returns:
    - imgOverlay: Overlay image with marked polygons.
    """

    if isinstance(warped_point, list):
        check = []
        for warp_point in warped_point:
            for polygon, name in polygons:
                polygon_np = np.array(polygon, np.int32).reshape((-1, 1, 2))
                result = cv2.pointPolygonTest(polygon_np, warp_point, False)
                if result >= 0:
                    cv2.polylines(imgOverlay, [np.array(polygon)], isClosed=True, color=(0, 255, 0), thickness=2)
                    cv2.fillPoly(imgOverlay, [np.array(polygon)], (0, 255, 0))
                    cvzone.putTextRect(imgOverlay, name, polygon[0], scale=1, thickness=1)
                    # cvzone.putTextRect(imgOverlay, name, (0, 100), scale=8, thickness=5)
                    check.append(name)
        if len(check) == 2:
            cv2.line(imgOverlay, warped_point[0], warped_point[1], (0, 255, 0), 10)
            for flight_time in flight_time_list:
                if check[0] in flight_time and check[1] in flight_time:
                    cvzone.putTextRect(imgOverlay, flight_time[1] + " to " + flight_time[0], (0, 100), scale=8,
                                       thickness=5)
                    cvzone.putTextRect(imgOverlay, flight_time[2], (0, 200), scale=8, thickness=5)
    else:
        # loop through all the countries
        for polygon, name in polygons:
            polygon_np = np.array(polygon, np.int32).reshape((-1, 1, 2))
            result = cv2.pointPolygonTest(polygon_np, warped_point, False)
            if result >= 0:
                cv2.polylines(imgOverlay, [np.array(polygon)], isClosed=True, color=(0, 255, 0), thickness=2)
                cv2.fillPoly(imgOverlay, [np.array(polygon)], (0, 255, 0))
                cvzone.putTextRect(imgOverlay, name, polygon[0], scale=1, thickness=1)
                cvzone.putTextRect(imgOverlay, name, (0, 100), scale=8, thickness=5)

    return imgOverlay


while True:
    # Read a frame from the webcam
    success, img = cap.read()
    imgWarped, matrix = warp_image(img, map_points)
    imgOutput = img.copy()

    # Find the hand and its landmarks
    warped_point = get_finger_location(img, imgWarped)

    h, w, _ = imgWarped.shape
    imgOverlay = np.zeros((h, w, 3), dtype=np.uint8)

    if warped_point:
        imgOverlay = create_overlay_image(polygons, warped_point, imgOverlay)
        imgOutput = inverse_warp_image(img, imgOverlay, map_points)

    # imgStacked = cvzone.stackImages([img, imgWarped,imgOutput,imgOverlay], 2, 0.3)
    # cv2.imshow("Stacked Image", imgStacked)

    # cv2.imshow("Original Image", img)
    # cv2.imshow("Warped Image", imgWarped)
    cv2.imshow("Output Image", imgOutput)

    key = cv2.waitKey(1)