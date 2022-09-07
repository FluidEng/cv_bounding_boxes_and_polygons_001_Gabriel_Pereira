import math
from typing import List

# Lens constants assuming a 1080p image
f = 714.285714
center = [960, 540]
# FOV angle
D = 1.082984  # For image-1, switch to 0.871413 for image-2


def cartesian2sphere(pt):
    x = (pt[0] - center[0]) / f
    y = (pt[1] - center[1]) / f

    r = math.sqrt(x*x + y*y)
    if r != 0:
        x /= r
        y /= r
    r *= D
    sin_theta = math.sin(r)
    x *= sin_theta
    y *= sin_theta
    z = math.cos(r)

    return [x, y, z]


def sphere2cartesian(pt):
    r = math.acos(pt[2])
    r /= D
    if pt[2] != 1:
        r /= math.sqrt(1 - pt[2] * pt[2])
    x = r * pt[0] * f + center[0]
    y = r * pt[1] * f + center[1]
    return [x, y]


def convert_point(point: List[int]) -> List[int]:
    """Convert single points between Cartesian and spherical coordinate systems"""
    if len(point) == 2:
        return cartesian2sphere(point)
    elif len(point) == 3:
        return sphere2cartesian(point)
    else:
        raise ValueError(f'Expected point to be 2 or 3D, got {len(point)} dimensions')

class Point2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.point = [x, y]
    def __getitem__(self, idx):
        return self.point[idx]
    def __len__(self):
        return len(self.point)
    def __str__(self) -> str:
        return str(self.point)

class Point3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.point = [x, y, z]
    def __getitem__(self, idx):
        return self.point[idx]
    def __len__(self):
        return len(self.point)
    def __str__(self) -> str:
        return str(self.point)

class CartesianBbox:
    def __init__(self, points: List[Point2D], fmt: str):
        """
            points -> List[Tuple(int, int)]:
                A list of 2D points
            fmt:
                xyxy:
                    means that the coordinates the first point in the list represents the top left corner of the image
                    and the second point in the list represents the bottom right corner of the image.
                xywh:
                    First point in the list represents the top left corner of the image and the second pair of 
                    values (wh) represents width and height of the image respectively.
                cxcywh:
                    First point in the list represents central point of the image and the second point in the list
                    represents the width and height of the image respectively.                    
        """
        assert fmt in ['xyxy', 'xywh', 'cxcywh'], 'Invalid bbox format'
        assert len(points) >= 2, 'Invalid number of points, cartesian bbox must have at least 2 2D points'
        assert len(points) % 2 == 0, 'the number of points must be pair'
        self.points = points
        self.fmt = fmt

    def get_points_as_xyxy(self) -> List[Point2D]:
        points = self.points
        if self.fmt == 'xywh':
            points = []
            for idx in range(0, 2, len(self.points)):
                pt1 = self.points[idx]
                pt2 = self.points[idx+1]
                points = [*points, *self._from_xywh_to_xyxy([pt1, pt2])]
        if self.fmt == 'cxcywh':
            points = []
            for idx in range(0, 2, len(self.points)):
                pt1 = self.points[idx] #Point2D
                pt2 = self.points[idx+1] #Point2D
                points = [*points, *self._from_cxcywh_to_xyxy([pt1, pt2])]
        return points

    def _from_xywh_to_xyxy(self, points):
        x1, y1 = points[0]
        w, h = points[1]
        x2 = x1 + w
        y2 = y1 + h
        return [Point2D(x1, y1), Point2D(x2, y2)]
   
    def _from_cxcywh_to_xyxy(self, points):
        cx, cy = points[0]
        w, h = points[1]
        x1 = cx - w//2
        y1 = cy - h//2
        x2 = x1 + w
        y2 = y1 + h
        return [Point2D(x1, y1), Point2D(x2, y2)]

    def __str__(self):
        return str(self.points)


class SphericalBbox:
    def __init__(self, points: List[Point3D]):
        # points is a list of spehrical coordinates
        # format is 'xyzxyz' only for now
        assert len(points) >= 2, 'Invalid number of points, cartesian bbox must have at least 2 3D points'
        assert len(points) % 2 == 0, 'the number of points must be pair'
        self.points = points
    def __str__(self):
        return str(self.points)

def bbox_to_spherical(cartesian: CartesianBbox) -> SphericalBbox:
    spherical_points = []
    # cartesian_point format should have to be in xyxy format
    cartesian_points = cartesian.get_points_as_xyxy()
    for cartesian_point in cartesian_points:
        spherical_point = convert_point(cartesian_point)
        spherical_points.append(spherical_point)
    return SphericalBbox(spherical_points)


if __name__ == '__main__':
    cartesian_points = [Point2D(3,5), Point2D(7,10), Point2D(7,10), Point2D(7,10)]
    spherical_points = [Point3D(3,5,10), Point3D(7,10,20)]

    cart_bbox = CartesianBbox(cartesian_points, fmt='cxcywh')
    spher_bbox= SphericalBbox(spherical_points)

    print(bbox_to_spherical(cart_bbox))