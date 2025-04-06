import os
import math
import pygame
import itertools
import copy
from enum import Enum
from itertools import chain
from collections.abc import Iterable

from rotating_chess import settings


class Side(Enum):
    BLACK = 1
    WHITE = 2


class DistsAngle:
    """immutable. represents an angle and some points at given distances to that angle.

    >>> d = DistsAngle(range(4), math.pi / 4)
    >>> for x, y in d.get_offsets(0):
    ...     print(f"({x},{y})")
    ...
    (0.0,0.0)
    (0.707,0.707)
    (1.414,1.414)
    (2.121,2.121)

    >>> d = DistsAngle(itertools.count(step=1), math.pi / 8)
    >>> for x, y in d.get_offsets(0):
    ...     print(f"({x},{y})")
    ...     if abs(x) > 20 or abs(y) > 20:
    ...         break
    ...
    (0.0,0.0)
    (0.9238795325112867,0.3826834323650898)
    (1.8477590650225735,0.7653668647301796)
    (2.77163859753386,1.1480502970952693)
    ...
    (20.325349715248308,8.419035512031975)
    """

    def __init__(self, distances: Iterable[float], angle: float):
        """locs must be iterable, angle in radians"""
        self.__distances = distances
        self.__angle = angle

    def get_distances(self):
        return self.__distances

    def get_angle(self):
        return self.__angle

    def get_offsets(self, angle: float) -> Iterable[tuple[float, float]]:
        """angle in radians is the offset angle"""
        return (
            self.get_point(d, self.__angle, angle) for d in copy.copy(self.__distances)
        )

    def get_point(
        self, distance: float, base_angle: float, offset_angle: float
    ) -> tuple[float, float]:
        """angle in radians"""
        angle = base_angle - offset_angle
        return (distance * math.cos(angle), distance * math.sin(angle))


