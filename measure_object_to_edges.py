import cv2
import os

def calculate_font_scale(text, max_width, max_height, font=cv2.FONT_HERSHEY_SIMPLEX, thickness=2):
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
                contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(contour)

                # Determine the new image size with padding for the pink zone
                padding = 100  # Adjust this for more or less space
                new_width = image.shape[1] + 2 * padding
                new_height = image.shape[0] + 2 * padding

                # Create a new image with a pink background
                new_image = cv2.copyMakeBorder(image, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=(255, 192, 203))

                # Draw the shape (rectangle) around the object
                cv2.rectangle(new_image, (x + padding, y + padding), (x + w + padding, y + h + padding), (0, 255, 0), 2)

                # Calculate distances from the object to the edges of the original image
                left_distance = x
                right_distance = image.shape[1] - (x + w)
                top_distance = y
                bottom_distance = image.shape[0] - (y + h)

                # Draw lines from the shape to the edges of the pink zone
                cv2.line(new_image, (x + padding, y + h // 2 + padding), (padding, y + h // 2 + padding), (0, 255, 0), 2)  # Line to left edge
                cv2.line(new_image, (x + w + padding, y + h // 2 + padding), (new_width - padding, y + h // 2 + padding), (0, 255, 0), 2)  # Line to right edge
                cv2.line(new_image, (x + w // 2 + padding, y + padding), (x + w // 2 + padding, padding), (0, 255, 0), 2)  # Line to top edge
                cv2.line(new_image, (x + w // 2 + padding, y + h + padding), (x + w // 2 + padding, new_height - padding), (0, 255, 0), 2)  # Line to bottom edge

                # Prepare text for distances
                text_lines = [
                    f"{left_distance}px",
                    f"{right_distance}px",
                    f"{top_distance}px",
                    f"{bottom_distance}px"
                ]

                # Calculate font scale and text size
                text_max_width = padding - 10
                text_max_height = padding - 10
                font_scale = min(
                    calculate_font_scale(line, text_max_width, text_max_height)
                    for line in text_lines
                )
                font = cv2.FONT_HERSHEY_SIMPLEX
                thickness = 2  # Thicker for better visibility

                # Add text in the pink zone only, ensuring no overlap with the original image
                cv2.putText(new_image, text_lines[0], (padding // 4, y + h // 2 + padding + 10), font, font_scale, (42, 42, 165), thickness, cv2.LINE_AA)
                cv2.putText(new_image, text_lines[1], (new_width - text_max_width, y + h // 2 + padding + 10), font, font_scale, (42, 42, 165), thickness, cv2.LINE_AA)
                cv2.putText(new_image, text_lines[2], (x + w // 2 + padding, padding // 4), font, font_scale, (42, 42, 165), thickness, cv2.LINE_AA)
                cv2.putText(new_image, text_lines[3], (x + w // 2 + padding, new_height - padding // 4), font, font_scale, (42, 42, 165), thickness, cv2.LINE_AA)

            output_path = os.path.join(output_folder, filename)
            cv2.imwrite(output_path, new_image)

# Example usage
input_folder = 'path/images'  # Update this to your input folder path
output_folder = 'path/image_results'  # Update this to your output folder path
process_images(input_folder, output_folder)
