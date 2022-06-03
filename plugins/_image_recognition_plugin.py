#############################
# ======== IMPORTS ======== #
#############################

import json
import sys
from pathlib import Path as p

# ============================================== #
ABSDIR = p(__file__).parent.absolute()
sys.path.append(str(ABSDIR.joinpath("../src")))
# ============================================== #

from typing import Dict, List, NamedTuple, Tuple

import _rust_types as rt
import _stdlib as std
import _validators as val
import cv2
import numpy as np
import requests
from praw.models import Submission
from praw.reddit import Reddit

###############################
# ======== INSTANCES ======== #
###############################

configs = std.Configs(ABSDIR.joinpath("../config/plugins/image_recognition.json"))
logger = std.Logger(
    ABSDIR.joinpath("../logs/image.recognition.log"), "ImageRecognitionPlugin"
)

##########################
# ======== PATH ======== #
##########################

_hashes_path = ABSDIR.joinpath("../data/plugins/image_recognition/hashes.json")


###############################
# ======== CONSTANTS ======== #
###############################


# hashing constants
HASH_RES: Tuple[int, int] = tuple(
    configs.get("hashing", "resolution").expect(
        "Expected to find a resolution tuple under: 'hashing/resolution'!"
    )
)
THUMB_RES: Tuple[int, int] = tuple(
    configs.get("hashing", "thumbnail_resolution").expect(
        "Expected to find a resolution tuple under: 'hashing/thumbnail_resolution'!"
    )
)
HASH_SCHEMA = {
    "type": "array",
    "items": [
        {
            "type": "object",
            "properties": {"hash": {"type": "string"}, "path": {"type": "string"}},
            "required": ["hash", "path"],
            "additionalProperties": False,
        }
    ],
}

MAX_BIT_FLIPS = 0  # TODO: configure bit flips
AMBIGUOUS_BIT_FLIPS = range(0)
MAX_MATCHES = 0

# cv2 constants
FLANN_INDEX_KDTREE = configs.get("opencv", "flann_index_kdtree").unwrap()
TREES: int = configs.get("opencv", "trees").unwrap()
CHECKS: int = configs.get("opencv", "checks").unwrap()
FILTER: float = configs.get("opencv", "filter").unwrap()
CV2_SUPPORTED_TYPES = (
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
)

# networking constants
MAX_OCTETS: int = configs.get("networking", "max_octets").unwrap()


#############################
# ======== CLASSES ======== #
#############################


class FeatureMatcher:
    def __init__(self):
        self.__sift = cv2.SIFT_create()

        index_params = {"algorithm": FLANN_INDEX_KDTREE, "trees": TREES}
        search_params = {"checks": CHECKS}

        self.__flann = cv2.FlannBasedMatcher(index_params, search_params)

    def match(
        self, comp_img: cv2.Mat, train_img: cv2.Mat
    ) -> List[Tuple[cv2.DMatch, cv2.DMatch]]:
        _, des1 = self.__sift.detectAndCompute(comp_img, None)
        _, des2 = self.__sift.detectAndCompute(train_img, None)

        matches = self.__flann.knnMatch(des1, des2, k=2)

        return [m for m, n in matches if m.distance < FILTER * n.distance]


class StoredImageHash:
    def __init__(self, path: p, img_hash: str):
        self.path = path
        self.img_hash = img_hash

    @property
    def thumb(self) -> rt.Result[cv2.Mat]:
        try:
            return rt.Ok(cv2.imread(str(self.path), 0))
        except BaseException as e:
            return rt.Err(e)

    def __repr__(self) -> str:
        return f"StoredImageHash( hash={self.img_hash!r}, thumb=numpy.array({self.thumb}) )"


class CompImageHash:
    def __init__(self, img_hash: "str | int", thumb: cv2.Mat):
        self.img_hash = img_hash if isinstance(img_hash, int) else int(img_hash, base=0)
        self.thumb = thumb

    def __repr__(self):
        return f"CompImageHash( hash={self.img_hash!r}, thumb=numpy.array({self.thumb.shape}) )"

    @property
    def hash_bin(self) -> str:
        return bin(self.img_hash)[2:].zfill(HASH_RES[0] * HASH_RES[1])

    @property
    def hash_int(self) -> int:
        return self.img_hash

    def compare_hash(self, other: StoredImageHash):
        return sum(x != y for x, y in zip(self.hash_bin[2:], other.img_hash[2:]))

    def compare_thumb(self, other: StoredImageHash, matcher: FeatureMatcher):
        other_thumb = other.thumb

        if isinstance(other_thumb, rt.Ok):
            return matcher.match(self.thumb, other.thumb.unwrap())

        logger.critical(
            f"failed to load thumb from {other!r}: {other_thumb.err}"
        )  # XXX: !r calls repr()
        return []