class Piece:
    def __init__(
        self,
        x: float,
        y: float,
        angle: float,
        side: Side,
        img: pygame.Surface | None,
        piece_name: str,  # TODO MAKE THIS A ENUM?
    ):
        # TODO: maybe add a self.headless: bool to check if we're in testing to avoid weird inscrutable Nones?
        # coordinates represent the CENTER of the piece.
        self.__x = x
        self.__y = y
        # angle is in radians
        self.__angle = angle
        self.__preview_angle: float | None = None
        self.__side = side
        self.selected = False
        self.__default_image = img
        self.__actual_image = (
            None if img is None else pygame.transform.rotate(img, math.degrees(angle))
        )
        self.__preview_image: pygame.Surface | None = None
        self.__piece_name: str = piece_name

        self.__nonpreview_blit_coords: tuple[int, int]
        if img is not None:
            self.__set_nonpreview_blit_rect()

        # the DAs calculate relative angle; they get self.__angle passed in.
        # the points are only used when only one piece is selected.
        # they are updated using the DAs on init and when we confirm a preview angle (ie update our angle)
        self.can_jump = False
        self.__capture_DAs: list[DistsAngle] = []
        self.__move_DAs: list[DistsAngle] = []
        self.__capture_points: list[tuple[float, float]] = []
        self.__preview_capture_points: list[tuple[float, float]] | None = None
        self.__move_points: list[tuple[float, float]] = []
        self.__preview_move_points: list[tuple[float, float]] | None = None
        self.__init()

    def __str__(self):
        return f"Piece(x={self.__x}, y={self.__y}, side={self.__side})"

    def to_JSON_dict(self):
        return {
            "x": self.__x,
            "y": self.__y,
            "angle": self.__angle,
            "side": self.__side.value,
            "piece_name": self.__piece_name,
        }

    def __set_nonpreview_blit_rect(self):
        """creates coords (from a rect) that is used to blit the current image whenever we are not in rotation preview mode"""
        assert self.__actual_image is not None
        self.__nonpreview_blit_coords = self.__actual_image.get_rect(
            center=(self.__x, self.__y)
        ).topleft

    def coord_collides(self, x: float, y: float) -> bool:
        return (
            (x - self.__x) ** 2 + (y - self.__y) ** 2
        ) < settings.HITCIRCLE_RADIUS**2

    def piece_collides(self, x: float, y: float) -> bool:
        return ((x - self.__x) ** 2 + (y - self.__y) ** 2) < (
            settings.HITCIRCLE_RADIUS * 2
        ) ** 2

    def get_x(self) -> float:
        return self.__x

    def get_y(self) -> float:
        return self.__y

    def get_angle(self) -> float:
        return self.__angle

    def get_side(self) -> Side:
        return self.__side

    def get_piece_name(self) -> str:
        return self.__piece_name

    def should_promote(self) -> bool:
        # board height is 400px, tile height is 50
        if self.__piece_name != "pawn":
            return False

        if self.__side == Side.BLACK:
            return self.__y + settings.HITCIRCLE_RADIUS > 350
        if self.__side == Side.WHITE:
            return self.__y - settings.HITCIRCLE_RADIUS < 50

        return False

    def move(self, x: float, y: float):
        """
        strictly just moves self to x,y and updates self invariants.
        doesn't even check for promotion---should be done in Pieces.move().
        """
        debug = os.environ.get("DEBUG_ROTCHESS", "False")
        if debug is not None and debug == "True":
            print(
                f"moving {self.__piece_name} xy {self.__x}, {self.__y} to xy {x}, {y}"
            )

        self.__x = x
        self.__y = y

        if self.__actual_image is not None:
            self.update_capture_points()
            self.update_move_points()
            self.__set_nonpreview_blit_rect()

    def get_movable_points(self) -> list[tuple[float, float]]:
        return self.__capture_points + self.__move_points

    def __init_capture_points(self):
        self.__capture_points = []
        self.__capture_points.clear()

        angle = self.__angle
        if self.__preview_angle is not None:
            angle = self.__preview_angle

        for cap_DA in self.__capture_DAs:
            for x, y in cap_DA.get_offsets(angle):
                point = (x + self.__x, y + self.__y)
                if not self.should_draw_point(point[0], point[1]):
                    break

                self.__capture_points.append(point)

    def update_capture_points(self):
        cap_points = self.__capture_points
        if self.__preview_capture_points is not None:
            cap_points = self.__preview_capture_points

        cap_points.clear()

        angle = self.__angle
        if self.__preview_angle is not None:
            angle = self.__preview_angle

        for cap_DA in self.__capture_DAs:
            for x, y in cap_DA.get_offsets(angle):
                point = (x + self.__x, y + self.__y)
                if not self.should_draw_point(point[0], point[1]):
                    break

                cap_points.append(point)

    def __init_move_points(self):
        self.__move_points = []
        self.__move_points.clear()

        for move_DA in self.__move_DAs:
            for x, y in move_DA.get_offsets(self.__angle):
                point = (x + self.__x, y + self.__y)
                if not self.should_draw_point(point[0], point[1]):
                    break

                self.__move_points.append(point)

    def update_move_points(self):
        move_points = self.__move_points
        if self.__preview_move_points is not None:
            move_points = self.__preview_move_points
        move_points.clear()

        angle = self.__angle
        if self.__preview_angle is not None:
            angle = self.__preview_angle

        for move_DA in self.__move_DAs:
            for x, y in move_DA.get_offsets(angle):
                point = (x + self.__x, y + self.__y)
                if not self.should_draw_point(point[0], point[1]):
                    break

                move_points.append(point)

    def draw(self, screen: pygame.Surface):
        if self.selected:
            pygame.draw.circle(
                screen,
                settings.SELECTED_PIECE_COLOR,
                (self.__x, self.__y),
                settings.HITCIRCLE_RADIUS,
            )

        if self.__preview_angle is None and self.__preview_image is None:
            assert self.__actual_image is not None
            screen.blit(self.__actual_image, self.__nonpreview_blit_coords)
        else:
            assert self.__preview_image is not None
            assert self.__actual_image is not None
            pos_rect = self.__preview_image.get_rect(
                center=self.__actual_image.get_rect(center=(self.__x, self.__y)).center
            )
            screen.blit(self.__preview_image, pos_rect)

    def draw_hitcircle(self, screen: pygame.Surface):
        pygame.draw.circle(
            screen,
            settings.HITCIRCLE_COLOR,
            (self.__x, self.__y),
            settings.HITCIRCLE_RADIUS,
            width=1,
        )

    def draw_capture_points(self, screen: pygame.Surface):
        points = self.__capture_points
        if self.__preview_capture_points is not None:
            points = self.__preview_capture_points

        for point in points:
            pygame.draw.circle(
                screen,
                settings.CAPTURE_POINT_COLOR,
                point,
                settings.HITCIRCLE_RADIUS,
                width=1,
            )

    def draw_move_points(self, screen: pygame.Surface):
        points = self.__move_points
        if self.__preview_move_points is not None:
            points = self.__preview_move_points

        for point in points:
            pygame.draw.circle(
                screen,
                settings.MOVE_POINT_COLOR,
                point,
                settings.HITCIRCLE_RADIUS,
                width=1,
            )

    def draw_guide_lines(self, screen: pygame.Surface):
        # v_hat is a "unit vector", with the unit length being the hitcircle radius.
        v_hat = pygame.math.Vector2(settings.HITCIRCLE_RADIUS, 0)
        for da in chain(self.__capture_DAs, self.__move_DAs):
            # v_angle should be the angle the d.a. is pointing in.
            v_angle = v_hat.rotate_rad(
                (2 * math.pi)
                - (
                    self.__angle
                    if self.__preview_angle is None
                    else self.__preview_angle
                )
                * 1
            ).rotate_rad(da.get_angle())
            v_offset = v_angle.rotate(90)
            center = pygame.math.Vector2(self.__x, self.__y)
            point: pygame.math.Vector2
            for x, y in da.get_offsets(
                self.__angle if self.__preview_angle is None else self.__preview_angle
            ):
                point = (
                    pygame.math.Vector2(x, y) + center
                )  # point is a point the piece can move to
                # center = point
                if abs(x) > 1000 or abs(y) > 1000:
                    break
            # draw from center to the furthest points
            pygame.draw.line(
                screen, (255, 255, 255), center + v_offset, point + v_offset
            )
            pygame.draw.line(
                screen, (255, 255, 255), center - v_offset, point - v_offset
            )

    def should_draw_point(self, x: float, y: float) -> bool:
        BOARD_SIZE = 50 * 8
        MARGIN = settings.HITCIRCLE_RADIUS
        if (
            x < 0 - MARGIN
            or x > BOARD_SIZE + MARGIN
            or y < 0 - MARGIN
            or y > BOARD_SIZE + MARGIN
        ):
            return False
        return True

    def set_preview_angle(self, angle: float):
        """angle as radians"""
        assert self.__default_image is not None
        self.__preview_angle = angle
        self.__preview_image = pygame.transform.rotate(
            self.__default_image, math.degrees(angle)
        )
        if self.__preview_move_points is None and self.__preview_capture_points is None:
            self.__preview_move_points = []
            self.__preview_capture_points = []

    def confirm_preview(self):
        assert self.__preview_angle is not None and self.__preview_image is not None

        print(
            f"rotating {self.get_x()},{self.get_y()}{self.__piece_name} {self.__angle}rad to {self.__preview_angle}rad"
        )

        self.__actual_image = self.__preview_image
        self.__preview_image = None

        self.__angle = self.__preview_angle
        self.__preview_angle = None

        assert self.__preview_move_points is not None
        assert self.__preview_capture_points is not None
        self.__move_points = self.__preview_move_points
        self.__preview_move_points = None
        self.__capture_points = self.__preview_capture_points
        self.__preview_capture_points = None

        self.__set_nonpreview_blit_rect()

    def stop_previewing(self):
        self.__preview_angle = None
        self.__preview_image = None
        self.__preview_move_points = None
        self.__preview_capture_points = None

        self.__set_nonpreview_blit_rect()

    def __init(self):
        self.__init_movement()
        self.__init_capture_points()
        self.__init_move_points()

    def __init_movement(self):
        """initializes DAs and changes whether the piece can jump from the default"""
        if self.__piece_name == "pawn":
            self.can_jump = True
            self.__move_DAs.append(
                DistsAngle(
                    [50, 100],
                    angle=math.pi / -2,
                )
            )
            self.__capture_DAs.append(
                DistsAngle(
                    [50 * math.sqrt(2)],
                    angle=3 * math.pi / -4,
                )
            )
            self.__capture_DAs.append(
                DistsAngle(
                    [50 * math.sqrt(2)],
                    angle=math.pi / -4,
                )
            )
        elif self.__piece_name == "rook":
            self.include_level_DAs()
        elif self.__piece_name == "knight":
            self.can_jump = True

            for rad in [
                0.4636476090008061,
                -0.4636476090008061,
                -1.1071487177940904,
                -2.0344439357957027,
                -2.677945044588987,
                2.677945044588987,
                2.0344439357957027,
                1.1071487177940904,
            ]:
                self.__capture_DAs.append(
                    DistsAngle(
                        [math.sqrt(50**2 + 100**2)],
                        angle=rad,
                    )
                )
            self.__move_DAs = self.__capture_DAs
        elif self.__piece_name == "bishop":
            self.include_diagonal_DAs()
        elif self.__piece_name == "queen":
            self.include_level_DAs()
            self.include_diagonal_DAs()
        elif self.__piece_name == "king":
            self.can_jump = True
            for rad in [math.pi / -2, 0, math.pi / 2, math.pi, 3 * math.pi / 2]:
                self.__capture_DAs.append(
                    DistsAngle(
                        [50],
                        angle=rad,
                    )
                )
            for rad in [math.pi / -2, 0, math.pi / 2, math.pi, 3 * math.pi / 2]:
                rad = rad + math.pi / 4
                self.__capture_DAs.append(
                    DistsAngle(
                        [math.sqrt(50**2 + 50**2)],
                        angle=rad,
                    )
                )
            self.__move_DAs = self.__capture_DAs
        else:
            raise Exception(
                f"no distances angle mapping found for piece name: {self.__piece_name}"
            )

    def include_diagonal_DAs(self):
        """appends the base moveset for a bishop to self's DistsAngles"""
        self.__capture_DAs.append(
            DistsAngle(
                itertools.count(start=50 * math.sqrt(2), step=50 * math.sqrt(2)),
                angle=math.pi / 4,
            )
        )
        self.__capture_DAs.append(
            DistsAngle(
                itertools.count(start=-50 * math.sqrt(2), step=-50 * math.sqrt(2)),
                angle=math.pi / 4,
            )
        )
        self.__capture_DAs.append(
            DistsAngle(
                itertools.count(start=50 * math.sqrt(2), step=50 * math.sqrt(2)),
                angle=math.pi / -4,
            )
        )
        self.__capture_DAs.append(
            DistsAngle(
                itertools.count(start=-50 * math.sqrt(2), step=-50 * math.sqrt(2)),
                angle=math.pi / -4,
            )
        )
        self.__move_DAs = self.__capture_DAs

    def include_level_DAs(self):
        """appends the base moveset for a rook to self's DistsAngles"""
        self.__capture_DAs.append(
            DistsAngle(itertools.count(start=50, step=50), angle=0)
        )
        self.__capture_DAs.append(
            DistsAngle(itertools.count(start=-50, step=-50), angle=0)
        )
        self.__capture_DAs.append(
            DistsAngle(itertools.count(start=50, step=50), angle=math.pi / 2)
        )
        self.__capture_DAs.append(
            DistsAngle(itertools.count(start=-50, step=-50), angle=math.pi / 2)
        )
        self.__move_DAs = self.__capture_DAs


if __name__ == "__main__":
    d = DistsAngle(range(4), math.pi / 4)
    # d = DistsAngle(itertools.count(step=1), math.pi / 8)
    for x, y in d.get_offsets(0):
        print(f"({x},{y})")
        if abs(x) > 20 or abs(y) > 20:
            break
