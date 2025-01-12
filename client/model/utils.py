from __future__ import annotations

import abc
import functools
import math
from typing import Any, Generator, Iterable, List, Optional, Tuple, TypeVar

from . import objects

from .. import xml_

T = TypeVar('T')

class IPositionable(abc.ABC):
    """ Any object that has the 'position' attribute """

    @property
    @abc.abstractmethod
    def position(self) -> Vector:
        """ Object position """
        ...

    @classmethod
    def __subclasshook__(cls, C):
        if cls is IPositionable and 'position' in C.__dict__:
            return True
        return NotImplemented

@xml_.XMLInclude
class Vector(xml_.SupportsXML, IPositionable):
    """ 3D Vector class """
    def __init__(self,
        x: float = 0, y: float = 0, z: float = 0,
        is_height_defined: bool = True
    ):
        """ Creates new vector given all 3 coords """
        self._x = x
        self._y = y
        self._z = z
        self.is_height_defined = is_height_defined

    @property
    def position(self) -> Vector:
        """ Returns itself """
        return self

    @property
    def x(self) -> float:
        """ X cooord """
        return self._x

    @x.setter
    def x(self, x: float):
        self._x = x

    @property
    def y(self) -> float:
        """ Y cooord (height) """
        if self.is_height_defined:
            return self._y
        return 0

    @y.setter
    def y(self, y: float):
        self._y = y

    @property
    def z(self) -> float:
        """ Z cooord """
        return self._z

    @z.setter
    def z(self, z: float):
        self._z = z

    @classmethod
    def vector_xz(cls, x: float, z: float):
        """ Creates new vector given the X and Z coord """
        ret = super().__new__(cls)
        ret.__init__(x=x, z=z, is_height_defined=False)
        return ret

    def __eq__(self, o: 'Vector') -> bool:
        return self.x == o.x \
            and self.y == o.y \
            and self.z == o.z \
            and self.is_height_defined == o.is_height_defined

    def __hash__(self) -> int:
        ret = -393058493
        magic = -1521134295
        ret = ret * magic + hash(self.x)
        ret = ret * magic + hash(self.y)
        ret = ret * magic + hash(self.z)
        ret = ret * magic + hash(self.is_height_defined)
        return ret

    def __add__(self, o: 'Vector') -> 'Vector':
        return Vector(
            self.x + o.x, self.y + o.y, self.z + o.z,
            self.is_height_defined and o.is_height_defined
        )

    def __sub__(self, o: 'Vector') -> 'Vector':
        return Vector(
            self.x - o.x, self.y - o.y, self.z - o.z,
            self.is_height_defined and o.is_height_defined
        )

    def __mul__(self, o: float) -> 'Vector':
        return Vector(
            self.x * o, self.y * o, self.z * o,
            self.is_height_defined
        )

    def __rmul__(self, o: float) -> 'Vector':
        return self * o

    def __truediv__(self, o: float) -> 'Vector':
        return Vector(
            self.x / o, self.y / o, self.z / o,
            self.is_height_defined
        )

    def __abs__(self) -> float:
        """ Vector length """
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

    def __str__(self) -> str:
        if self.is_height_defined:
            return '({0.x:.2f}, {0.y:.2f}, {0.z:.2f})'.format(self)
        return '({0.x:.2f}, undefined, {0.z:.2f})'.format(self)

    def __repr__(self) -> str:
        return f'<Vector(x={self.x:.2f}, y={self.y:.2f}, z={self.z:.2f}, ' \
            f'is_height_defined={self.is_height_defined})>'

    @classmethod
    @property
    def zero(cls):
        """ Returns zero vector """
        return Vector(0, 0, 0)

    def flat_angle(self, o: Optional['Vector']):
        """
        Returns angle in XZ plane. If 'other' vector is null,returns angle with the X axis
        """
        if o is None:
            o = Vector.vector_xz(1, 0)
        
        sin = self.x * o.z - o.x * self.z
        cos = self.x * o.x + o.z * self.z
        angle = math.pi - math.atan2(sin, cos)
        return angle if angle > 0 else angle + 2 * math.pi

    def flat_rotate(self, angle: float, pivot: Optional['Vector'] = None) -> 'Vector':
        """ Rotates vector in XZ plane """
        if pivot is None:
            pivot = self.zero
        diff = self - pivot

        sin = math.sin(angle)
        cos = math.cos(angle)

        return pivot + Vector(
            diff.x * cos - diff.z * sin, 0, diff.x * sin + diff.z * cos
        )

    def increase_y(self, o: float) -> 'Vector':
        """ Returns new vector with changed y value """
        return Vector(self.x, self.y + o, self.z)

    @property
    def magnitude(self):
        """ Vector length """
        return abs(self)

    @property
    def normalized(self):
        """ Returns new vectors with length 1 """
        return self / abs(self)

    @property
    def flat(self):
        """ Returns new vector with undefined Y coord """
        return Vector.vector_xz(self.x, self.z)

    @staticmethod
    def clamp01(x: float) -> float:
        if x > 1:
            return 1
        return 0 if x < 0 else x

    @classmethod
    def lerp(cls, a: 'Vector', b: 'Vector', t: float):
        """ Linearlly interpolates new postion between a and b """
        t = cls.clamp01(t)
        return a * t + b * (1 - t)

    @classmethod
    def from_xml_node(cls, root_node: xml_.XMLNode) -> 'Vector':
        decoder = xml_.XMLDeserializer()
        kwargs = {
            _.name: decoder.deserialize(_, is_container=False)
            for _ in root_node.child
        }
        try:
            return Vector(**kwargs)
        except TypeError:
            raise xml_.IncompatibleError

    def default(self, parent: Optional[xml_.XMLNode]) -> xml_.XMLNode:
        encoder = xml_.XMLSerializer()
        ret_node = xml_.XMLNode(
            xml_.XMLInclude.get_name(Vector),
            parent=parent, **{'xsi:type': xml_.XMLInclude.get_name(Vector)}
        )
        create_node = functools.partial(encoder.serialize, parent=ret_node)
        create_node(self.x, name_override='x')
        create_node(self.y, name_override='y')
        create_node(self.z, name_override='z')
        create_node(self.is_height_defined, name_override='is_height_defined')

        if parent is not None:
            parent.add_child(ret_node)
        return ret_node


