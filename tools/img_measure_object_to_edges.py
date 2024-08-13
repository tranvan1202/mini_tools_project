import cv2
import os
import numpy as np

def calculate_font_scale(text, max_width, max_height, font=cv2.FONT_HERSHEY_SIMPLEX, thickness=1):
    """Calculate the appropriate font scale based on the text and available space."""
    font_scale = 1
    while True:
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        if text_size[0] <= max_width and text_size[1] <= max_height:
            break
        font_scale -= 0.1
        if font_scale <= 0.1:
            break
    return font_scale

def get_nearest_contour(contours, edge, image_shape):
    """Find the nearest contour to a given edge."""
    if not contours:
        return None, None
    nearest_contour = None
    min_distance = float('inf')
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if edge == 'left':
            distance = x
        elif edge == 'right':
            distance = image_shape[1] - (x + w)
        elif edge == 'top':
            distance = y
        elif edge == 'bottom':
            distance = image_shape[0] - (y + h)
        if distance < min_distance:
            min_distance = distance
            nearest_contour = cnt
    return nearest_contour, min_distance

def process_images(input_folder, output_folder):
    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_folder, filename)
            image = cv2.imread(image_path)

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                # Find nearest contours to each edge
                nearest_left, left_distance = get_nearest_contour(contours, 'left', image.shape)
                nearest_right, right_distance = get_nearest_contour(contours, 'right', image.shape)
                nearest_top, top_distance = get_nearest_contour(contours, 'top', image.shape)
                nearest_bottom, bottom_distance = get_nearest_contour(contours, 'bottom', image.shape)

                # Extract bounding boxes of the nearest contours
                x_left, y_left, w_left, h_left = cv2.boundingRect(nearest_left) if nearest_left is not None else (0, 0, 0, 0)
                x_right, y_right, w_right, h_right = cv2.boundingRect(nearest_right) if nearest_right is not None else (0, 0, 0, 0)
                x_top, y_top, w_top, h_top = cv2.boundingRect(nearest_top) if nearest_top is not None else (0, 0, 0, 0)
                x_bottom, y_bottom, w_bottom, h_bottom = cv2.boundingRect(nearest_bottom) if nearest_bottom is not None else (0, 0, 0, 0)

                # Determine the new image size with padding for the white zone
                padding = 100  # Adjust this for more or less space
                new_width = image.shape[1] + 2 * padding
                new_height = image.shape[0] + 2 * padding

                # Create a new image with a white background
                new_image = cv2.copyMakeBorder(image, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=(255, 255, 255))

                # Draw rectangles around the nearest objects
                if nearest_left is not None:
                    cv2.rectangle(new_image, (x_left + padding, y_left + padding), (x_left + w_left + padding, y_left + h_left + padding), (0, 0, 255), 2)
                if nearest_right is not None:
                    cv2.rectangle(new_image, (x_right + padding, y_right + padding), (x_right + w_right + padding, y_right + h_right + padding), (0, 0, 255), 2)
                if nearest_top is not None:
                    cv2.rectangle(new_image, (x_top + padding, y_top + padding), (x_top + w_top + padding, y_top + h_top + padding), (0, 0, 255), 2)
                if nearest_bottom is not None:
                    cv2.rectangle(new_image, (x_bottom + padding, y_bottom + padding), (x_bottom + w_bottom + padding, y_bottom + h_bottom + padding), (0, 0, 255), 2)

                # Draw lines from the shapes to the edges of the white zone
                if nearest_left is not None:
                    cv2.line(new_image, (x_left + padding, y_left + h_left // 2 + padding), (padding, y_left + h_left // 2 + padding), (0, 0, 255), 2)
                if nearest_right is not None:
                    cv2.line(new_image, (x_right + w_right + padding, y_right + h_right // 2 + padding), (new_width - padding, y_right + h_right // 2 + padding), (0, 0, 255), 2)
                if nearest_top is not None:
                    cv2.line(new_image, (x_top + w_top // 2 + padding, y_top + padding), (x_top + w_top // 2 + padding, padding), (0, 0, 255), 2)
                if nearest_bottom is not None:
                    cv2.line(new_image, (x_bottom + w_bottom // 2 + padding, y_bottom + h_bottom + padding), (x_bottom + w_bottom // 2 + padding, new_height - padding), (0, 0, 255), 2)

                # Prepare text for distances
                text_lines = [
                    f"Left: {left_distance}px" if nearest_left is not None else "Left: N/A",
                    f"Right: {right_distance}px" if nearest_right is not None else "Right: N/A",
                    f"Top: {top_distance}px" if nearest_top is not None else "Top: N/A",
                    f"Bottom: {bottom_distance}px" if nearest_bottom is not None else "Bottom: N/A"
                ]

                # Calculate font scale and text size
                text_max_width = padding - 10
                text_max_height = padding - 10
                font_scale = min(
                    calculate_font_scale(line, text_max_width, text_max_height, thickness=1)
                    for line in text_lines
                )
                font = cv2.FONT_HERSHEY_SIMPLEX
                thickness = 1  # Thinner for better readability

                # Add text in the white zone only, ensuring no overlap with the original image
                cv2.putText(new_image, text_lines[0], (padding // 4, y_left + h_left // 2 + padding + 10), font, font_scale, (42, 42, 165), thickness, cv2.LINE_AA)
                cv2.putText(new_image, text_lines[1], (new_width - text_max_width, y_right + h_right // 2 + padding + 10), font, font_scale, (42, 42, 165), thickness, cv2.LINE_AA)
                cv2.putText(new_image, text_lines[2], (x_top + w_top // 2 + padding, padding // 4), font, font_scale, (42, 42, 165), thickness, cv2.LINE_AA)
                cv2.putText(new_image, text_lines[3], (x_bottom + w_bottom // 2 + padding, new_height - padding // 4), font, font_scale, (42, 42, 165), thickness, cv2.LINE_AA)

            # Update the output file name to include "_result"
            output_filename = os.path.splitext(filename)[0] + '_result' + os.path.splitext(filename)[1]
            output_path = os.path.join(output_folder, output_filename)
            cv2.imwrite(output_path, new_image)

# Example usage
input_folder = '../data/input/images'  # Path to input images
output_folder = '../data/output/img_measure_object_to_edges_results'  # Path to output results
process_images(input_folder, output_folder)
