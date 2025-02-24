import math

import numpy as np

from .geo import degree2radian, get_horizontal_distance


class Grid:
    """
    用于处理三维空间网格的工具类

    网格系统将空间划分为经度、纬度和高度三个维度。其中:
    - 经度范围: 43.5° ~ 50.5°, 在48.5°处分为两个区域
        - 左侧区域: 间隔 1/120°
        - 右侧区域: 间隔 1/12° (稀疏区域)
    - 纬度范围: 38.5° ~ 42°, 间隔 1/120°
    - 高度分层: [0, 6, 450, 1000, 3000, 7000, 10000] 米

    示例
    ```python
    # 获取位置对应的网格ID
    grid_id = Grid.get_grid_id(longitude=45.5, latitude=39.5, altitude=1500)

    # 获取网格索引
    indices = Grid.get_index(longitude=45.5, latitude=39.5, altitude=1500)

    # 获取网格中心位置
    position = Grid.get_position(longitude_index=10, latitude_index=20, altitude_index=2)

    # 获取网格尺寸
    dimensions = Grid.get_grid_dimensions(latitude_index=20, longitude_index=10)
    ```
    """

    # 网格系统常量
    DEGREE_UNIT = 1 / 120  # 基础经纬度划分单元
    DEGREE_UNIT_SPARSE = 1 / 12  # 稀疏区域经度划分单元

    # 区域边界
    MIN_LONGITUDE = 43.5
    MAX_LONGITUDE = 50.5
    MIN_LATITUDE = 38.5
    MAX_LATITUDE = 42.0
    MID_LONGITUDE = 48.5  # 经度分区点

    # 高度分层
    ALTITUDE_BANDS = [0, 6, 450, 1000, 3000, 7000, 10000]

    # 预计算常量
    LAT_DEGREE_DISTANCE = 111.1973  # 每纬度对应的距离(km)
    LEFT_LON_COUNT = round((MID_LONGITUDE - MIN_LONGITUDE) / DEGREE_UNIT)
    LON_UNIT_COUNT = LEFT_LON_COUNT + round((MAX_LONGITUDE - MID_LONGITUDE) / DEGREE_UNIT_SPARSE)
    LAT_UNIT_COUNT = round((MAX_LATITUDE - MIN_LATITUDE) / DEGREE_UNIT)

    # 中心点相关常量
    CENTER_LAT_INDEX = LAT_UNIT_COUNT // 2
    CENTER_LON_INDEX = LEFT_LON_COUNT // 2

    @classmethod
    def get_index(cls, longitude: float, latitude: float, altitude: float) -> tuple[int, int, int] | None:
        """获取给定位置对应的网格索引

        Args:
            longitude: 经度
            latitude: 纬度
            altitude: 高度(米)

        Returns:
            包含 (经度索引, 纬度索引, 高度索引) 的元组，如果位置在区域外则返回 None
        """
        lon_idx = cls._get_longitude_index(longitude)
        if lon_idx is None:
            return None
        lat_idx = cls._get_latitude_index(latitude)
        if lat_idx is None:
            return None
        alt_idx = cls._get_altitude_index(altitude)
        if alt_idx is None:
            return None

        return lon_idx, lat_idx, alt_idx

    @classmethod
    def get_position(
        cls, longitude_index: int, latitude_index: int, altitude_index: int
    ) -> tuple[float, float, float] | None:
        """获取网格索引对应的中心位置

        Args:
            longitude_index: 经度索引
            latitude_index: 纬度索引
            altitude_index: 高度索引

        Returns:
            包含 (经度, 纬度, 高度) 的元组，如果索引无效则返回 None
        """
        longitude = cls._get_longitude(longitude_index)
        if longitude is None:
            return None
        latitude = cls._get_latitude(latitude_index)
        if latitude is None:
            return None
        altitude = cls._get_altitude(altitude_index)
        if altitude is None:
            return None

        return longitude, latitude, altitude

    @classmethod
    def get_grid_id(cls, longitude: float, latitude: float, altitude: float) -> int | None:
        """获取位置对应的唯一网格ID

        Args:
            longitude: 经度
            latitude: 纬度
            altitude: 高度(米)

        Returns:
            网格ID，如果位置在区域外则返回 None
        """
        indices = cls.get_index(longitude, latitude, altitude)
        if indices is None:
            return None
        lon_idx, lat_idx, alt_idx = indices
        return alt_idx * 1000000 + lat_idx * 1000 + lon_idx

    @classmethod
    def get_grid_dimensions(cls, latitude_index: int, longitude_index: int) -> tuple[float, float] | None:
        """获取指定网格的尺寸

        Args:
            latitude_index: 纬度索引
            longitude_index: 经度索引

        Returns:
            包含 (纬度长度, 经度宽度) 的元组(单位:km)，如果索引无效则返回 None
        """
        latitude = cls._get_latitude(latitude_index)
        if latitude is None:
            return None

        if longitude_index >= cls.LEFT_LON_COUNT:
            width = cls.LAT_DEGREE_DISTANCE * cls.DEGREE_UNIT_SPARSE * math.cos(degree2radian * latitude)
        else:
            width = cls.LAT_DEGREE_DISTANCE * cls.DEGREE_UNIT * math.cos(degree2radian * latitude)
        return cls.LAT_DEGREE_DISTANCE * cls.DEGREE_UNIT, width

    # 以下是内部辅助方法
    @classmethod
    def _get_longitude_index(cls, longitude: float) -> int | None:
        """获取经度对应的索引"""
        if not cls.MIN_LONGITUDE <= longitude < cls.MAX_LONGITUDE:
            return None

        if longitude < cls.MID_LONGITUDE:
            return math.floor((longitude - cls.MIN_LONGITUDE) / cls.DEGREE_UNIT)
        return cls.LEFT_LON_COUNT + math.floor((longitude - cls.MID_LONGITUDE) / cls.DEGREE_UNIT_SPARSE)

    @classmethod
    def _get_latitude_index(cls, latitude: float) -> int | None:
        """获取纬度对应的索引"""
        if not cls.MIN_LATITUDE <= latitude < cls.MAX_LATITUDE:
            return None
        return math.floor((latitude - cls.MIN_LATITUDE) / cls.DEGREE_UNIT)

    @classmethod
    def _get_altitude_index(cls, altitude: float) -> int:
        """获取高度对应的索引"""
        for i in range(len(cls.ALTITUDE_BANDS) - 1):
            if cls.ALTITUDE_BANDS[i] <= altitude < cls.ALTITUDE_BANDS[i + 1]:
                return i
        return len(cls.ALTITUDE_BANDS) - 1

    @classmethod
    def _get_longitude(cls, longitude_index: int) -> float | None:
        """获取经度索引对应的经度值"""
        if not 0 <= longitude_index < cls.LON_UNIT_COUNT:
            return None

        if longitude_index < cls.LEFT_LON_COUNT:
            return cls.MIN_LONGITUDE + longitude_index * cls.DEGREE_UNIT + cls.DEGREE_UNIT / 2
        return (
            cls.MID_LONGITUDE
            + (longitude_index - cls.LEFT_LON_COUNT) * cls.DEGREE_UNIT_SPARSE
            + cls.DEGREE_UNIT_SPARSE / 2
        )

    @classmethod
    def _get_latitude(cls, latitude_index: int) -> float | None:
        """获取纬度索引对应的纬度值"""
        if not 0 <= latitude_index < cls.LAT_UNIT_COUNT:
            return None
        return cls.MIN_LATITUDE + latitude_index * cls.DEGREE_UNIT + cls.DEGREE_UNIT / 2

    @classmethod
    def _get_altitude(cls, altitude_index: int) -> float | None:
        """获取高度索引对应的高度值"""
        if not 0 <= altitude_index < len(cls.ALTITUDE_BANDS):
            return None
        return cls.ALTITUDE_BANDS[altitude_index]

    @classmethod
    def _get_horizontal_position(cls, latitude_index: int, longitude_index: int) -> tuple[float, float] | None:
        """获取纬度索引和经度索引对应的水平位置"""
        latitude = cls._get_latitude(latitude_index)
        if latitude is None:
            return None
        longitude = cls._get_longitude(longitude_index)
        if longitude is None:
            return None
        return latitude, longitude

    @classmethod
    def get_center_position(cls) -> tuple[float, float] | None:
        """获取网格系统的中心位置"""
        latitude = cls._get_latitude(cls.CENTER_LAT_INDEX)
        if latitude is None:
            return None
        longitude = cls._get_longitude(cls.CENTER_LON_INDEX)
        if longitude is None:
            return None
        return latitude, longitude

    @classmethod
    def get_grids_within_distance(cls, location: tuple[float, float], distance_km: float) -> list[int]:
        """获取指定位置一定距离范围内的所有网格ID

        Args:
            location: (纬度, 经度)的元组
            distance_km: 距离(公里)

        Returns:
            网格ID列表
        """
        grid_array, (min_lat_idx, min_lon_idx) = cls._get_area_within_distance(location, distance_km, True)
        if grid_array is None or min_lat_idx is None or min_lon_idx is None:
            return []

        grid_ids = []
        lat_count, lon_count = grid_array.shape
        for i in range(lat_count):
            grid_indices = np.where(grid_array[i])[0]
            if grid_indices.size > 0:
                for j in grid_indices:
                    grid_id = 1000 * (i + min_lat_idx) + j + min_lon_idx
                    grid_ids.append(grid_id)
        return grid_ids

    @classmethod
    def get_grids_in_rectangle(
        cls, max_latitude: float, min_latitude: float, min_longitude: float, max_longitude: float, altitude: float
    ) -> list[int]:
        """获取给定矩形区域内的所有网格ID

        Args:
            max_latitude: 最大纬度
            min_latitude: 最小纬度
            min_longitude: 最小经度
            max_longitude: 最大经度
            altitude: 高度(米)

        Returns:
            网格ID列表
        """
        grid_ids = set()

        lon = min_longitude
        while lon < max_longitude:
            lat = min_latitude
            while lat < max_latitude:
                grid_id = cls.get_grid_id(lon, lat, altitude)
                if grid_id is not None:
                    grid_ids.add(grid_id)
                lat += cls.DEGREE_UNIT
            lon += cls.DEGREE_UNIT

        return list(grid_ids)

    @classmethod
    def get_all_grids(cls) -> list[int]:
        """获取整个作战区域内的所有网格ID

        Returns:
            网格ID列表
        """
        grid_ids = []
        for altitude in cls.ALTITUDE_BANDS:
            grid_ids.extend(
                cls.get_grids_in_rectangle(
                    cls.MAX_LATITUDE, cls.MIN_LATITUDE, cls.MIN_LONGITUDE, cls.MAX_LONGITUDE, altitude
                )
            )
        return grid_ids

    # 内部缓存
    _area_cache = {}

    @classmethod
    def _get_area_within_distance(
        cls, location: tuple[float, float], distance_km: float, return_subarray: bool = False
    ) -> tuple[np.ndarray | None, tuple[int, int]]:
        """计算指定位置一定距离范围内的网格数组

        Args:
            location: (纬度, 经度)的元组
            distance_km: 距离(公里)
            return_subarray: 是否返回子数组

        Returns:
            (网格数组, (最小纬度索引, 最小经度索引))的元组
        """
        distance = round(distance_km, 1)
        if distance <= 0:
            return None, (0, 0)

        max_half_distance = cls._get_max_half_distance()
        if distance >= max_half_distance:
            return cls._calculate_area_from_distance(location, distance, return_subarray)

        # 使用缓存
        if distance in cls._area_cache:
            area, (min_lat_idx, min_lon_idx) = cls._area_cache[distance]
        else:
            center_pos = cls.get_center_position()
            if center_pos is None:
                return None, (0, 0)
            area, (min_lat_idx, min_lon_idx) = cls._calculate_area_from_distance(center_pos, distance, True)
            cls._area_cache[distance] = (area, (min_lat_idx, min_lon_idx))

        lat_idx = cls._get_latitude_index(location[0])
        lon_idx = cls._get_longitude_index(location[1])
        if area is None or lat_idx is None or lon_idx is None:
            return None, (0, 0)

        # 计算偏移
        lat_delta = lat_idx - cls.CENTER_LAT_INDEX
        lon_delta = lon_idx - cls.CENTER_LON_INDEX
        new_lat_idx = min_lat_idx + lat_delta
        new_lon_idx = min_lon_idx + lon_delta

        # 处理边界情况
        if (
            0 <= new_lat_idx < cls.LAT_UNIT_COUNT - area.shape[0]
            and 0 <= new_lon_idx < cls.LEFT_LON_COUNT - area.shape[1]
        ):
            new_area = area
        else:
            new_area = cls._adjust_area_boundaries(area, new_lat_idx, new_lon_idx)

        if return_subarray:
            return new_area, (new_lat_idx, new_lon_idx)
        else:
            all_area = np.zeros((cls.LAT_UNIT_COUNT, cls.LON_UNIT_COUNT), dtype=np.int8)
            all_area[new_lat_idx : new_lat_idx + new_area.shape[0], new_lon_idx : new_lon_idx + new_area.shape[1]] = (
                new_area
            )
            return all_area, (new_lat_idx, new_lon_idx)

    @classmethod
    def _get_max_half_distance(cls) -> float:
        """计算从中心点到边界的最大距离"""
        center_pos = cls.get_center_position()
        if center_pos is None:
            return 0
        latitude = cls._get_latitude(0)
        if latitude is None:
            return 0
        longitude = cls._get_longitude(cls.CENTER_LON_INDEX)
        if longitude is None:
            return 0
        edge_pos = (latitude, longitude)

        return get_horizontal_distance(center_pos, edge_pos)

    @classmethod
    def _adjust_area_boundaries(cls, area: np.ndarray, new_lat_idx: int, new_lon_idx: int) -> np.ndarray:
        """调整区域边界以适应网格范围"""
        if new_lat_idx < 0:
            left_lat_idx = 0 - new_lat_idx
            end_lat_idx = area.shape[0]
            new_lat_idx = 0
        elif new_lat_idx + area.shape[0] >= cls.LAT_UNIT_COUNT:
            left_lat_idx = 0
            end_lat_idx = area.shape[0] - (new_lat_idx + area.shape[0] - cls.LAT_UNIT_COUNT)
        else:
            left_lat_idx = 0
            end_lat_idx = area.shape[0]

        if new_lon_idx < 0:
            left_lon_idx = 0 - new_lon_idx
            end_lon_idx = area.shape[1]
            new_lon_idx = 0
        elif new_lon_idx + area.shape[1] >= cls.LEFT_LON_COUNT:
            left_lon_idx = 0
            end_lon_idx = area.shape[1] - (new_lon_idx + area.shape[1] - cls.LEFT_LON_COUNT)
        else:
            left_lon_idx = 0
            end_lon_idx = area.shape[1]

        return area[left_lat_idx:end_lat_idx, left_lon_idx:end_lon_idx]

    @classmethod
    def _calculate_area_from_distance(
        cls, location: tuple[float, float], distance_km: float, return_subarray: bool = False
    ) -> tuple[np.ndarray | None, tuple[int, int]]:
        """计算指定位置和距离范围内的网格数组

        Args:
            location: (纬度, 经度)的元组
            distance_km: 距离(公里)
            return_subarray: 是否返回子数组

        Returns:
            (网格数组, (最小纬度索引, 最小经度索引))的元组
        """
        air_lat_index = cls._get_latitude_index(location[0])
        air_lon_index = cls._get_longitude_index(location[1])
        if air_lat_index is None or air_lon_index is None:
            return None, (0, 0)

        # 计算经度方向上的距离
        lon_degree_dis = cls.LAT_DEGREE_DISTANCE * math.cos(location[0] * degree2radian)

        # 计算边界经纬度
        min_lon = max(cls.MIN_LONGITUDE, location[1] - distance_km / lon_degree_dis)
        max_lon = min(cls.MAX_LONGITUDE - 1e-4, location[1] + distance_km / lon_degree_dis)
        min_lat = max(cls.MIN_LATITUDE, location[0] - distance_km / cls.LAT_DEGREE_DISTANCE)
        max_lat = min(cls.MAX_LATITUDE - 1e-4, location[0] + distance_km / cls.LAT_DEGREE_DISTANCE)

        # 获取边界索引
        min_lat_index = cls._get_latitude_index(min_lat)
        max_lat_index = cls._get_latitude_index(max_lat)
        min_lon_index = cls._get_longitude_index(min_lon)
        max_lon_index = cls._get_longitude_index(max_lon)
        if min_lat_index is None or max_lat_index is None or min_lon_index is None or max_lon_index is None:
            return None, (0, 0)

        lat_valid_count = max_lat_index - min_lat_index + 1
        lon_valid_count = max_lon_index - min_lon_index + 1
        in_area = np.zeros((lat_valid_count, lon_valid_count), dtype=np.int8)
        max_axis_unit_count = max(lat_valid_count, lon_valid_count)

        # 小范围处理
        if max_axis_unit_count < 11:
            lon_degree_unit_dis = lon_degree_dis * cls.DEGREE_UNIT
            delta_lat = math.floor(distance_km / (cls.LAT_DEGREE_DISTANCE * cls.DEGREE_UNIT) / math.sqrt(2)) - 1
            delta_lon = math.floor(distance_km / lon_degree_unit_dis / math.sqrt(2)) - 1

            valid_min_lat = max(air_lat_index - delta_lat, min_lat_index) - min_lat_index
            valid_min_lon = max(air_lon_index - delta_lon, min_lon_index) - min_lon_index
            valid_max_lat = min(air_lat_index + delta_lat, max_lat_index) - min_lat_index + 1
            valid_max_lon = min(air_lon_index + delta_lon, max_lon_index) - min_lon_index + 1

            in_area[valid_min_lat:valid_max_lat, valid_min_lon:valid_max_lon] = 1

            for lat_index in range(min_lat_index, max_lat_index + 1):
                for lon_index in range(min_lon_index, max_lon_index + 1):
                    if not (
                        air_lat_index - delta_lat <= lat_index <= air_lat_index + delta_lat
                        and air_lon_index - delta_lon <= lon_index <= air_lon_index + delta_lon
                    ):
                        horizontal_position = cls._get_horizontal_position(lat_index, lon_index)
                        if horizontal_position is None:
                            continue
                        h_dis = get_horizontal_distance(location, horizontal_position)
                        if h_dis < distance_km:
                            in_area[lat_index - min_lat_index][lon_index - min_lon_index] = 1

        # 中等范围处理
        elif max_axis_unit_count < 56:
            lon_grid_len_up = math.cos((location[0] + 1 / 60) * degree2radian) * (
                cls.LAT_DEGREE_DISTANCE * cls.DEGREE_UNIT
            )
            lon_grid_len_down = math.cos((location[0] - 1 / 60) * degree2radian) * (
                cls.LAT_DEGREE_DISTANCE * cls.DEGREE_UNIT
            )
            lon_grid_len_up *= lon_grid_len_up
            lon_grid_len_down *= lon_grid_len_down

            lon_all_count = math.floor(distance_km / lon_degree_dis / cls.DEGREE_UNIT)
            air_lat_index_array = air_lat_index - min_lat_index
            air_lon_index_array = air_lon_index - min_lon_index

            for i in range(1, lon_all_count):
                lon_delta = i - 1
                lat_count_up = (
                    math.floor(
                        math.sqrt(distance_km * distance_km - i * i * lon_grid_len_up)
                        / (cls.LAT_DEGREE_DISTANCE * cls.DEGREE_UNIT)
                    )
                    - 1
                )
                lat_count_down = (
                    math.floor(
                        math.sqrt(distance_km * distance_km - i * i * lon_grid_len_down)
                        / (cls.LAT_DEGREE_DISTANCE * cls.DEGREE_UNIT)
                    )
                    - 1
                )

                r1 = max(0, air_lat_index_array - lat_count_down)
                r2 = min(lat_valid_count, air_lat_index_array + lat_count_up + 1)
                c1 = max(0, air_lon_index_array - lon_delta)
                c2 = min(lon_valid_count, air_lon_index_array + lon_delta + 1)
                in_area[r1:r2, c1:c2] = 1

            # 检查剩余格子
            for lat_index in range(min_lat_index, max_lat_index + 1):
                have_in = False
                for lon_index in range(min_lon_index, max_lon_index + 1):
                    if in_area[lat_index - min_lat_index][lon_index - min_lon_index] != 1:
                        horizontal_position = cls._get_horizontal_position(lat_index, lon_index)
                        if horizontal_position is None:
                            continue
                        h_dis = get_horizontal_distance(location, horizontal_position)
                        if h_dis < distance_km:
                            have_in = True
                            in_area[lat_index - min_lat_index][lon_index - min_lon_index] = 1
                        elif have_in:
                            break

        # 大范围处理
        else:
            lon_grid_len_up = math.cos((location[0] + 1 / 60) * degree2radian) * (
                cls.LAT_DEGREE_DISTANCE * cls.DEGREE_UNIT
            )
            lon_grid_len_down = math.cos((location[0] - 1 / 60) * degree2radian) * (
                cls.LAT_DEGREE_DISTANCE * cls.DEGREE_UNIT
            )
            lon_grid_len_up *= lon_grid_len_up
            lon_grid_len_down *= lon_grid_len_down

            lon_all_count = math.floor(distance_km / lon_degree_dis / cls.DEGREE_UNIT)
            air_lat_index_array = air_lat_index - min_lat_index
            air_lon_index_array = air_lon_index - min_lon_index

            for i in range(1, lon_all_count):
                lon_delta = i - 1
                lat_count_up = (
                    math.floor(
                        math.sqrt(distance_km * distance_km - i * i * lon_grid_len_up)
                        / (cls.LAT_DEGREE_DISTANCE * cls.DEGREE_UNIT)
                    )
                    - 1
                )
                lat_count_down = (
                    math.floor(
                        math.sqrt(distance_km * distance_km - i * i * lon_grid_len_down)
                        / (cls.LAT_DEGREE_DISTANCE * cls.DEGREE_UNIT)
                    )
                    - 1
                )

                r1 = max(0, air_lat_index_array - lat_count_down)
                r2 = min(lat_valid_count, air_lat_index_array + lat_count_up + 1)
                c1 = max(0, air_lon_index_array - lon_delta)
                c2 = min(lon_valid_count, air_lon_index_array + lon_delta + 1)
                in_area[r1:r2, c1:c2] = 1

            # 检查边界行
            for r in [0, 1, 3, lat_valid_count - 3, lat_valid_count - 2, lat_valid_count - 1]:
                horizontal_position = cls._get_horizontal_position(r + min_lat_index, air_lon_index)
                if horizontal_position is None:
                    continue
                h_dis = get_horizontal_distance(location, horizontal_position)
                if h_dis < distance_km:
                    in_area[r][air_lon_index_array] = 1

            # 优化检查范围
            for r in range(lat_valid_count):
                one_array = np.where(in_area[r])[0]
                if one_array.size > 0:
                    if r == 0:
                        check_more_count = 10
                    elif r < 5:
                        check_more_count = 20
                    elif r < 13:
                        check_more_count = 8
                    elif r < 20 or lat_valid_count - r < 15:
                        check_more_count = 5
                    else:
                        check_more_count = 3

                    left_check = max(0, one_array[0] - check_more_count)
                    right_check = min(lon_valid_count, one_array[-1] + check_more_count)

                    # 检查左侧
                    for i in range(left_check, one_array[0]):
                        horizontal_position = cls._get_horizontal_position(r + min_lat_index, i + min_lon_index)
                        if horizontal_position is None:
                            continue
                        h_dis = get_horizontal_distance(location, horizontal_position)
                        if h_dis < distance_km:
                            in_area[r][i] = 1

                    # 检查右侧
                    for i in range(one_array[-1] + 1, right_check):
                        horizontal_position = cls._get_horizontal_position(r + min_lat_index, i + min_lon_index)
                        if horizontal_position is None:
                            continue
                        h_dis = get_horizontal_distance(location, horizontal_position)
                        if h_dis < distance_km:
                            in_area[r][i] = 1

        if return_subarray:
            return in_area, (min_lat_index, min_lon_index)
        else:
            all_area = np.zeros((cls.LAT_UNIT_COUNT, cls.LON_UNIT_COUNT), dtype=np.int8)
            all_area[min_lat_index : max_lat_index + 1, min_lon_index : max_lon_index + 1] = in_area
            return all_area, (min_lat_index, min_lon_index)
