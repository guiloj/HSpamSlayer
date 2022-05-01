#############################
# ======== IMPORTS ======== #
#############################

import sys
from pathlib import Path as p

# ============================================== #
ABSDIR = p(__file__).parent.absolute()
sys.path.append(str(ABSDIR.joinpath("../src")))
# ============================================== #

from typing import List, NamedTuple, Tuple

import cv2
import numpy as np
import requests
from _stdlib import Logger, gen_reddit_instance
from praw.models import Submission
from praw.reddit import Reddit

###############################
# ======== CONSTANTS ======== #
###############################


# hashing constants
HASH_RES = (6, 7)
THUMB_RES = (200, 200)

# cv2 constants
FLANN_INDEX_KDTREE = 0
TREES = 5
CHECKS = 50

# networking constants
MAX_OCTETS = 10000000


#############################
# ======== CLASSES ======== #
#############################


class FeatureMatcher:
    def __init__(self):
        self.sift = cv2.SIFT_create()

        index_params = {"algorithm": FLANN_INDEX_KDTREE, "trees": TREES}
        search_params = {"checks": CHECKS}

        self.flann = cv2.FlannBasedMatcher(index_params, search_params)

    def match(
        self, comp_img: cv2.Mat, train_img: cv2.Mat
    ) -> List[Tuple[cv2.DMatch, cv2.DMatch]]:
        _, des1 = self.sift.detectAndCompute(comp_img, None)
        _, des2 = self.sift.detectAndCompute(train_img, None)

        matches = self.flann.knnMatch(des1, des2, k=2)

        return [m for m, n in matches if m.distance < 0.7 * n.distance]


class StoredImageHash:
    def __init__(self, path: p):
        self.path = path
        self.hash = int(self.path.name.split(".")[0])

    @property
    def thumb(self) -> cv2.Mat:
        return cv2.imread(str(self.path), 0)

    @property
    def hash_bin(self) -> str:
        return bin(self.hash)[2:].zfill(HASH_RES[0] * HASH_RES[1])

    @property
    def hash_int(self) -> int:
        return self.hash


class CompImageHash:
    def __init__(self, hash_: "str | int", thumb: cv2.Mat):
        self.hash = hash_ if isinstance(hash_, int) else int(hash_, base=0)
        self.thumb = thumb

    def __str__(self):
        return (
            f"CompImageHash( hash={self.hash}, thumb=numpy.array({self.thumb.shape}) )"
        )

    @property
    def hash_bin(self) -> str:
        return bin(self.hash)[2:].zfill(HASH_RES[0] * HASH_RES[1])

    @property
    def hash_int(self) -> int:
        return self.hash

    def compare_hash(self, other: StoredImageHash):
        return sum(x != y for x, y in zip(self.hash_bin[2:], other.hash_bin[2:]))

    def compare_thumb(self, other: StoredImageHash, matcher: FeatureMatcher):
        return matcher.match(self.thumb, other.thumb)


###########################
# ======== TYPES ======== #
###########################


Hash = NamedTuple("Hash", result="CompImageHash | None", error="BaseException | None")


###############################
# ======== INSTANCES ======== #
###############################

sys.stderr = sys.stdout
matcher = FeatureMatcher()
logger = Logger(
    ABSDIR.joinpath("../logs/image.recognition.log"), "ImageRecognitionPlugin"
)

###############################
# ======== FUNCTIONS ======== #
###############################


def hash_image(
    img_bytes: bytes,
) -> Hash:
    """Hash, create a thumbnail from the given image bytes and return it as a new CompImageHash object.

    Args:
        img_bytes (bytes): The image bytes to hash.

    Returns:
        NamedTuple["Hash", None | CompImageHash, None | BaseException]: The CompImageHash object or an exception.
    """
    try:
        img = np.asarray(bytearray(img_bytes), dtype="uint8")
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    except BaseException as e:
        return Hash(None, e)

    hashable = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), HASH_RES)
    thumb = cv2.resize(img, THUMB_RES)

    res = "0b"

    for row_idx, row in enumerate(hashable):
        use_row = 0 if row_idx == HASH_RES[1] - 1 else row_idx + 1
        for pixel_idx, pixel in enumerate(row):
            use_pixel = 0 if pixel_idx == HASH_RES[0] - 1 else pixel_idx + 1
            res += "1" if pixel < hashable[use_row][use_pixel] else "0"

    return Hash(CompImageHash(res, thumb), None)


def is_supported_mimetype(mimetype: "str | None") -> bool:
    """Check if the given mimetype is valid for cv2.

    Args:
        mimetype (str | None): The mimetype to check.

    Returns:
        bool: If the mimetype is supported or not.
    """
    if mimetype is None:
        return False

    split = mimetype.split("/")

    return split[0] == "image" and split[1] in [
        "bmp",
        "dib",
        "jpeg",
        "jpg",
        "jpe",
        "jp2",
        "png",
        "pbm",
        "pgm",
        "ppm",
        "sr",
        "ras",
        "tiff",
        "tif",
    ]


def _request(url: str, result: List[bytes]):
    try:
        headers = requests.head(url).headers

        if not is_supported_mimetype(headers.get("Content-Type")):
            return

        if int(headers.get("Content-Length", MAX_OCTETS + 1)) > MAX_OCTETS:
            return

        result.append(requests.get(url).content)

    except requests.exceptions.RequestException as e:
        logger.error(f'GET request for "%s" failed: %s' % (url, e))

    except BaseException as e:
        logger.error(f'GET request for "%s" failed unexpectedly: %s' % (url, e))


def get_images_from_submission(submission: Submission) -> "List[bytes]":
    """Get all image's byte data from a given submission.

    Args:
        submission (Submission): The submission to get the images from.

    Returns:
        List[bytes]: List of all image's byte data.
    """
    result = []
    if submission.is_self:
        return result  # text submission

    elif hasattr(submission, "is_gallery"):
        for value in submission.media_metadata.values():

            url = value["s"]["u"].split("?")[0].replace("preview", "i")

            _request(url, result)

    else:
        _request(submission.url, result)

    return result


def is_image_blacklisted(img: bytes) -> bool:
    return False


def remove_submission(submission: Submission, reddit: Reddit) -> None:
    pass


def main(_, **kwargs):
    reddit = gen_reddit_instance()

    submission: Submission = reddit.submission(str(kwargs["submission"]))

    images = get_images_from_submission(submission)

    if not len(images):
        return

    for image in images:
        if is_image_blacklisted(image):
            remove_submission(submission, reddit)


# hash_ = hash_image(requests.get("https://i.redd.it/2iu0gi41rfu81.jpg").content)
# print(hash_)
# cv2.imshow("image", hash_[0].thumb)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