class Hashes:
    def __init__(self, hashes_path: p = _hashes_path, schema=HASH_SCHEMA):
        """Create a helper object for managing Hashed images.

        Args:
            hashes_path (p, optional): The path to the hashes file. Defaults to _hashes_path.
            schema (object, optional): A schema object to validate against. Defaults to HASH_SCHEMA.
        """
        self.hashes_path = hashes_path
        self.schema = schema

    def get(self):
        """Get the hashes from the file.

        Returns:
            List[StoredImageHash]: The hashes as a list of StoredImageHash.
        """
        hashes: List[Dict[str, str]] = json.loads(self.hashes_path.read_text())

        if error := val.validate(hashes, self.schema):
            raise error

        return [StoredImageHash(p(hash_["path"]), hash_["hash"]) for hash_ in hashes]


#####################################
# ======== LOCAL INSTANCES ======== #
#####################################

sys.stderr = sys.stdout
matcher = FeatureMatcher()
hashes = Hashes()

###############################
# ======== FUNCTIONS ======== #
###############################


def hash_image(
    img_bytes: bytes,
) -> rt.Result[CompImageHash]:
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
        return rt.Err(e)

    hashable = cv2.resize(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), HASH_RES)
    thumb = cv2.resize(img, THUMB_RES)

    res = "0b"

    for row_idx, row in enumerate(hashable):
        use_row = 0 if row_idx == HASH_RES[1] - 1 else row_idx + 1
        for pixel_idx, pixel in enumerate(row):
            use_pixel = 0 if pixel_idx == HASH_RES[0] - 1 else pixel_idx + 1
            res += "1" if pixel < hashable[use_row][use_pixel] else "0"

    return rt.Ok(CompImageHash(res, thumb))


def is_supported_mimetype(mimetype: "str | None") -> bool:
    """Check if the given mimetype is valid for cv2.

    Args:
        mimetype (str | None): The mimetype to check. If None, return False.

    Returns:
        bool: If the mimetype is supported or not.
    """
    if mimetype is None:
        return False

    split = mimetype.split("/")

    return split[0] == "image" and split[1] in CV2_SUPPORTED_TYPES


def _request(url: str, result: List[bytes]):
    """Request the given url and append the response to the result list.

    Args:
        url (str): Url to request.
        result (List[bytes]): Result list to append to.
    """
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
        logger.critical(f'GET request for "%s" failed unexpectedly: %s' % (url, e))


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
    """Check if the given image is blacklisted."""
    img_hash = hash_image(img)

    if isinstance(img_hash, rt.Err):
        logger.error(f"failed to hash image: {img_hash.err}")
        return False

    img_hash = img_hash.unwrap()

    for stored_hash in hashes.get():
        flips = img_hash.compare_hash(stored_hash)

        if flips >= MAX_BIT_FLIPS:
            return True

        elif flips in AMBIGUOUS_BIT_FLIPS:
            if len(img_hash.compare_thumb(stored_hash, matcher)) >= MAX_BIT_FLIPS:
                return True

    return False


def remove_submission(submission: Submission, reddit: Reddit) -> None:
    for image in get_images_from_submission(submission):

        if is_image_blacklisted(image):
            logger.info(f"removing submission {submission.id}")
            submission.mod.remove()  # TODO: add default remove submission messages
            break


def main(_, **kwargs):
    reddit = std.gen_reddit_instance()

    submission: Submission = reddit.submission(str(kwargs["submission"]))

    images = get_images_from_submission(submission)

    if not len(images):
        return

    for image in images:
        if is_image_blacklisted(image):
            remove_submission(submission, reddit)
            return


# hash_ = hash_image(requests.get("https://i.redd.it/2iu0gi41rfu81.jpg").content)
# print(hash_)
# cv2.imshow("image", hash_[0].thumb)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
