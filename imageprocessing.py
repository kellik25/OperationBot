import cv2
import numpy as np
import time
import paho.mqtt.client as mqtt

# Initialize MQTT client
mqtt_client = mqtt.Client()

# MQTT broker information
broker_address = "broker.hivemq.com"  # Update with your Hive MQTT broker address
broker_port = 1883

# Connect to the broker
mqtt_client.connect(broker_address, broker_port)


def send_mqtt_message(topic, payload):
    mqtt_client.publish(topic, payload)


def find_nearest_point(points, target):
    distances = np.linalg.norm(points - target, axis=1)
    nearest_index = np.argmin(distances)
    return tuple(points[nearest_index])

def find_orange_contours(image):
    centroids = []
    distances = []
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    cropped_image = hsv_image[:200, :]

    lower_orange = np.array([20, 124, 20])
    upper_orange = np.array([50, 200, 60])

    orange_mask = cv2.inRange(cropped_image, lower_orange, upper_orange)

    contours, _ = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # Calculate centroid
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            centroids.append((cX, cY))
            
    for centroid in centroids:
        cv2.circle(image, centroid, 5, (0, 255, 0), -1)

    # Calculate distance between centroids
    if len(centroids) == 2:
        distance = np.linalg.norm(np.array(centroids[0]) - np.array(centroids[1]))
        distances.append(distance)

    return distances



def find_intersection(line1, line2):
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2

    det = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if det == 0:
        return None

    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / det
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / det

    return int(px), int(py)