@xml_.XMLInclude
class Bezier(xml_.SupportsXML):
    """ Abstract bezier structure """
    def __init__(self,
        a: Vector = Vector.zero,
        b: Vector = Vector.zero,
        c: Vector = Vector.zero,
        d: Vector = Vector.zero
    ):
        """ Creates new bezier from 4 control points """
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    @staticmethod
    def yield_two(o: Iterable[T]) -> Generator[Tuple[T, T], None, None]:
        first, second = None, None
        for _ in o:
            first = second
            second = _
            if first is not None:
                yield (first, second)

    @property
    def controls(self):
        """ Returns control points """
        return [self.a, self.b, self.c, self.d].copy()

    @property
    def reversed(self):
        """ Returns inverted bezier """
        return Bezier(self.d, self.c, self.b, self.a)

    @classmethod
    def lower(cls, controls: List[Vector], t: float) -> List[Vector]:
        return [
            Vector.lerp(x, y, 1 - t)
            for x, y in cls.yield_two(controls)
        ]

    def position(self, t: float) -> Vector:
        """ Returns point on bezier (t is number from 0 to 1) """
        controls = self.controls
        while len(controls) > 1:
            controls = self.lower(controls, 1 - t)
        return controls[0]
        
    def tangent(self, t: float) -> Vector:
        """ Returns tangent vector to the bezier (t is number from 0 to 1) """
        controls = self.controls
        while len(controls) > 2:
            controls = self.lower(controls, 1 - t)
        x, y = controls
        return (y - x).normalized

    def flat_normal(self, t: float) -> Vector:
        """ Returns normal vector to the bezier. Y coord is undefined """
        return self.tangent(t).flat_rotate(math.pi / 2)

    def __str__(self) -> str:
        return f'[{self.a}, {self.b}, {self.c}, {self.d}]'
    
    def __repr__(self) -> str:
        return f'<Bezier[a={self.a}, b={self.b}, c={self.c}, d={self.d}]>'

    def default(self, parent: Optional[xml_.XMLNode]) -> xml_.XMLNode:
        """ For XML Serialization" """
        encoder = xml_.XMLSerializer()
        ret_node = xml_.XMLNode(
            xml_.XMLInclude.get_name(Bezier),
            parent=parent, **{'xsi:type': xml_.XMLInclude.get_name(Bezier)}
        )
        encoder.serialize(self.a, name_override='a', parent=ret_node)
        encoder.serialize(self.b, name_override='b', parent=ret_node)
        encoder.serialize(self.c, name_override='c', parent=ret_node)
        encoder.serialize(self.d, name_override='d', parent=ret_node)

        if parent is not None:
            parent.add_child(ret_node)
        return ret_node

    @classmethod
    def from_xml_node(cls, root_node: xml_.XMLNode) -> 'Bezier':
        """ For XML Deserialization" """
        decoder = xml_.XMLDeserializer()
        kwargs = {
            _.name: decoder.deserialize(_)
            for _ in root_node.child
        }
        try:
            return Bezier(**kwargs)
        except:
            raise xml_.IncompatibleError

