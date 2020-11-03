#!/usr/bin/env python

import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url


def main():
    cloudinary.config(
        cloud_name="dijpr9qcs",
        api_key="867126563973785",
        api_secret="tvtXgGn_OL2RzA1YxScf3nwxpPE"
    )

    DEFAULT_TAG = "python_sample_basic"

    print("--- Upload a local file")
    response = upload("missingimage.png", tags=DEFAULT_TAG)
    url, options = cloudinary_url(
        response['public_id'],
        format=response['format'],
    )
    print(url)


if __name__ == '__main__':
    main()
