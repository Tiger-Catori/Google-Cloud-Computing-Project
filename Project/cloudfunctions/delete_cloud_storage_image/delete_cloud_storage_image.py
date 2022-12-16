from google.cloud import storage


def delete_cloud_storage_image(request):

    bucketName = "video-game-products"

    # Connect to bucket
    storage_client = storage.Client.from_service_account_json(
        "Google_Service_Key.json")
    bucket = storage_client.get_bucket(bucketName)

    imageName = request.form['id'] + ".jpg"
    blob = bucket.blob(imageName)

    result = blob.delete()

    return "Successfully deleted image " + imageName