@xml_.XMLInclude
class NetOptions(xml_.SupportsXML):
    """ Network options object """

    def __init__(self, prefab_name: str, *,
        follow_terrain: Optional[str | bool] = None, elevation_mode: str = 'default',
        invert: bool = False, node_spacing: int = 100
    ):
        """ Example call: NetOptions(\"Basic Road\", false, \"elevated\", true) """
        if follow_terrain is None:
            follow_terrain = 'false'
        self.follow_terrain = str(follow_terrain)
        if isinstance(follow_terrain, bool):
            self.follow_terrain = self.follow_terrain.lower()
        self.prefab_name = prefab_name
        self.elevation_mode = elevation_mode.lower()
        self.invert = invert
        self.node_spacing = node_spacing

    @classmethod
    def ensure(cls, obj: str |  NetOptions | objects.NetPrefab) -> 'NetOptions':
        if not isinstance(obj, (str, NetOptions, objects.NetPrefab)):
            raise ValueError(
                "Segment type must be prefab name, "
                f"NetPrefab or NetOptions object - not {type(obj)}"
            )
        if isinstance(obj, NetOptions):
            return obj
        if isinstance(obj, str):
            return NetOptions(obj)
        return NetOptions(obj.name)

    def __repr__(self) -> str:
        return f'NetOptions:\n' \
            f'Prefab name: {self.prefab_name}\n' \
            f'Elevation mode: {self.elevation_mode}\n' \
            f'Follow terrain: {self.follow_terrain}\n' \
            f'Invert: {self.invert}\n' \
            f'Node spacing: {self.node_spacing}\n'

    def default(self, parent: Optional[xml_.XMLNode]) -> xml_.XMLNode:
        encoder = xml_.XMLSerializer()
        ret_node = xml_.XMLNode(
            xml_.XMLInclude.get_name(NetOptions),
            parent=parent, **{'xsi:type': xml_.XMLInclude.get_name(NetOptions)}
        )
        create_node = functools.partial(encoder.serialize, parent=ret_node)
        create_node(
            self.follow_terrain, name_override='follow_terrain',
            type_override='xsi:string'
        )
        create_node(self.elevation_mode, name_override='elevation_mode')
        create_node(self.prefab_name, name_override='prefab_name')
        create_node(self.invert, name_override='invert')
        create_node(self.node_spacing, name_override='node_spacing')

        if parent is not None:
            parent.add_child(ret_node)
        return ret_node

    @classmethod
    def from_xml_node(cls, root_node: xml_.XMLNode) -> 'NetOptions':
        decoder = xml_.XMLDeserializer()
        kwargs = {
            _.name: decoder.deserialize(_, is_container=False, type_override=str)
            for _ in root_node.child
        }
        try:
            return NetOptions(**kwargs)
        except TypeError:
            raise xml_.IncompatibleError

@xml_.XMLInclude
class NaturalResourceCellBase(xml_.SupportsXML):

    def __init__(self, *,
        ore: int = 0, oil: int = 0, forest: int = 0, fertility: int = 0,
        pollution: int = 0, water: int = 0
    ):
        self._attrs = {
            'ore': ore,
            'oil': oil,
            'forest': forest,
            'fertility': fertility,
            'pollution': pollution,
            'water': water
        }

    @property
    def ore(self) -> int:
        return self._attrs['ore']

    @property
    def oil(self) -> int:
        return self._attrs['oil']

    @property
    def forest(self) -> int:
        return self._attrs['forest']

    @property
    def fertility(self):
        return self._attrs['fertility']

    @property
    def pollution(self):
        return self._attrs['pollution']
    
    @property
    def water(self):
        return self._attrs['water']

    def default(self, parent: Optional[xml_.XMLNode]) -> xml_.XMLNode:
        encoder = xml_.XMLSerializer()
        ret_node = xml_.XMLNode(
            xml_.XMLInclude.get_name(NaturalResourceCellBase),
            parent=parent, **{
                'xsi:type': xml_.XMLInclude.get_name(NaturalResourceCellBase)
            }
        )
        create_node = functools.partial(encoder.serialize, parent=ret_node)
        for _ in self._attrs:
            create_node(self._attrs[_], name_override=_)

        if parent is not None:
            parent.add_child(ret_node)
        return ret_node


    @classmethod
    def from_xml_node(cls, root_node: xml_.XMLNode) -> 'NaturalResourceCellBase':
        decoder = xml_.XMLDeserializer()
        try:
            kwargs = {
                _.name: decoder.deserialize(_, is_container=False, type_override=int)
                for _ in root_node.child
            }
            return NaturalResourceCellBase(**kwargs)
        except ValueError:
            raise xml_.IncompatibleError
        except TypeError:
            raise xml_.IncompatibleError