def operationCV(original_image, capture_mode=0, image_path=None):
    all_yellow_points = np.array([])
    intersection_point = [0, 0]  # Initialize intersection_point to None
    roi = False
    blue_contours = False
    moments = False
    min_yellow_area = 100
    og_saved = original_image.copy()

    hsv_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)

    lower_yellow = np.array([25, 80, 80])
    upper_yellow = np.array([40, 255, 255])

    yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)

    contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    valid_yellow_contours = [cnt for cnt in contours if cv2.contourArea(cnt) >= min_yellow_area]
    all_yellow_points = np.vstack(valid_yellow_contours) if valid_yellow_contours else np.array([])
    all_yellow_points = np.squeeze(all_yellow_points, axis=1) if all_yellow_points.size > 0 and all_yellow_points.shape[1] == 1 else all_yellow_points

    rows, cols = original_image.shape[:2]

    mid_x = cols // 2
    mid_y = rows // 2

    if all_yellow_points.size > 0:
        top_left = find_nearest_point(all_yellow_points, np.array([0, 0]))
        top_right = find_nearest_point(all_yellow_points, np.array([cols - 1, 0]))
        bottom_left = find_nearest_point(all_yellow_points, np.array([0, rows - 1]))
        bottom_right = find_nearest_point(all_yellow_points, np.array([cols - 1, rows - 1]))

        x_factor = 0.16
        y_factor = 0.56

        x_top = int(top_left[0] + x_factor * (top_right[0] - top_left[0]))
        y_top = int(0.5 * (top_right[1] + top_left[1]))

        x_bot = int(bottom_left[0] + x_factor * abs(bottom_right[0] - bottom_left[0]))
        y_bot = int(0.5 * (bottom_right[1] + bottom_left[1]))

        y_left = int(top_left[1] + y_factor * abs(top_left[1] - bottom_left[1]))
        x_left = int(0.5 * (top_left[0] + bottom_left[0]))

        y_right = int(top_right[1] + y_factor * abs(top_right[1] - bottom_right[1]))
        x_right = int(0.5 * (top_right[0] + bottom_right[0]))

        cv2.line(original_image, top_left, bottom_left, (0, 255, 0), 2)
        cv2.line(original_image, top_left, top_right, (0, 255, 0), 2)
        cv2.line(original_image, top_right, bottom_right, (0, 255, 0), 2)
        cv2.line(original_image, bottom_left, bottom_right, (0, 255, 0), 2)

        cv2.circle(original_image, (x_top, y_top), 5, (255, 0, 0), -1)
        cv2.circle(original_image, (x_bot, y_bot), 5, (255, 0, 0), -1)
        cv2.circle(original_image, (x_right, y_right), 5, (255, 0, 0), -1)
        cv2.circle(original_image, (x_left, y_left), 5, (255, 0, 0), -1)

        cv2.line(original_image, (x_top, y_top), (x_bot, y_bot), (0, 0, 255), 2)
        cv2.line(original_image, (x_left, y_left), (x_right, y_right), (0, 0, 255), 2)

        new_intersection_point = find_intersection((x_top, y_top, x_bot, y_bot), (x_left, y_left, x_right, y_right))

        if new_intersection_point is not None:
            cv2.circle(original_image, new_intersection_point, 5, (0, 255, 0), -1)
            if intersection_point is not None:
                # Check if there is a significant change in the intersection point
                distance_change = abs(sum(np.array(new_intersection_point) - np.array(intersection_point)))
                # print(distance_change)
                cv2.circle(original_image, new_intersection_point, 5, (0, 255, 0), -1)  # Display the new intersection point

            # Always update the ROI position
            roi_size = 60
            roi_x = max(0, new_intersection_point[0] - roi_size // 2)
            roi_y = max(0, new_intersection_point[1] - roi_size // 2)
            roi = og_saved[roi_y:roi_y + roi_size, roi_x:roi_x + roi_size]
            brightness_factor = 1.2  # Adjust this factor as needed
            brightened_roi = cv2.convertScaleAbs(roi, alpha=brightness_factor, beta=0)
            og_saved[roi_y:roi_y + roi_size, roi_x:roi_x + roi_size] = brightened_roi
            roi = og_saved[roi_y:roi_y + roi_size, roi_x:roi_x + roi_size]
            intersection_point = new_intersection_point  # Update the intersection_point

    # Search for white objects in the ROI
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        lower_blue = np.array([90, 100, 100])
        upper_blue = np.array([120, 255, 255])
        blue_mask = cv2.inRange(hsv_roi, lower_blue, upper_blue)
        cv2.imshow('Mask', blue_mask)
        blue_contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if blue_contours:
            # Find centroid of the first white object
            blue_object = max(blue_contours, key=cv2.contourArea)
            M = cv2.moments(blue_object)
            if M["m00"] != 0:
                moments = True
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                # Plot the centroid on the original image
                cv2.circle(original_image, (roi_x + cx, roi_y + cy), 5, (255, 0, 0), -1)
                
    #orange_contours = find_orange_contours(original_image)
    #print(orange_contours)

    # Find all light green objects in the original image
    lower_light_green = np.array([40, 40, 40])
    upper_light_green = np.array([80, 255, 255])
    light_green_mask = cv2.inRange(hsv_image, lower_light_green, upper_light_green)
    light_green_contours, _ = cv2.findContours(light_green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the centroid of the largest light green contour
    if light_green_contours:
        largest_light_green_contour = max(light_green_contours, key=cv2.contourArea)
        light_green_moment = cv2.moments(largest_light_green_contour)
        if light_green_moment["m00"] != 0:
            base_x = int(light_green_moment["m10"] / light_green_moment["m00"])
            base_y = int(light_green_moment["m01"] / light_green_moment["m00"])
            cv2.circle(original_image, (base_x, base_y), 5, (0, 0, 255), -1)
        

        if blue_contours:
            # Calculate distance between blue and green centroids in the original image
            piece_x = roi_x + cx  # Assuming you've already found the blue centroid in the ROI
            piece_y = roi_y + cy  # Assuming you've already found the blue centroid in the ROI
            distance_blue_green = np.linalg.norm(np.array([piece_x, piece_y]) - np.array([base_x, base_y]))

            distance1 = abs(top_right[0]-top_left[0])
            distance2 = abs(top_right[0]-bottom_left[0])
            distance3 = abs(bottom_right[0]-top_left[0])
            distance4 = abs(bottom_right[0]-bottom_left[0])
            

            # Calculate the average horizontal distance between all combinations in pixels
            average_horizontal_distance_pixels = (distance1+ distance2+distance3+ distance4) / 4
            #print(average_horizontal_distance_pixels)

            # Known physical width of the operation board in inches
            known_physical_width_inches = 12.8

            # Calculate the pixel-to-inch conversion factor
            pixel_to_inch_conversion = 0.043#known_physical_width_inches / average_horizontal_distance_pixels
            piece_distance = distance_blue_green * pixel_to_inch_conversion
            #print("Distance between blue and green dots (in inches):", piece_distance)
            piece_angle = 101+(101 - (np.arctan2(abs(piece_y - base_y),abs(piece_x - base_x)) * 180 / np.pi))
            #print(piece_angle)

            #print("Angle between blue and green centroids:", piece_angle)
            
            cv2.circle(original_image, (480,240), 5, (255, 255, 255), -1)
            return [piece_distance, piece_angle, piece_x, piece_y, base_x, base_y], original_image

def checkOperation(frame):
    point = (480,240)
    roi_size = 100
    roi_x = max(0, point[0] - roi_size // 2)
    roi_y = max(0, point[1] - roi_size // 2)
    roi = frame[roi_y:roi_y + roi_size, roi_x:roi_x + roi_size]
    lower_blue = np.array([90, 100, 100])
    upper_blue = np.array([120, 255, 255])
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    blue_mask = cv2.inRange(hsv_roi, lower_blue, upper_blue)
    
    if blue_mask.sum() >100:
        return True
    else:
        return False


# Example usage
def main():
    capture_mode = 1  # 0 for video capture, 1 for file processing
    url = '***********"
    #cv2.namedWindow('Original Image', cv2.WINDOW_NORMAL)
    #cv2.namedWindow('ROI', cv2.WINDOW_NORMAL)
    num_frames = 100
    angles = []
    distances = []
    send_mqtt_message('mode','initialize')
    print("Initializing...")
    time.sleep(2)
    print('Opening Camera...')
    cap = cv2.VideoCapture(url)
    trying = True
    while trying == True:
        for i in range(num_frames):
            ret, frame = cap.read()
            cv2.imshow('frame', frame)
            cv2.waitKey(1)
            if not ret:
                print('Failed to connect to Camera!')
            else:
                functionresult = operationCV(frame)
                if functionresult != None:
                    processed_frame = functionresult[0]
                    original_image = functionresult[1]
                else:
                    processed_frame = None
                    print('Unable to play Operation at this time. Please Try Again')
                    trying = False
                if processed_frame != None:
                    piece_distance, piece_angle = processed_frame[0], processed_frame[1]
                    distances.append(piece_distance)
                    angles.append(piece_angle)
            cv2.imshow('Original Image',original_image)
            cv2.waitKey(1)
        print(angles)
        avg_angle = round((sum(angles)/len(angles)),3)
        avg_radius = round((sum(distances)/len(distances)),3)
        #print('Avg Angle:',avg_angle)
        #print('Avg Radius:',avg_radius)
        send_mqtt_message('angle',str(avg_angle))
        time.sleep(.5)
        send_mqtt_message('radius',str(avg_radius))
        print("Going to the piece!")
        send_mqtt_message('mode','work')
        time.sleep(3)
        print('Moving down...')
        send_mqtt_message('mode','down')
        print('Moving to Checkpoint!')
        time.sleep(10)
        ret,frame = cap.read()
        cv2.imshow('frame',frame)
        cv2.waitKey(1)
        if not ret:
            print('Failed to connect to Camera!')
        else:
            functionresult = checkOperation(frame)
        if functionresult:
            print("I did it! Yay!")
            break
        else:
            print("Couldn't get the piece... Trying again.")
            send_mqtt_message('mode','initialize')
            time.sleep(3)
        
main()
