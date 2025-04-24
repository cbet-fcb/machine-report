import cv2
import os
import concurrent.futures

def load_and_downscale(image_path, scale=0.5):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at {image_path}")
    return cv2.resize(image, (0, 0), fx=scale, fy=scale)

def enhance_contrast(image, contrast=1.5, brightness=0):
    return cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)

def load_super_resolution_model(model_path="EDSR_x3.pb", model_name="edsr", scale=3):
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel(model_path)
    sr.setModel(model_name, scale)
    return sr

def upscale_image(sr_model, image):
    return sr_model.upsample(image)

def invert_image(image):
    return cv2.bitwise_not(image)

def save_image(image, output_path):
    cv2.imwrite(output_path, image)

def crop_receipt(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return image

    # Combine all contours into one bounding box
    x_min, y_min, x_max, y_max = float('inf'), float('inf'), 0, 0

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        x_max = max(x_max, x + w)
        y_max = max(y_max, y + h)

    cropped = image[y_min:y_max, x_min:x_max]
    return cropped

# Main pipeline
def preprocess_image(input_path, output_path):
    downscaled = load_and_downscale(input_path)
    contrasted = enhance_contrast(downscaled)
    # sr_model = load_super_resolution_model()
    # upscaled = upscale_image(sr_model, contrasted)
    inverted = invert_image(contrasted)

    save_image(inverted, output_path) 

def process_batched_preprocessing(image_paths, prep_dir):
    """
    Preprocess a list of images in parallel and save them into prep_dir.
    Returns a list of output paths (one‐to‐one with image_paths order is not guaranteed).
    """
    os.makedirs(prep_dir, exist_ok=True)
    processed_paths = []

    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Submit all preprocessing jobs, mapping futures back to their output path
        future_to_out = {}
        for img_path in image_paths:
            filename = os.path.basename(img_path)
            out_path = os.path.join(prep_dir, filename)
            future = executor.submit(preprocess_image, img_path, out_path)
            future_to_out[future] = out_path

        # As each finishes, collect its output path
        for future in concurrent.futures.as_completed(future_to_out):
            # If you want to catch preprocessing exceptions:
            try:
                future.result()
                processed_paths.append(future_to_out[future])
            except Exception as e:
                # handle/log error, decide whether to append original or skip
                print(f"Preprocessing failed for {future_to_out[future]}: {e}")

    return processed_paths

# Example usage
if __name__ == "__main__":
    preprocess_image("data/test37Successful.jpg", "images/upscaled.jpg")
